"""
DART 회사 정보 수집 서비스

OpenDart API를 통해 회사 정보를 수집하고 Company 모델을 업데이트합니다.
- DART: corp_code, english_name, primary_stock_code 수집
"""

from __future__ import annotations

import logging
import re
from typing import Dict, List, Optional

from django.db import transaction

from common.clients.dart import CorpCodeDartClient
from common.clients.krx import CompanyInfoKRXClient
from companies.dataclasses import DartCompanyData
from companies.models import Company, CompanySector, Country

logger = logging.getLogger(__name__)

# SPAC 및 인수목적 회사 필터링 패턴
SPAC_SUFFIX_PATTERN = re.compile(r"(제\d+호스팩|스팩\d+호|[가-힣]+\d+호스팩|[가-힣]+비전스팩\d+호)$", re.IGNORECASE)
ACQUISITION_PURPOSE_PATTERN = re.compile(r"인수목적", re.IGNORECASE)


def _is_spac_or_acquisition_company(company_name: str) -> bool:
  """SPAC 또는 인수목적 회사 여부 판단

  Args:
    company_name: 회사명

  Returns:
    bool: SPAC 또는 인수목적 회사 여부
  """
  if SPAC_SUFFIX_PATTERN.search(company_name):
    return True
  if ACQUISITION_PURPOSE_PATTERN.search(company_name):
    return True
  return False


def _is_financial_company(company_name: str) -> bool:
  """회사명을 보고 금융업 여부 판단

  Args:
    company_name: 회사명

  Returns:
    bool: 금융업 여부
  """
  financial_keywords = ["금융", "증권", "보험", "카드", "캐피탈", "저축은행", "생명", "은행", "투자", "자산운용", "리츠", "리스"]

  return any(keyword in company_name for keyword in financial_keywords)


class DartCompanyIngestService:
  """DART 회사 정보 수집 서비스

  OpenDart API를 통해 회사 정보를 수집하고 Company 모델을 업데이트합니다.
  """

  def __init__(
    self,
    api_key: Optional[str] = None,
    dart_client: Optional[CorpCodeDartClient] = None,
    krx_client: Optional[CompanyInfoKRXClient] = None,
  ):
    """
    Args:
      api_key: OpenDart API 키 (None이면 settings에서 가져옴)
      dart_client: CorpCodeDartClient 인스턴스 (None이면 새로 생성)
      krx_client: CompanyInfoKRXClient 인스턴스 (None이면 새로 생성)
    """
    self.api_key = api_key
    self.dart_client = dart_client or CorpCodeDartClient(api_key=api_key)
    self.krx_client = krx_client or CompanyInfoKRXClient()

  def perform(self):
    """DART 회사 정보 수집 및 업데이트 수행"""
    with transaction.atomic():
      # DART에서 법인 코드 조회
      dart_data_list = self.fetch_dart_company_data()

      # KRX에서 업종(sector) 정보 조회
      krx_sector_map = self.fetch_krx_sector_data()

      # Company 모델 업데이트/생성
      stats = self.update_or_create_companies(dart_data_list, krx_sector_map)

    return stats

  def fetch_dart_company_data(self) -> List[DartCompanyData]:
    """DART API를 통해 회사 정보 조회

    Returns:
      List[DartCompanyData]: 회사 정보 리스트
    """
    logger.info("DART 회사 정보 조회 시작")

    corp_map = self.dart_client.fetch_corp_codes()

    # DartCompanyData 객체로 변환
    company_data_list: List[DartCompanyData] = [
      DartCompanyData(
        corp_code=info.get("corp_code", ""),
        corp_name=info.get("corp_name", ""),
        stock_code=stock_code,
        corp_eng_name=info.get("corp_eng_name"),
      ) for stock_code, info in corp_map.items()
    ]

    logger.info(f"DART 회사 정보 조회 완료: {len(company_data_list)}개")
    return company_data_list

  def fetch_krx_sector_data(self) -> Dict[str, str]:
    """KRX API를 통해 종목별 업종(sector) 정보 조회

    Returns:
      Dict[str, str]: stock_code를 키로 하는 sector 이름 딕셔너리
    """
    from datetime import datetime, timedelta

    logger.info("KRX 업종 정보 조회 시작")

    try:
      # KRX API는 거래일 기준이므로 어제 날짜 사용 (오늘은 데이터가 아직 없을 수 있음)
      yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
      logger.info(f"KRX 조회 기준일: {yesterday}")

      sector_map: Dict[str, str] = {}

      for market_code in ["STK", "KSQ"]:
        logger.info(f"KRX {market_code} 시장 업종 정보 조회 중...")
        company_list = self.krx_client.fetch_company_list(market_code=market_code, trade_date=yesterday)
        logger.info(f"KRX {market_code} 시장에서 {len(company_list)}개 회사 조회됨")

        for company_info in company_list:
          stock_code = company_info.get("stock_code")
          sector_name = company_info.get("sector", "").strip()

          if stock_code and sector_name:
            sector_map[stock_code] = sector_name

      logger.info(f"KRX 업종 정보 조회 완료: {len(sector_map)}개")
      return sector_map

    except Exception as e:
      logger.exception(f"KRX 업종 정보 조회 실패: {e}. 업종 정보 없이 진행합니다.")
      return {}

  def update_or_create_companies(
    self,
    dart_data_list: List[DartCompanyData],
    krx_sector_map: Dict[str, str],
  ) -> Dict[str, int]:
    """DART 데이터를 기반으로 Company 모델 업데이트 또는 생성

    Args:
      dart_data_list: DART 회사 정보 리스트
      krx_sector_map: stock_code를 키로 하는 sector 이름 딕셔너리

    Returns:
      Dict[str, int]: 업데이트 통계 정보
        - companies_created: 생성된 회사 수
        - companies_updated: 업데이트된 회사 수
        - total_dart_data: 처리한 DART 데이터 수
    """
    companies_created = 0
    companies_updated = 0

    # corp_code를 기준으로 Company 조회
    companies = Company.objects.filter(corp_code__isnull=False).exclude(corp_code="")
    corp_code_to_company: Dict[str, Company] = {
      company.corp_code: company
      for company in companies if company.corp_code  # None 체크
    }

    for dart_data in dart_data_list:
      try:
        # corp_code가 없으면 스킵
        if not dart_data.corp_code:
          logger.debug(f"corp_code가 없는 항목: {dart_data.stock_code}")
          continue

        # SPAC 또는 인수목적 회사 필터링
        if _is_spac_or_acquisition_company(dart_data.corp_name):
          logger.debug(f"SPAC/인수목적 회사 제외: {dart_data.corp_name} ({dart_data.corp_code})")
          continue

        # KRX에서 sector 정보 가져오기
        sector_name = krx_sector_map.get(dart_data.stock_code)

        # corp_code로 Company 조회
        company = corp_code_to_company.get(dart_data.corp_code)

        if company:
          # 기존 Company 업데이트
          updated = self._update_company(company, dart_data, sector_name)
          if updated:
            companies_updated += 1
        else:
          # 새로운 Company 생성
          company = self._create_company(dart_data, sector_name)
          corp_code_to_company[dart_data.corp_code] = company
          companies_created += 1
          logger.debug(f"Company 생성: {company.name} (corp_code: {dart_data.corp_code})")

      except Exception as e:
        logger.error(f"데이터 처리 실패 ({dart_data.stock_code}): {e}")
        continue

    logger.info(
      f"회사 정보 업데이트 완료 - "
      f"생성: {companies_created}, "
      f"업데이트: {companies_updated}, "
      f"전체 DART: {len(dart_data_list)}"
    )

    return {
      "companies_created": companies_created,
      "companies_updated": companies_updated,
      "total_dart_data": len(dart_data_list),
    }

  def _create_company(
    self,
    dart_data: DartCompanyData,
    sector_name: Optional[str] = None,
  ) -> Company:
    """DART 데이터로 새로운 Company 생성

    Args:
      dart_data: DART 회사 정보
      sector_name: KRX 업종명 (선택)

    Returns:
      Company: 생성된 Company 객체
    """
    # 기본 국가 조회 (한국)
    korea, _ = Country.objects.get_or_create(code="KR", defaults={"name": "대한민국"})

    # 금융업 여부 판단
    is_financial = _is_financial_company(dart_data.corp_name)

    # Sector 조회 또는 생성
    sector = None
    if sector_name:
      sector, _ = CompanySector.objects.get_or_create(name=sector_name)

    company = Company.objects.create(
      name=dart_data.corp_name,
      english_name=dart_data.corp_eng_name or "",
      corp_code=dart_data.corp_code,
      country=korea,
      sector=sector,
      is_financial=is_financial,
      primary_stock_code=dart_data.stock_code,  # primary_stock_code 저장
    )

    return company

  def _update_company(
    self,
    company: Company,
    dart_data: DartCompanyData,
    sector_name: Optional[str] = None,
  ) -> bool:
    """DART 데이터로 Company 업데이트

    Args:
      company: 업데이트할 Company 객체
      dart_data: DART 회사 정보
      sector_name: KRX 업종명 (선택)

    Returns:
      bool: 업데이트 여부
    """
    updated_fields: List[str] = []

    # corp_code 업데이트 (비어있는 경우에만)
    if not company.corp_code and dart_data.corp_code:
      company.corp_code = dart_data.corp_code
      updated_fields.append("corp_code")

    # english_name 업데이트 (비어있는 경우에만)
    if not company.english_name and dart_data.corp_eng_name:
      company.english_name = dart_data.corp_eng_name
      updated_fields.append("english_name")

    # primary_stock_code 업데이트 (비어있는 경우에만)
    if not company.primary_stock_code and dart_data.stock_code:
      company.primary_stock_code = dart_data.stock_code
      updated_fields.append("primary_stock_code")

    # sector 업데이트 (is_fixed_sector=False이고 sector_name이 있는 경우에만)
    if sector_name and not company.is_fixed_sector:
      sector, _ = CompanySector.objects.get_or_create(name=sector_name)
      if company.sector != sector:
        company.sector = sector
        updated_fields.append("sector")

    # 업데이트가 있는 경우에만 저장
    if updated_fields:
      updated_fields.append("updated_at")
      company.save(update_fields=updated_fields)
      logger.debug(f"Company 업데이트: {company.name} (fields: {', '.join(updated_fields)})")
      return True

    return False

  def close(self):
    """리소스 정리"""
    self.dart_client.close()
    self.krx_client.close()

  def __enter__(self):
    """Context manager 진입"""
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    """Context manager 종료"""
    self.close()
