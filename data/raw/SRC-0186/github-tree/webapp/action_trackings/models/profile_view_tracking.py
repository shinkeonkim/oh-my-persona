from django.contrib.auth import get_user_model

from action_trackings.choices import ActionTypeChoices

from .action_tracking import ActionTracking

User = get_user_model()


class ProfileViewTrackingManager(ActionTracking.objects.__class__):
  """프로필 조회 트래킹 전용 매니저"""

  def get_queryset(self):
    return super().get_queryset().filter(action_type=ActionTypeChoices.PROFILE_VIEW)

  def track_profile_view(self, viewer, viewed_profile, request=None, **metadata):
    """
        프로필 조회를 추적하는 헬퍼 메서드

        Args:
            viewer: 프로필을 조회한 사용자
            viewed_profile: 조회된 프로필 객체
            request: HTTP 요청 객체 (optional)
            **metadata: 추가 메타데이터

        Returns:
            ProfileViewTracking: 생성된 트래킹 객체
        """
    # 기본 메타데이터 구성
    tracking_metadata = {
      "viewed_user_id": viewed_profile.user.id if hasattr(viewed_profile, "user") else None,
      "viewed_profile_id": viewed_profile.id,
      **metadata,
    }

    return ActionTracking.track(
      user=viewer,
      action_type=ActionTypeChoices.PROFILE_VIEW,
      content_object=viewed_profile,
      metadata=tracking_metadata,
      request=request,
    )


class ProfileViewTracking(ActionTracking):
  """
    프로필 조회 트래킹 Proxy 모델

    ActionTracking을 상속받아 프로필 조회 액션만 다루는 Proxy 모델입니다.
    """

  class Meta:
    proxy = True
    verbose_name = "프로필 조회 트래킹"
    verbose_name_plural = "프로필 조회 트래킹"

  objects = ProfileViewTrackingManager()

  def save(self, *args, **kwargs):
    """저장 시 action_type을 자동으로 설정"""
    self.action_type = ActionTypeChoices.PROFILE_VIEW
    super().save(*args, **kwargs)
