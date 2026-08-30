from django.db import models

from common.models import BaseModel
from users.models.user import FemaleUser, MaleUser


class PreMatchingStatus(models.TextChoices):
  # 점수 계산 전 대기상태
  PENDING = "PENDING"
  # 점수 계산 중
  CALCULATING = "CALCULATING"
  # 점수 계산 완료 및 추천 대기 상태
  COMPLETED = "COMPLETED"
  # 추천됨
  RECOMMENDED = "RECOMMENDED"


class PreMatching(BaseModel):

  class Meta:
    db_table = "pre_matchings"
    verbose_name = "Pre Matching"
    verbose_name_plural = "Pre Matchings"
    unique_together = [["male_user", "female_user"]]

  male_user = models.ForeignKey(MaleUser, on_delete=models.CASCADE, related_name="male_pre_matchings")
  female_user = models.ForeignKey(FemaleUser, on_delete=models.CASCADE, related_name="female_pre_matchings")
  status = models.CharField(
    max_length=20,
    choices=PreMatchingStatus.choices,
    default=PreMatchingStatus.PENDING,
  )

  matching_reason = models.TextField(null=True, blank=True, verbose_name="매칭 사유")

  # 마지막으로 점수가 계산된 시간 (중복 실행 방지용)
  last_calculated_at = models.DateTimeField(null=True, blank=True, verbose_name="마지막 계산 시간")

  # TODO: referral에도 캐싱하기
  compatibility_score = models.IntegerField(default=0, verbose_name="궁합 점수")
