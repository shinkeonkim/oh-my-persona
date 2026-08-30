from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest

from action_trackings.models import ProfileViewTracking

from common.utils.logger import get_logger
from profiles.models import Profile

User = get_user_model()
logger = get_logger(__name__)


class ProfileViewTrackingService:
  """프로필 조회 트래킹 전용 서비스"""

  @staticmethod
  def track_profile_view(
    viewer: User,
    viewed_profile,
    request: Optional[HttpRequest] = None,
    **metadata,
  ) -> Optional[ProfileViewTracking]:
    """
        프로필 조회를 추적합니다.

        Args:
            viewer: 프로필을 조회한 사용자
            viewed_profile: 조회된 프로필 객체
            request: HTTP 요청 객체 (optional)
            **metadata: 추가 메타데이터

        Returns:
            ProfileViewTracking: 생성된 트래킹 객체 또는 None (실패 시)
        """
    try:
      # 자기 자신의 프로필 조회는 트래킹하지 않음
      if hasattr(viewed_profile, "user") and viewer.id == viewed_profile.user.id:
        logger.debug(
          "Skipping self-profile view tracking",
          viewer_id=viewer.id,
        )
        return None

      tracking = ProfileViewTracking.objects.track_profile_view(
        viewer=viewer,
        viewed_profile=viewed_profile,
        request=request,
        **metadata,
      )

      logger.info(
        "Profile view tracked",
        viewer_id=viewer.id,
        viewed_profile_id=viewed_profile.id,
        tracking_id=tracking.id,
      )

      return tracking

    except Exception as e:
      logger.error(
        "Failed to track profile view",
        exception=e,
        viewer_id=viewer.id if viewer else None,
        viewed_profile_id=viewed_profile.id if viewed_profile else None,
      )
      return None

  @staticmethod
  def get_profile_view_count(profile) -> int:
    """
        특정 프로필의 조회 횟수를 반환합니다.

        Args:
            profile: 조회 횟수를 확인할 프로필 객체

        Returns:
            int: 조회 횟수
        """
    try:
      content_type = ContentType.objects.get_for_model(profile)
      return ProfileViewTracking.objects.filter(
        content_type=content_type,
        object_id=profile.id,
      ).count()

    except Exception as e:
      logger.error(
        "Failed to get profile view count",
        exception=e,
        profile_id=profile.id if profile else None,
      )
      return 0

  @staticmethod
  def get_profile_viewers(profile, limit: int = 50) -> list:
    """
        특정 프로필을 조회한 사용자 목록을 반환합니다.

        Args:
            profile: 프로필 객체
            limit: 조회할 최대 개수

        Returns:
            list: 조회한 사용자 목록
        """
    try:
      from django.contrib.contenttypes.models import ContentType

      content_type = ContentType.objects.get_for_model(profile)
      trackings = (ProfileViewTracking.objects.filter(
        content_type=content_type,
        object_id=profile.id,
      ).select_related("user").order_by("-created_at")[:limit])

      return [tracking.user for tracking in trackings]

    except Exception as e:
      logger.error(
        "Failed to get profile viewers",
        exception=e,
        profile_id=profile.id if profile else None,
      )
      return []

  @staticmethod
  def get_recent_profile_views(viewer: User, limit: int = 20) -> list:
    """
        사용자가 최근에 조회한 프로필 목록을 반환합니다.

        Args:
            viewer: 조회한 사용자
            limit: 조회할 최대 개수

        Returns:
            list: ProfileViewTracking 객체 리스트
        """
    try:
      return list(
        ProfileViewTracking.objects.filter(user=viewer).select_related("content_type").order_by("-created_at")[:limit])

    except Exception as e:
      logger.error(
        "Failed to get recent profile views",
        exception=e,
        viewer_id=viewer.id if viewer else None,
      )
      return []

  @staticmethod
  def get_mutual_profile_views(user1: User, user2: User) -> dict:
    """
        두 사용자 간의 상호 프로필 조회 이력을 반환합니다.

        Args:
            user1: 사용자 1
            user2: 사용자 2

        Returns:
            dict: {
                'user1_viewed_user2': bool,
                'user2_viewed_user1': bool,
                'user1_view_count': int,
                'user2_view_count': int,
            }
        """
    try:
      from django.contrib.contenttypes.models import ContentType

      profile_content_type = ContentType.objects.get_for_model(Profile)

      # user1이 user2의 프로필을 조회한 횟수
      user1_views = ProfileViewTracking.objects.filter(
        user=user1,
        content_type=profile_content_type,
        metadata__viewed_user_id=user2.id,
      ).count()

      # user2가 user1의 프로필을 조회한 횟수
      user2_views = ProfileViewTracking.objects.filter(
        user=user2,
        content_type=profile_content_type,
        metadata__viewed_user_id=user1.id,
      ).count()

      return {
        "user1_viewed_user2": user1_views > 0,
        "user2_viewed_user1": user2_views > 0,
        "user1_view_count": user1_views,
        "user2_view_count": user2_views,
      }

    except Exception as e:
      logger.error(
        "Failed to get mutual profile views",
        exception=e,
        user1_id=user1.id if user1 else None,
        user2_id=user2.id if user2 else None,
      )
      return {
        "user1_viewed_user2": False,
        "user2_viewed_user1": False,
        "user1_view_count": 0,
        "user2_view_count": 0,
      }
