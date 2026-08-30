from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from action_trackings.choices import ActionTypeChoices

from common.models import BaseModel

User = get_user_model()


class ActionTracking(BaseModel):
  """
    범용 액션 트래킹 모델

    - 모든 사용자 액션을 추적하기 위한 기본 모델
    - Proxy 모델을 통해 특정 액션 타입별로 확장
    """

  class Meta:
    db_table = "action_trackings"
    verbose_name = "액션 트래킹"
    verbose_name_plural = "액션 트래킹"
    indexes = [
      models.Index(fields=["user", "action_type", "-created_at"]),
      models.Index(fields=["action_type", "-created_at"]),
      models.Index(fields=["content_type", "object_id"]),
    ]

  # 액션을 수행한 사용자
  user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="action_trackings",
    verbose_name="사용자",
    db_index=True,
  )

  # 액션 타입
  action_type = models.CharField(
    max_length=50,
    choices=ActionTypeChoices.choices,
    verbose_name="액션 타입",
    db_index=True,
  )

  # Generic Foreign Key - 액션의 대상 객체
  content_type = models.ForeignKey(
    ContentType,
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    verbose_name="컨텐츠 타입",
  )
  object_id = models.PositiveIntegerField(
    null=True,
    blank=True,
    verbose_name="객체 ID",
  )
  content_object = GenericForeignKey("content_type", "object_id")

  # 추가 메타데이터 (JSON 형태로 저장)
  metadata = models.JSONField(
    default=dict,
    blank=True,
    verbose_name="메타데이터",
    help_text="액션과 관련된 추가 정보를 JSON 형태로 저장",
  )

  # IP 주소
  ip_address = models.GenericIPAddressField(
    null=True,
    blank=True,
    verbose_name="IP 주소",
  )

  # User Agent
  user_agent = models.TextField(
    null=True,
    blank=True,
    verbose_name="User Agent",
  )

  def __str__(self):
    return f"{self.user} - {self.get_action_type_display()} - {self.created_at}"

  @classmethod
  def track(cls, user, action_type, content_object=None, metadata=None, request=None):
    """
        액션을 추적하는 헬퍼 메서드

        Args:
            user: 액션을 수행한 사용자
            action_type: 액션 타입 (ActionTypeChoices)
            content_object: 액션의 대상 객체 (optional)
            metadata: 추가 메타데이터 (optional)
            request: HTTP 요청 객체 (optional, IP와 User-Agent 추출용)

        Returns:
            ActionTracking: 생성된 트래킹 객체
        """
    data = {
      "user": user,
      "action_type": action_type,
      "metadata": metadata or {},
    }

    # content_object가 있으면 추가
    if content_object:
      data["content_object"] = content_object

    # request가 있으면 IP와 User-Agent 추출
    if request:
      # IP 주소 추출
      x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
      if x_forwarded_for:
        ip_address = x_forwarded_for.split(",")[0].strip()
      else:
        ip_address = request.META.get("REMOTE_ADDR")
      data["ip_address"] = ip_address

      # User-Agent 추출
      data["user_agent"] = request.META.get("HTTP_USER_AGENT", "")

    return cls.objects.create(**data)
