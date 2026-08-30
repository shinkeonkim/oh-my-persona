from django.db import models

from common.models import BaseModel


class Company(BaseModel):
  """회사 모델

    실제 법인(회사) 정보를 저장하는 모델입니다.
    한 회사가 여러 주식을 상장할 수 있으므로 주식 정보는 CompanyStock 모델에서 관리합니다.
    """

  class Meta:
    db_table = "companies"
    verbose_name = "Company"
    verbose_name_plural = "Companies"
    indexes = [
      models.Index(fields=["name"], name="idx_company_name"),
    ]

  # 회사 기본 정보
  name = models.CharField(
    max_length=255,
    verbose_name="회사명",
  )
  english_name = models.CharField(
    max_length=255,
    blank=True,
    null=True,
    verbose_name="영문 회사명",
  )

  corp_code = models.CharField(
    max_length=20,
    unique=True,
    null=False,
    blank=False,
    verbose_name="법인 코드 (DART)",
    help_text="DART API에서 사용하는 고유 법인 코드",
  )

  country = models.ForeignKey(
    "companies.Country",
    on_delete=models.PROTECT,
    related_name="companies",
    verbose_name="국가",
  )

  # 산업 분류
  sector = models.ForeignKey(
    "companies.CompanySector",
    on_delete=models.SET_NULL,
    related_name="companies",
    null=True,
    blank=True,
    verbose_name="섹터",
  )

  industry = models.ForeignKey(
    "companies.CompanyIndustry",
    on_delete=models.SET_NULL,
    related_name="companies",
    null=True,
    blank=True,
    verbose_name="산업",
  )

  is_fixed_sector = models.BooleanField(default=False, verbose_name="섹터 고정 여부")
  is_fixed_industry = models.BooleanField(default=False, verbose_name="산업군 고정 여부")
  is_financial = models.BooleanField(default=False, verbose_name="금융업 여부")

  # 회사 정보
  website = models.URLField(
    max_length=300,
    blank=True,
    null=True,
    verbose_name="웹사이트",
  )

  description = models.TextField(
    blank=True,
    default="",
    verbose_name="회사 설명",
  )

  primary_stock_code = models.CharField(
    max_length=20,
    blank=True,
    null=True,
    unique=True,
    verbose_name="기본 주식 코드",
    help_text="DART 기준 데이터 수집용 / 실제 API에 사용 X",
  )

  def __str__(self) -> str:
    return self.name
