from django.contrib.auth import get_user_model
from django.db import models

from common.models import BaseModel
from matchmakings.choices import GenerationStatusChoice

User = get_user_model()


class Referral(BaseModel):

  class Meta:
    db_table = "referrals"
    verbose_name = "Referral"
    verbose_name_plural = "Referrals"
    constraints = [
      models.UniqueConstraint(
        fields=["user", "referral_user"],
        name="unique_user_referral_user",
      ),
    ]

  user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="received_referrals",
    verbose_name="추천을 받은 사용자",
  )
  referral_user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="suggested_referrals",
    verbose_name="추천된 사용자",
  )
  referred_at = models.DateTimeField(verbose_name="추천 일시")
  referred_algorithm = models.CharField(
    verbose_name="추천 알고리즘",
    max_length=255,
  )

  compatibility_score = models.IntegerField(default=0, verbose_name="궁합 점수")

  synergy_generation_status = models.CharField(
    max_length=20,
    choices=GenerationStatusChoice.choices,
    default=GenerationStatusChoice.PENDING,
    verbose_name="시너지 생성 상태",
  )

  compatibility_tags = models.ManyToManyField(
    "matchmakings.CompatibilityTag",
    through="matchmakings.ReferralCompatibilityTag",
    related_name="referrals",
    verbose_name="궁합 태그",
  )

  def __str__(self):
    return f"{self.user} <- {self.referral_user} ({self.referred_at})"
