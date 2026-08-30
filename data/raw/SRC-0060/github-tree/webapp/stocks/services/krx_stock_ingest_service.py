"""
KRX 주식 정보 수집 서비스

KRX API를 통해 주식 정보를 수집하고 Stock 모델을 업데이트합니다.
이 서비스는 DART Company Ingest가 먼저 실행된 후 사용됩니다.
"""

from __future__ import annotations

import logging
import re
import time
from datetime import datetime
from typing import Callable, Dict, Iterable, List, Optional

from django.conf import settings
from django.db import transaction

from pydantic import BaseModel
from stocks.choices import StockCategoryChoice
from stocks.models import DelistedStock, Market, Stock

from common.clients.krx import CompanyInfoKRXClient, StockInfoKRXClient
from companies.models import Company

logger = logging.getLogger(__name__)

KRX_DEFAULT_MARKETS = settings.KRX_DEFAULT_MARKETS
KRX_SLEEP = settings.KRX_SLEEP

# SPAC 필터링 패턴
SPAC_SUFFIX_PATTERN = re.compile(r"(제\d+호스팩|스팩\d+호|[가-힣]+\d+호스팩|[가-힣]+비전스팩\d+호)$", re.IGNORECASE)

MARKET_MAPPING = {
  "KOSPI": "STK",
  "STK": "STK",
  "KOSDAQ": "KSQ",
  "KSQ": "KSQ",
}


class KrxStockEntry(BaseModel):
  """KRX 주식 정보 데이터 모델"""

  stock_code: str
  corp_name: str
  market: str

  def is_common_stock(self) -> bool:
    """보통주인지 확인 (종목 코드가 0으로 끝남)"""
    return self.stock_code.endswith("0")

  def get_base_stock_code(self) -> str:
    """우선주/기타 주식의 보통주 코드 반환 (마지막 자리를 0으로 변경)"""
    return self.stock_code[:-1] + "0"

  def is_preferred_stock(self) -> bool:
    """우선주인지 확인

    우선주 패턴 예시:
    - 대신증권2우B (숫자 + 우 + 알파벳)
    - 아모레퍼시픽홀딩스3우C (숫자 + 우 + 알파벳)
    - 진흥기업우B (우 + 알파벳)
    - CJ4우(전환) (숫자 + 우 + (전환))
    - 삼성전자우 (우로 끝남)

    주의사항:
    - 보통주(종목코드가 0으로 끝남)는 절대 우선주가 아님
    - "대우"처럼 회사명이 "우"로 끝나지만 보통주인 경우 제외

    Returns:
      bool: 우선주 여부
    """
    # 보통주는 절대 우선주가 아님
    if self.is_common_stock():
      return False

    # 우선주 패턴: 숫자(선택) + "우" + (알파벳/괄호/끝)
    preferred_pattern = re.compile(r'\d*우([A-Z]|\(|$)')
    return bool(preferred_pattern.search(self.corp_name))


def _upsert_stock(
  entry: KrxStockEntry,
  company: Company,
  market: Market,
  is_primary: bool = False,
  stock_info: Optional[Dict] = None,
) -> tuple[Stock, bool]:
  """Stock 생성 또는 업데이트"""

  # 주식 종류 판단 (보통주 먼저 확인)
  if entry.is_common_stock():
    category = StockCategoryChoice.COMMON
  elif entry.is_preferred_stock():
    category = StockCategoryChoice.PREFERRED
  else:
    category = StockCategoryChoice.OTHER

  defaults = {
    "company": company,
    "market": market,
    "name": entry.corp_name,
    "category": category,
    "is_primary": is_primary,
    "is_listed": True,
  }

  # Stock info 데이터가 있으면 추가 필드 업데이트
  if stock_info:
    # LIST_DD: 상장일 (YYYY/MM/DD 형식)
    if list_dd := stock_info.get("LIST_DD"):
      try:
        defaults["listed_date"] = datetime.strptime(list_dd, "%Y/%m/%d").date()
      except ValueError:
        logger.warning(f"상장일 파싱 실패: {list_dd}")

  # DelistedStock 조회하여 상장 폐지 여부 확인
  delisted_stock = DelistedStock.objects.filter(isu_cd=entry.stock_code).first()
  if delisted_stock:
    # 상장 폐지된 경우
    defaults["is_listed"] = False
    defaults["delisted_date"] = delisted_stock.delist_dd
    logger.debug(f"상장 폐지 데이터 발견: {entry.stock_code} - "
                 f"폐지일: {delisted_stock.delist_dd}")

  stock, created = Stock.objects.get_or_create(
    code=entry.stock_code,
    defaults=defaults,
  )

  if not created:
    # 기존 Stock 업데이트
    updated_fields = []
    for field, value in defaults.items():
      if getattr(stock, field) != value:
        setattr(stock, field, value)
        updated_fields.append(field)

    if updated_fields:
      updated_fields.append("updated_at")
      stock.save(update_fields=updated_fields)

  return stock, created


class KrxStockIngestService:
  """KRX 주식 정보 수집 서비스

  KRX API를 통해 주식 정보를 수집하고 Stock 모델을 업데이트합니다.
  이 서비스는 DART Company Ingest가 먼저 실행된 후 사용됩니다.
  """

  def __init__(
    self,
    markets: Optional[Iterable[str]] = None,
    krx_client: Optional[CompanyInfoKRXClient] = None,
    stock_info_client: Optional[StockInfoKRXClient] = None,
  ):
    """초기화

    Args:
      markets: 조회할 시장 목록 (None이면 설정에서 가져옴)
      krx_client: CompanyInfoKRXClient 인스턴스 (None이면 새로 생성)
      stock_info_client: StockInfoKRXClient 인스턴스 (None이면 새로 생성)
    """
    self.markets = list(markets) if markets is not None else list(KRX_DEFAULT_MARKETS)
    self.krx_client = krx_client or CompanyInfoKRXClient()
    self.stock_info_client = stock_info_client or StockInfoKRXClient()

    self._listing_filters: List[Callable[[Dict[str, str]], bool]] = [
      self._exclude_spac_suffix,
    ]

  def perform(self, trade_date: Optional[str] = None) -> dict:
    """KRX 주식 정보 수집 및 업데이트

    Args:
      trade_date: 거래일 (YYYYMMDD 형식, None이면 현재일)

    Returns:
      dict: 수집 결과
        - stock_created: 생성된 주식 수
        - stock_updated: 업데이트된 주식 수
        - total_entries: 처리한 항목 수
    """
    logger.info("KRX 주식 정보 수집 시작")

    trade_date = trade_date or datetime.now().strftime("%Y%m%d")

    # KRX에서 주식 데이터 수집
    stock_entries = self.fetch_krx_stock_entries(trade_date=trade_date)
    stock_info_map = self.fetch_stock_info(market_id="ALL")

    stock_created = 0
    stock_updated = 0

    # Market 이름 -> 객체 매핑 캐시
    market_cache: Dict[str, Market] = {}

    # primary_stock_code -> Company 매핑 생성 (DB에서 조회)
    stock_codes = [entry.stock_code for entry in stock_entries]
    companies = Company.objects.filter(primary_stock_code__in=stock_codes)
    primary_stock_code_to_company: Dict[str, Company] = {
      company.primary_stock_code: company
      for company in companies if company.primary_stock_code
    }

    # 보통주와 비보통주 분리
    common_stocks: List[KrxStockEntry] = []
    non_common_stocks: List[KrxStockEntry] = []

    for entry in stock_entries:
      if entry.market not in self.markets:
        logger.debug(f"시장 필터링으로 제외: {entry.corp_name} ({entry.stock_code}), 시장: {entry.market}")
        continue

      if entry.is_common_stock():
        common_stocks.append(entry)
      else:
        non_common_stocks.append(entry)

    # 보통주 코드 -> Company 매핑 (우선주/기타 주식 처리용)
    base_code_to_company: Dict[str, Company] = {}

    with transaction.atomic():
      # 1단계: 보통주 처리
      for entry in common_stocks:
        try:
          # primary_stock_code로 Company 조회
          company = primary_stock_code_to_company.get(entry.stock_code)
          if not company:
            logger.warning(f"Company를 찾을 수 없음: {entry.corp_name} ({entry.stock_code})")
            continue

          # Market 조회 (캐싱)
          if entry.market not in market_cache:
            market_cache[entry.market] = Market.objects.get(code=entry.market)
          market = market_cache[entry.market]

          # Stock info 조회
          stock_info = stock_info_map.get(entry.stock_code)

          # Stock 생성/업데이트 (is_primary=True)
          _, created = _upsert_stock(entry, company, market, is_primary=True, stock_info=stock_info)
          if created:
            stock_created += 1
          else:
            stock_updated += 1

          # 보통주 매핑 저장
          base_code_to_company[entry.stock_code] = company

        except Exception as e:
          logger.error(f"보통주 처리 실패 ({entry.stock_code}): {e}")
          continue

      # 2단계: 우선주/기타 주식 처리
      for entry in non_common_stocks:
        try:
          # 보통주 코드로 Company 찾기
          base_code = entry.get_base_stock_code()
          company = base_code_to_company.get(base_code)

          if not company:
            # 보통주를 찾지 못한 경우 DB에서 직접 검색
            base_stock = Stock.objects.filter(code=base_code).select_related("company").first()
            if base_stock:
              company = base_stock.company
            else:
              logger.error(f"보통주를 찾을 수 없음: {entry.stock_code} (base: {base_code})")
              continue

          # Market 조회 (캐싱)
          if entry.market not in market_cache:
            market_cache[entry.market] = Market.objects.get(code=entry.market)
          market = market_cache[entry.market]

          # Stock info 조회
          stock_info = stock_info_map.get(entry.stock_code)

          # Stock 생성/업데이트 (is_primary=False)
          _, created = _upsert_stock(entry, company, market, is_primary=False, stock_info=stock_info)
          if created:
            stock_created += 1
          else:
            stock_updated += 1

        except Exception as e:
          logger.error(f"우선주/기타 처리 실패 ({entry.stock_code}): {e}")
          continue

    logger.info(
      f"KRX 주식 정보 수집 완료 - "
      f"주식 생성: {stock_created}, "
      f"주식 업데이트: {stock_updated}, "
      f"전체: {len(stock_entries)}"
    )

    return {
      "stock_created": stock_created,
      "stock_updated": stock_updated,
      "total_entries": len(stock_entries),
    }

  def fetch_krx_stock_entries(self, trade_date: Optional[str] = None) -> List[KrxStockEntry]:
    """KRX API를 통해 주식 정보 조회

    Args:
      trade_date: 거래일 (YYYYMMDD 형식, None이면 현재일)

    Returns:
      List[KrxStockEntry]: KRX 주식 정보 리스트
    """
    logger.info("KRX 주식 정보 조회 시작")

    listings: List[Dict[str, str]] = []

    # KRX에서 시장별 상장 주식 목록 조회
    for market_id in self.markets:
      try:
        market_listings = self.krx_client.fetch_company_list(market_id, trade_date)
        # 필터링 적용 (SPAC 제외)
        filtered_listings = [listing for listing in market_listings if not self._should_filter_listing(listing)]

        listings.extend(filtered_listings)
        logger.info(f"KRX {market_id} 조회 완료: {len(filtered_listings)}개")

        time.sleep(KRX_SLEEP)

      except Exception as e:
        logger.error(f"KRX {market_id} 조회 실패: {e}")
        continue

    # 종목 코드별로 통합 (중복 제거)
    consolidated: Dict[str, Dict[str, str]] = {}
    for listing in listings:
      stock_code = listing["stock_code"]
      if stock_code not in consolidated:
        consolidated[stock_code] = listing

    # KrxStockEntry 객체 생성
    entries: List[KrxStockEntry] = []
    for stock_code, listing in consolidated.items():
      entry = KrxStockEntry(
        stock_code=stock_code,
        corp_name=listing["corp_name"],
        market=MARKET_MAPPING[listing["market"]],
      )
      entries.append(entry)

    logger.info(f"KRX 주식 정보 수집 완료: {len(entries)}개")
    return entries

  def fetch_stock_info(self, market_id: str = "ALL") -> Dict[str, Dict]:
    """전체 주식 상세 정보 조회

    Args:
      market_id: 시장 구분 (ALL, STK, KSQ, KNX)

    Returns:
      Dict[str, Dict]: ISU_SRT_CD를 키로 하는 주식 정보 딕셔너리
        - ISU_CD: 종목코드 (12자리 표준코드)
        - ISU_SRT_CD: 단축코드 (6자리)
        - ISU_NM: 종목명
        - ISU_ABBRV: 종목명 약어
        - ISU_ENG_NM: 영문 종목명
        - LIST_DD: 상장일
        - MKT_TP_NM: 시장구분명
        - SECUGRP_NM: 증권그룹명
        - SECT_TP_NM: 업종명
        - KIND_STKCERT_TP_NM: 주식종류명
        - PARVAL: 액면가
        - LIST_SHRS: 상장주식수
    """
    stock_info_list = self.stock_info_client.fetch_stock_info(market_id)

    # ISU_SRT_CD를 키로 하는 딕셔너리로 변환
    stock_info_map = {}
    for info in stock_info_list:
      isu_srt_cd = info.get("ISU_SRT_CD")
      if isu_srt_cd:
        stock_info_map[isu_srt_cd] = info

    logger.info(f"주식 상세 정보 수집 완료: {len(stock_info_map)}개")
    return stock_info_map

  def _should_filter_listing(self, listing: Dict[str, str]) -> bool:
    """필터링 여부 확인

    Args:
      listing: 상장 정보

    Returns:
      bool: 필터링 여부
    """
    return any(filter_fn(listing) for filter_fn in self._listing_filters)

  @staticmethod
  def _exclude_spac_suffix(listing: Dict[str, str]) -> bool:
    """SPAC 제외 필터

    Args:
      listing: 상장 정보

    Returns:
      bool: SPAC 여부
    """
    corp_name = listing.get("corp_name", "")
    return bool(SPAC_SUFFIX_PATTERN.search(corp_name))

  def close(self):
    """리소스 정리"""
    self.krx_client.close()
    self.stock_info_client.close()

  def __enter__(self):
    """Context manager 진입"""
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    """Context manager 종료"""
    self.close()
