from typing import Any, Dict, Optional

from django.contrib.auth import get_user_model
from django.http import HttpRequest

from action_trackings.choices import ActionTypeChoices
from action_trackings.models import ActionTracking

from common.utils.logger import get_logger

User = get_user_model()
logger = get_logger(__name__)


class ActionTrackingService:
  """범용 액션 트래킹 서비스"""

  @staticmethod
  def track_action(
    user: User,
    action_type: str,
    content_object: Any = None,
    metadata: Optional[Dict] = None,
    request: Optional[HttpRequest] = None,
  ) -> Optional[ActionTracking]:
    """
        액션을 추적합니다.

        Args:
            user: 액션을 수행한 사용자
            action_type: 액션 타입 (ActionTypeChoices의 값)
            content_object: 액션의 대상 객체 (optional)
            metadata: 추가 메타데이터 (optional)
            request: HTTP 요청 객체 (optional)

        Returns:
            ActionTracking: 생성된 트래킹 객체 또는 None (실패 시)
        """
    try:
      # action_type 유효성 검사
      if action_type not in dict(ActionTypeChoices.choices):
        logger.warning(
          f"Invalid action_type: {action_type}",
          user_id=user.id if user else None,
        )
        return None

      tracking = ActionTracking.track(
        user=user,
        action_type=action_type,
        content_object=content_object,
        metadata=metadata,
        request=request,
      )

      logger.info(
        f"Action tracked: {action_type}",
        user_id=user.id,
        tracking_id=tracking.id,
        action_type=action_type,
      )

      return tracking

    except Exception as e:
      logger.error(
        "Failed to track action",
        exception=e,
        user_id=user.id if user else None,
        action_type=action_type,
      )
      return None

  @staticmethod
  def get_user_actions(
    user: User,
    action_type: Optional[str] = None,
    limit: int = 100,
  ) -> list:
    """
        사용자의 액션 이력을 조회합니다.

        Args:
            user: 조회할 사용자
            action_type: 특정 액션 타입으로 필터링 (optional)
            limit: 조회할 최대 개수

        Returns:
            list: ActionTracking 객체 리스트
        """
    try:
      queryset = ActionTracking.objects.filter(user=user).order_by("-created_at")

      if action_type:
        queryset = queryset.filter(action_type=action_type)

      return list(queryset[:limit])

    except Exception as e:
      logger.error(
        "Failed to get user actions",
        exception=e,
        user_id=user.id,
      )
      return []

  @staticmethod
  def get_action_count(
    user: User,
    action_type: Optional[str] = None,
  ) -> int:
    """
        사용자의 액션 횟수를 조회합니다.

        Args:
            user: 조회할 사용자
            action_type: 특정 액션 타입으로 필터링 (optional)

        Returns:
            int: 액션 횟수
        """
    try:
      queryset = ActionTracking.objects.filter(user=user)

      if action_type:
        queryset = queryset.filter(action_type=action_type)

      return queryset.count()

    except Exception as e:
      logger.error(
        "Failed to get action count",
        exception=e,
        user_id=user.id,
      )
      return 0
