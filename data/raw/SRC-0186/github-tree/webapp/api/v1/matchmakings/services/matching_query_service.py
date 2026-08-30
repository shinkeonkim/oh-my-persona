from django.db.models import Case, DateTimeField, Q, When

from common.utils.logger import get_logger
from matchmakings.models import Matching

logger = get_logger(__name__)


class MatchingQueryService:
    """매칭 조회 관련 서비스"""

    @staticmethod
    def get_sent_matchings(user):
        """사용자가 보낸 호감 목록 조회 (진행 중인 호감만)"""
        try:
            matchings = (
                Matching.objects.filter(
                    sender=user,
                    received_at__isnull=True,
                    rejected_at__isnull=True,
                    expired_at__isnull=True,
                )
                .select_related(
                    "sender__profile__job_info",
                    "receiver__profile__job_info",
                )
                .order_by("-sent_at")
            )

            return matchings
        except Exception as e:
            logger.error("Failed to fetch sent matchings", exception=e, user_id=user.id)
            raise

    @staticmethod
    def get_received_matchings(user):
        """사용자가 받은 호감 목록 조회 (진행 중인 호감만)"""
        try:
            matchings = (
                Matching.objects.filter(
                    receiver=user,
                    received_at__isnull=True,
                    rejected_at__isnull=True,
                    expired_at__isnull=True,
                )
                .select_related(
                    "sender__profile__job_info",
                    "receiver__profile__job_info",
                )
                .order_by("-sent_at")
            )

            return matchings
        except Exception as e:
            logger.error("Failed to fetch received matchings", exception=e, user_id=user.id)
            raise

    @staticmethod
    def get_completed_matchings(user):
        """매칭 완료 목록 조회 (양쪽 모두 수락한 경우)"""
        try:
            matchings = (
                Matching.objects.filter(Q(sender=user) | Q(receiver=user), received_at__isnull=False)
                .select_related("sender__profile__job_info", "receiver__profile__job_info")
                .order_by("-received_at")
            )

            return matchings
        except Exception as e:
            logger.error("Failed to fetch completed matchings", exception=e, user_id=user.id)
            raise

    @staticmethod
    def get_past_connections(user):
        """지난 인연 목록 조회 (거절되었거나 매칭이 성사되지 않은 경우)"""
        try:
            matchings = (
                Matching.objects.filter(
                    Q(sender=user) | Q(receiver=user),
                    Q(rejected_at__isnull=False) | Q(expired_at__isnull=False),
                )
                .select_related("sender__profile__job_info", "receiver__profile__job_info")
                .annotate(
                    past_connection_at=Case(
                        When(rejected_at__isnull=False, then="rejected_at"),
                        When(expired_at__isnull=False, then="expired_at"),
                        output_field=DateTimeField(),
                    )
                )
                .order_by("-past_connection_at")
            )

            return matchings
        except Exception as e:
            logger.error("Failed to fetch past connections", exception=e, user_id=user.id)
            raise
