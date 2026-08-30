"""
Delisted Stock Ingest Service

상장 폐지 종목 정보 수집 서비스
"""

import logging
from datetime import date, datetime
from typing import Dict, List

from django.db import transaction

from stocks.models import DelistedStock, Market, Stock

from common.clients.krx import DelistedStockKRXClient

logger = logging.getLogger(__name__)


class DelistedStockIngestService:
  """상장 폐지 종목 정보 수집 서비스"""

  def __init__(self):
    self.client = DelistedStockKRXClient()

  def perform(
    self,
    start_date: str,
    end_date: str,
    market_id: str = "ALL",
  ) -> Dict[str, int]:
    """상장 폐지 종목 정보 수집

        Args:
            start_date: 조회 시작일 (YYYYMMDD 형식)
            end_date: 조회 종료일 (YYYYMMDD 형식)
            market_id: 시장 구분 (ALL, STK=KOSPI, KSQ=KOSDAQ)

        Returns:
            Dict[str, int]: 수집 결과 통계
                - total: 총 조회된 종목 수
                - created: 새로 생성된 종목 수
                - updated: 업데이트된 종목 수
                - skipped: 스킵된 종목 수
        """
    logger.info(f"상장 폐지 종목 정보 수집 시작: start_date={start_date}, end_date={end_date}, market_id={market_id}")

    # KRX API에서 데이터 가져오기
    try:
      raw_data = self.client.fetch_delisted_stocks(
        start_date=start_date,
        end_date=end_date,
        market_id=market_id,
      )
    except Exception as e:
      logger.error(f"상장 폐지 종목 정보 조회 실패: {e}")
      raise

    # 데이터 저장
    stats = self._save_delisted_stocks(raw_data)

    # Stock 모델의 delisted_date 동기화
    sync_stats = self._sync_stock_delisted_dates()
    stats["stock_updated"] = sync_stats["updated"]
    stats["stock_delisted"] = sync_stats["delisted"]

    logger.info(
      f"상장 폐지 종목 정보 수집 완료: total={stats['total']}, "
      f"created={stats['created']}, updated={stats['updated']}, skipped={stats['skipped']}, "
      f"stock_updated={stats['stock_updated']}, stock_delisted={stats['stock_delisted']}"
    )

    return stats

  @transaction.atomic
  def _save_delisted_stocks(self, raw_data: List[Dict]) -> Dict[str, int]:
    """상장 폐지 종목 정보 저장

        Args:
            raw_data: KRX API에서 받은 원본 데이터 리스트

        Returns:
            Dict[str, int]: 저장 결과 통계
        """
    created_count = 0
    updated_count = 0
    skipped_count = 0

    for item in raw_data:
      try:
        # 날짜 파싱
        list_dd = self._parse_date(item.get("LIST_DD", ""))
        delist_dd = self._parse_date(item.get("DELIST_DD", ""))
        arrantrd_mktact_enforce_dd = self._parse_date(item.get("ARRANTRD_MKTACT_ENFORCE_DD", ""))
        arrantrd_end_dd = self._parse_date(item.get("ARRANTRD_END_DD", ""))

        if not list_dd or not delist_dd:
          logger.warning(f"필수 날짜 정보 누락: ISU_CD={item.get('ISU_CD')}, {item}")
          skipped_count += 1
          continue

        # 시장 정보 매핑 (KOSPI, KOSDAQ만)
        market_name = item.get("MKT_NM", "")
        market = self._get_market_by_name(market_name)

        # DelistedStock 생성 또는 업데이트
        delisted_stock, created = DelistedStock.objects.update_or_create(
          isu_cd=item.get("ISU_CD", ""),
          list_dd=list_dd,
          delist_dd=delist_dd,
          defaults={
            "isu_nm": item.get("ISU_NM", ""),
            "market": market,
            "secugrp_nm": item.get("SECUGRP_NM", ""),
            "kind_stkcert_tp_nm": item.get("KIND_STKCERT_TP_NM", ""),
            "delist_rsn_dsc": item.get("DELIST_RSN_DSC", ""),
            "arrantrd_mktact_enforce_dd": arrantrd_mktact_enforce_dd,
            "arrantrd_end_dd": arrantrd_end_dd,
            "idx_ind_nm": item.get("IDX_IND_NM", ""),
            "parval": item.get("PARVAL", ""),
            "list_shrs": item.get("LIST_SHRS", ""),
            "to_isu_srt_cd": item.get("TO_ISU_SRT_CD", ""),
            "to_isu_abbrv": item.get("TO_ISU_ABBRV", ""),
            "raw": item,
          },
        )

        if created:
          created_count += 1
          logger.debug(f"상장 폐지 종목 생성: {delisted_stock.isu_nm} ({delisted_stock.isu_cd})")
        else:
          updated_count += 1
          logger.debug(f"상장 폐지 종목 업데이트: {delisted_stock.isu_nm} ({delisted_stock.isu_cd})")

      except Exception as e:
        logger.error(f"상장 폐지 종목 저장 실패: {item.get('ISU_CD')}, {e}")
        skipped_count += 1
        continue

    return {
      "total": len(raw_data),
      "created": created_count,
      "updated": updated_count,
      "skipped": skipped_count,
    }

  def _get_market_by_name(self, market_name: str) -> Market | None:
    """시장 이름으로 Market 객체 조회 (KOSPI, KOSDAQ만)

        Args:
            market_name: 시장 이름 (KOSPI, KOSDAQ 등)

        Returns:
            Market: Market 객체, KOSPI/KOSDAQ이 아니거나 찾을 수 없으면 None
        """
    if not market_name:
      return None

    # KOSPI, KOSDAQ만 연결
    if market_name == "KOSPI":
      try:
        return Market.objects.get(code="STK")
      except Market.DoesNotExist:
        logger.warning("KOSPI 시장을 찾을 수 없습니다. code=STK")
        return None
    elif market_name == "KOSDAQ":
      try:
        return Market.objects.get(code="KSQ")
      except Market.DoesNotExist:
        logger.warning("KOSDAQ 시장을 찾을 수 없습니다. code=KSQ")
        return None
    else:
      # KONEX 등 다른 시장은 연결하지 않음
      logger.debug(f"시장 연결 제외: {market_name}")
      return None

  @transaction.atomic
  def _sync_stock_delisted_dates(self) -> Dict[str, int]:
    """DelistedStock의 delist_dd를 Stock의 delisted_date에 동기화

        DelistedStock에 있는 종목 중 Stock 테이블에도 존재하는 종목들에 대해
        상장폐지일(delist_dd)을 Stock 모델의 delisted_date 필드에 업데이트하고
        is_listed를 False로 설정합니다.

        Returns:
            Dict[str, int]: 동기화 결과 통계
                - updated: 업데이트된 Stock 레코드 수
                - delisted: 상장폐지 처리된 Stock 레코드 수
        """
    updated_count = 0
    delisted_count = 0

    # DelistedStock 전체 조회
    delisted_stocks = DelistedStock.objects.select_related("market").all()

    for delisted_stock in delisted_stocks:
      try:
        # ISU_CD는 6자리 종목코드 (예: 000885)로 직접 저장됨
        isu_cd = delisted_stock.isu_cd

        if not isu_cd:
          logger.debug("ISU_CD가 비어있음")
          continue

        # Stock 조회 (ISU_CD를 code로 직접 사용)
        try:
          stock = Stock.objects.get(code=isu_cd)
        except Stock.DoesNotExist:
          logger.debug(f"Stock 찾을 수 없음: {isu_cd}")
          continue

        # delisted_date 업데이트
        updated = False
        if stock.delisted_date != delisted_stock.delist_dd:
          stock.delisted_date = delisted_stock.delist_dd
          updated = True

        # is_listed를 False로 설정
        if stock.is_listed:
          stock.is_listed = False
          updated = True
          delisted_count += 1

        if updated:
          stock.save(update_fields=["delisted_date", "is_listed", "updated_at"])
          updated_count += 1
          logger.debug(
            f"Stock 상장폐지 정보 업데이트: {stock.name} ({stock.code}), "
            f"delisted_date={delisted_stock.delist_dd}"
          )

      except Exception as e:
        logger.error(f"Stock 상장폐지 정보 동기화 실패: ISU_CD={delisted_stock.isu_cd}, {e}")
        continue

    logger.info(f"Stock 상장폐지 정보 동기화 완료: updated={updated_count}, delisted={delisted_count}")

    return {
      "updated": updated_count,
      "delisted": delisted_count,
    }

  def _parse_date(self, date_str: str) -> date | None:
    """날짜 문자열 파싱

        Args:
            date_str: 날짜 문자열 (YYYY/MM/DD 또는 YYYYMMDD 형식)

        Returns:
            date: 파싱된 날짜 객체, 실패 시 None
        """
    if not date_str or date_str.strip() == "":
      return None

    try:
      # YYYY/MM/DD 형식
      if "/" in date_str:
        return datetime.strptime(date_str, "%Y/%m/%d").date()
      # YYYYMMDD 형식
      elif len(date_str) == 8:
        return datetime.strptime(date_str, "%Y%m%d").date()
      else:
        logger.warning(f"지원하지 않는 날짜 형식: {date_str}")
        return None
    except ValueError as e:
      logger.warning(f"날짜 파싱 실패: {date_str}, {e}")
      return None

  def close(self):
    """클라이언트 세션 종료"""
    if self.client:
      self.client.close()

  def __enter__(self):
    """Context manager 진입"""
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    """Context manager 종료"""
    self.close()
