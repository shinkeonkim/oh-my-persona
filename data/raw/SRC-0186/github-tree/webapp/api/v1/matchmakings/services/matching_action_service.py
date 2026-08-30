from django.db import transaction

from api.v1.matchmakings.exceptions import MatchingValidationError
from common.utils.logger import get_logger

logger = get_logger(__name__)


class MatchingActionService:
    """매칭 액션 처리 관련 서비스"""

    @staticmethod
    @transaction.atomic
    def process_matching_action(matching, action):
        """매칭 액션 처리 (승인/거부)"""
        if matching.received_at or matching.rejected_at:
            raise MatchingValidationError(
                message="Matching already processed",
                details={"matching_id": matching.id},
            )

        if action == "accept":
            matching.accept()
        elif action == "reject":
            matching.reject()
        else:
            raise MatchingValidationError(message=f"Invalid action: {action}", details={"action": action})

        matching.save()
        return matching
