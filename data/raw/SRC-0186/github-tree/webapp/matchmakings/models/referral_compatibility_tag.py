from django.db import models

from common.models import BaseModel


class ReferralCompatibilityTag(BaseModel):

  class Meta:
    db_table = "referral_compatibility_tags"
    verbose_name = "Referral Compatibility Tag"
    verbose_name_plural = "Referral Compatibility Tags"
    unique_together = [["referral", "compatibility_tag"]]

  referral = models.ForeignKey(
    "matchmakings.Referral",
    on_delete=models.CASCADE,
    related_name="referral_compatibility_tags",
    verbose_name="추천",
  )
  compatibility_tag = models.ForeignKey(
    "matchmakings.CompatibilityTag",
    on_delete=models.CASCADE,
    related_name="referral_compatibility_tags",
    verbose_name="궁합 태그",
  )

  def __str__(self):
    return f"{self.referral} - {self.compatibility_tag}"
