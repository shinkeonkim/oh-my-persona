from django.db import models

from common.models import BaseModel


class DelistedStock(BaseModel):
  """
    상장 폐지된 주식 정보를 저장하는 모델입니다.
    """

  class Meta:
    db_table = "delisted_stocks"
    verbose_name = "Delisted Stock"
    verbose_name_plural = "Delisted Stocks"
    indexes = [
      models.Index(fields=["isu_cd"], name="idx_delisted_isu_cd"),
      models.Index(fields=["market"], name="idx_delisted_market"),
      models.Index(fields=["delist_dd"], name="idx_delisted_delist_dd"),
      models.Index(fields=["-delist_dd"], name="idx_delisted_delist_dd_desc"),
    ]
    constraints = [
      models.UniqueConstraint(
        fields=["isu_cd", "list_dd", "delist_dd"],
        name="unique_delisted_stock_isu_list_delist",
      ),
    ]

  # 기본 종목 정보
  isu_cd = models.CharField(
    max_length=20,
    verbose_name="종목 코드",
    help_text="ISU_CD",
  )
  isu_nm = models.CharField(
    max_length=255,
    verbose_name="종목명",
    help_text="ISU_NM",
  )

  # 시장 정보 (KOSPI, KOSDAQ만 연결)
  market = models.ForeignKey(
    "stocks.Market",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="delisted_stocks",
    verbose_name="시장",
    help_text="KOSPI 또는 KOSDAQ 시장",
  )

  # 증권 그룹 정보
  secugrp_nm = models.CharField(
    max_length=50,
    blank=True,
    default="",
    verbose_name="증권 그룹",
    help_text="SECUGRP_NM (주권, 수익증권, 신주인수권증서, 신주인수권증권 등)",
  )
  kind_stkcert_tp_nm = models.CharField(
    max_length=50,
    blank=True,
    default="",
    verbose_name="주식 종류",
    help_text="KIND_STKCERT_TP_NM (보통주, 우선주 등)",
  )

  # 상장/상장폐지 일자
  list_dd = models.DateField(
    verbose_name="상장일",
    help_text="LIST_DD",
  )
  delist_dd = models.DateField(
    verbose_name="상장폐지일",
    help_text="DELIST_DD",
  )

  # 상장폐지 사유
  delist_rsn_dsc = models.TextField(
    blank=True,
    default="",
    verbose_name="상장폐지 사유",
    help_text="DELIST_RSN_DSC",
  )

  # 정리매매 기간
  arrantrd_mktact_enforce_dd = models.DateField(
    null=True,
    blank=True,
    verbose_name="정리매매 시작일",
    help_text="ARRANTRD_MKTACT_ENFORCE_DD",
  )
  arrantrd_end_dd = models.DateField(
    null=True,
    blank=True,
    verbose_name="정리매매 종료일",
    help_text="ARRANTRD_END_DD",
  )

  # 업종 정보
  idx_ind_nm = models.CharField(
    max_length=100,
    blank=True,
    default="",
    verbose_name="업종명",
    help_text="IDX_IND_NM",
  )

  # 액면가 및 상장주식수
  parval = models.CharField(
    max_length=50,
    blank=True,
    default="",
    verbose_name="액면가",
    help_text="PARVAL",
  )
  list_shrs = models.CharField(
    max_length=50,
    blank=True,
    default="",
    verbose_name="상장주식수",
    help_text="LIST_SHRS (쉼표 포함 문자열)",
  )

  # 전환 종목 정보 (합병 등의 경우)
  to_isu_srt_cd = models.CharField(
    max_length=20,
    blank=True,
    default="",
    verbose_name="전환 종목 코드",
    help_text="TO_ISU_SRT_CD",
  )
  to_isu_abbrv = models.CharField(
    max_length=255,
    blank=True,
    default="",
    verbose_name="전환 종목 약어",
    help_text="TO_ISU_ABBRV",
  )

  # 원본 데이터 저장
  raw = models.JSONField(
    default=dict,
    blank=True,
    verbose_name="원본 데이터",
    help_text="KRX API에서 받은 원본 JSON 데이터",
  )

  def __str__(self) -> str:
    return f"{self.isu_nm} ({self.isu_cd}) - 폐지일: {self.delist_dd}"
