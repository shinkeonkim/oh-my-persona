from django.db import models

from common.models import BaseModel
from matchmakings.choices import GenerationStatusChoice
from matchmakings.models.referral import Referral


class ReferralOverallOpinion(BaseModel):
  """추천에 대한 중개인의 종합의견 모델"""

  class Meta:
    db_table = "referral_overall_opinions"
    verbose_name = "Referral Overall Opinion"
    verbose_name_plural = "Referral Overall Opinions"

  referral = models.OneToOneField(
    Referral,
    on_delete=models.CASCADE,
    related_name="overall_opinion",
    verbose_name="추천",
  )

  opinion_for_male = models.TextField(
    verbose_name="남자에게 보여줄 의견",
    blank=True,
    default="",
  )

  opinion_for_female = models.TextField(
    verbose_name="여자에게 보여줄 의견",
    blank=True,
    default="",
  )

  generation_status = models.CharField(
    max_length=20,
    choices=GenerationStatusChoice.choices,
    default=GenerationStatusChoice.PENDING,
    verbose_name="생성 상태",
  )

  error_message = models.TextField(
    verbose_name="에러 메시지",
    blank=True,
    default="",
  )

  def __str__(self):
    return f"Overall Opinion for {self.referral} - {self.generation_status}"
