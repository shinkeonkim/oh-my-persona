from django.db import models

from common.models import BaseModel
from matchmakings.choices import GenerationStatusChoice
from matchmakings.models.referral import Referral


class ReferralSynergy(BaseModel):
  """추천에 대한 천생연분 시너지 모델"""

  class Meta:
    db_table = "referral_synergies"
    verbose_name = "Referral Synergy"
    verbose_name_plural = "Referral Synergies"

  referral = models.ForeignKey(
    Referral,
    on_delete=models.CASCADE,
    related_name="synergies",
    verbose_name="추천",
  )

  title = models.CharField(
    max_length=255,
    verbose_name="시너지 제목",
    blank=True,
    default="",
  )

  description = models.TextField(
    verbose_name="시너지 설명",
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
    return f"Synergy for {self.referral} - {self.generation_status}"
