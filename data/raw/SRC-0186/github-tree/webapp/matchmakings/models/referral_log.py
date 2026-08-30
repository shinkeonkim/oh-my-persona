from django.contrib.auth import get_user_model
from django.db import models

from common.models import BaseModel

User = get_user_model()


class ReferralLog(BaseModel):

  class Meta:
    db_table = "referral_logs"
    verbose_name = "Referral Log"
    verbose_name_plural = "Referral Logs"

  referral = models.ForeignKey(
    "matchmakings.Referral",
    on_delete=models.SET_NULL,
    related_name="logs",
    verbose_name="추천",
    null=True,
    blank=True,
  )
  user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="received_referral_logs",
    verbose_name="추천을 받은 사용자",
  )
  referral_user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="suggested_referral_logs",
    verbose_name="추천된 사용자",
  )
  referred_at = models.DateTimeField(verbose_name="추천 일시")
  referred_algorithm = models.CharField(
    verbose_name="추천 알고리즘",
    max_length=255,
  )

  def __str__(self):
    return f"[LOG] {self.user} <- {self.referral_user} ({self.referred_at})"
