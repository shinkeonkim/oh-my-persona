from __future__ import annotations

import logging
import re
import warnings
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Callable, Dict, List, Optional
from zipfile import BadZipFile, ZipFile

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import requests
from bs4 import BeautifulSoup, FeatureNotFound, XMLParsedAsHTMLWarning
from disclosures.models import CompanyDisclosure

from companies.models import Company

logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

DART_API_BASE = "https://opendart.fss.or.kr/api"
DISCLOSURE_MAX_LENGTH = 10000
ALLOWED_DISCLOSURE_TITLE_KEYWORDS: List[str] = [
  "사업 보고서",
  "사업보고서",
  "분기 보고서",
  "분기보고서",
  "반기 보고서",
  "반기보고서",
  "정정"
  "현금ㆍ현물배당결정",
]


@dataclass
class DisclosureMetadata:
  receipt_no: str
  title: str
  published_at: str
  disclosure_type: str


class CompanyDisclosureService:

  def __init__(self, session: Optional[requests.Session] = None) -> None:
    self.session = session or requests.Session()
    self.api_key = settings.DART_API_KEY
    if not self.api_key:
      raise ValueError(_("DART API key is not configured."))
    self._disclosure_filters: List[Callable[[DisclosureMetadata], bool]] = [
      self._allow_only_whitelisted_titles,
    ]

  def perform(
    self,
    company: Company,
    begin_date: str,
    end_date: str,
    page_count: int = 100,
    refresh_existing: bool = False,
    corp_code: Optional[str] = None,
  ) -> Dict[str, int]:
    # market_code 초기화
    market_code = None

    # corp_code가 전달되지 않으면 primary stock에서 가져오기 (Stock에 저장되어 있다고 가정)
    # 또는 company에서 직접 가져오기
    if not corp_code:
      # Company에 corp_code 필드가 있다면
      corp_code = getattr(company, 'corp_code', None)

    # primary stock에서 market_code 가져오기 (corp_code 존재 여부와 무관하게 필요)
    primary_stock = company.stocks.filter(is_primary=True).first()
    if not primary_stock:
      primary_stock = company.stocks.first()

    if primary_stock:
      if not corp_code:
        # Stock에 corp_code가 있다면 가져오기 시도
        corp_code = getattr(primary_stock, 'corp_code', None)
      market_code = primary_stock.market.code if primary_stock.market else None
    else:
      logger.warning("No stocks found for company %s; cannot determine market info", company.id)
      if not corp_code:
        return {"created": 0, "updated": 0, "skipped": 0}

    if not corp_code:
      logger.warning("corp_code not found for company %s; skipping disclosure ingest", company.id)
      return {"created": 0, "updated": 0, "skipped": 0}

    corp_cls = self._determine_corp_cls(market_code)

    logger.info(
      "Starting disclosure ingest for company_id=%s corp_code=%s corp_cls=%s window=%s-%s refresh=%s page_count=%s",
      company.id,
      corp_code,
      corp_cls or "ALL",
      begin_date,
      end_date,
      refresh_existing,
      page_count,
    )

    disclosures = self._list_disclosures(
      corp_code=corp_code,
      begin_date=begin_date,
      end_date=end_date,
      page_count=page_count,
      corp_cls=corp_cls,
    )

    created = 0
    updated = 0
    skipped = 0

    for disclosure in disclosures:
      if not refresh_existing and CompanyDisclosure.objects.filter(company=company,
                                                                   receipt_no=disclosure.receipt_no).exists():
        logger.debug(
          "Skipping disclosure %s for company %s (already exists)",
          disclosure.receipt_no,
          company.id,
        )
        skipped += 1
        continue

      try:
        text_body, html_body = self._fetch_disclosure_content(disclosure.receipt_no)
      except requests.RequestException as exc:
        logger.warning(
          "Failed to download disclosure %s for company %s: %s",
          disclosure.receipt_no,
          company.id,
          exc,
        )
        continue
      if text_body is None and html_body is None:
        logger.warning(
          "Skipping disclosure %s for company %s due to unreadable document archive",
          disclosure.receipt_no,
          company.id,
        )
        continue

      published_at = self._parse_published_at(disclosure.published_at)

      defaults = {
        "title": disclosure.title,
        "published_at": published_at,
        "text_body": text_body or "",
        "html_body": html_body or "",
        "disclosure_type": disclosure.disclosure_type,
        "source_url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={disclosure.receipt_no}",
      }

      obj, was_created = CompanyDisclosure.objects.update_or_create(
        company=company,
        receipt_no=disclosure.receipt_no,
        defaults=defaults,
      )

      if was_created:
        created += 1
        logger.debug("Created disclosure %s for company %s", obj.receipt_no, company.id)
      else:
        updated += 1
        logger.debug("Updated disclosure %s for company %s", obj.receipt_no, company.id)

    logger.info(
      "Finished disclosure ingest for company_id=%s: created=%s updated=%s skipped=%s",
      company.id,
      created,
      updated,
      skipped,
    )
    return {"created": created, "updated": updated, "skipped": skipped}

  def _list_disclosures(
    self,
    corp_code: str,
    begin_date: str,
    end_date: str,
    page_count: int = 100,
    corp_cls: Optional[str] = None,
  ) -> List[DisclosureMetadata]:
    params = {
      "crtfc_key": self.api_key,
      "corp_code": corp_code,
      "bgn_de": begin_date,
      "end_de": end_date,
      "page_no": 1,
      "page_count": page_count,
      "sort": "date",
      "sort_mth": "desc",
    }
    if corp_cls:
      params["corp_cls"] = corp_cls

    collected: List[DisclosureMetadata] = []
    while True:
      logger.debug(
        "Requesting DART disclosures for corp_code=%s page=%s window=%s-%s corp_cls=%s",
        corp_code,
        params["page_no"],
        begin_date,
        end_date,
        corp_cls or "ALL",
      )
      response = self.session.get(f"{DART_API_BASE}/list.json", params=params, timeout=30)
      response.raise_for_status()
      payload = response.json()

      status = payload.get("status")
      if status != "000":
        logger.warning(
          "DART list.json returned status %s for corp_code=%s: %s",
          status,
          corp_code,
          payload.get("message"),
        )
        break

      logger.debug(
        "DART list.json returned %s disclosures on page %s of %s for corp_code=%s",
        len(payload.get("list", [])),
        params["page_no"],
        payload.get("total_page", 1),
        corp_code,
      )

      for entry in payload.get("list", []):
        metadata = DisclosureMetadata(
          receipt_no=entry.get("rcept_no", "").strip(),
          title=(entry.get("report_nm") or "").strip(),
          published_at=(entry.get("rcept_dt") or "").strip(),
          disclosure_type=(entry.get("rpt_nm") or entry.get("report_nm") or "").strip(),
        )
        if metadata.receipt_no and self._passes_disclosure_filters(metadata):
          collected.append(metadata)

      total_page = int(payload.get("total_page", 1))
      if params["page_no"] >= total_page:
        break
      params["page_no"] += 1

    logger.info(
      "Fetched %d disclosures for corp_code=%s between %s and %s",
      len(collected),
      corp_code,
      begin_date,
      end_date,
    )
    return collected

  def _fetch_disclosure_content(self, receipt_no: str) -> tuple[Optional[str], Optional[str]]:
    """공시 내용을 text와 html 형식으로 모두 반환

    Returns:
      tuple[Optional[str], Optional[str]]: (text_body, html_body)
    """
    params = {"crtfc_key": self.api_key, "rcept_no": receipt_no}
    response = self.session.get(f"{DART_API_BASE}/document.xml", params=params, timeout=60)
    response.raise_for_status()
    logger.debug("Downloaded document archive for receipt_no=%s (size=%s bytes)", receipt_no, len(response.content))

    try:
      with ZipFile(BytesIO(response.content)) as archive:
        candidates = [name for name in archive.namelist() if name.lower().endswith((".html", ".htm", ".xml"))]
        if not candidates:
          raise FileNotFoundError(f"No readable document found in archive for {receipt_no}")

        target_name = max(candidates, key=lambda name: archive.getinfo(name).file_size)
        raw_content = archive.read(target_name).decode("utf-8", errors="ignore")
        logger.debug(
          "Extracted %s from archive for receipt_no=%s (size=%s bytes)",
          target_name,
          receipt_no,
          len(raw_content),
        )
    except BadZipFile:
      logger.warning("DART returned non-zip payload for receipt_no=%s; skipping.", receipt_no)
      return None, None

    # HTML body 저장 (원본)
    html_body = raw_content

    # Text body 생성 (HTML에서 텍스트 추출)
    text_body = self._sanitize_html(raw_content)
    if len(text_body) > DISCLOSURE_MAX_LENGTH:
      logger.debug(
        "Disclosure text for receipt_no=%s exceeds max length (%s); truncating.",
        receipt_no,
        DISCLOSURE_MAX_LENGTH,
      )
      text_body = text_body[:DISCLOSURE_MAX_LENGTH] + "...(truncated)"

    return text_body, html_body

  @staticmethod
  def _sanitize_html(raw_content: str) -> str:
    try:
      soup = BeautifulSoup(raw_content, "lxml")
    except FeatureNotFound:
      soup = BeautifulSoup(raw_content, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

  @staticmethod
  def _parse_published_at(value: str) -> datetime:
    if not value:
      return timezone.now()
    naive = datetime.strptime(value, "%Y%m%d")
    return timezone.make_aware(naive, timezone=timezone.get_current_timezone())

  @staticmethod
  def _determine_corp_cls(market_code: Optional[str]) -> Optional[str]:
    """시장 코드를 DART API의 corp_cls 파라미터로 변환

    Args:
      market_code: Market 모델의 code 필드 값 (예: "STK", "KSQ")

    Returns:
      DART API의 corp_cls 파라미터 값 (Y, K, N, E 등)
    """
    if not market_code:
      return None

    normalized = market_code.strip().upper()
    mapping = {
      "STK": "Y",  # KOSPI
      "KOSPI": "Y",
      "KSQ": "K",  # KOSDAQ
      "KOSDAQ": "K",
      "KNX": "N",  # KONEX
      "KONEX": "N",
      "K-OTC": "E",
      "OTC": "E",
    }
    return mapping.get(normalized)

  def _passes_disclosure_filters(self, disclosure: DisclosureMetadata) -> bool:
    return all(filter_fn(disclosure) for filter_fn in self._disclosure_filters)

  @staticmethod
  def _allow_only_whitelisted_titles(disclosure: DisclosureMetadata) -> bool:
    title = disclosure.title or ""
    return any(keyword in title for keyword in ALLOWED_DISCLOSURE_TITLE_KEYWORDS)
