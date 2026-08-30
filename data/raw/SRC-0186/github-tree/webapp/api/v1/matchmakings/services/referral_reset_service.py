from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction

from common.exceptions.custom_exceptions import ValidationError
from common.utils.logger import get_logger
from users.models import TicketLog, TicketLogCategory

User = get_user_model()

logger = get_logger(__name__)

REFERRAL_QUOTA_RESET_TICKET_COST = settings.REFERRAL_QUOTA_RESET_TICKET_COST
REFERRAL_QUOTA_MAX = settings.REFERRAL_QUOTA_MAX


class ReferralResetService:
    """추천 횟수 초기화 서비스"""

    @staticmethod
    @transaction.atomic
    def reset_referral_quota(user):
        """추천 횟수 초기화"""
        try:
            locked_user = type(user).objects.select_for_update().get(pk=user.pk)

            if locked_user.can_receive_referral():
                raise ValidationError(
                    message="추천 횟수가 남아있어 초기화할 수 없습니다.",
                    details={
                        "remaining_quota": locked_user.remaining_referral_quota_count,
                        "message": "추천 횟수를 모두 소진한 후 초기화할 수 있습니다.",
                    },
                )

            if locked_user.ticket_amount < REFERRAL_QUOTA_RESET_TICKET_COST:
                raise ValidationError(
                    message="티켓이 부족합니다.",
                    details={
                        "required_tickets": REFERRAL_QUOTA_RESET_TICKET_COST,
                        "current_tickets": locked_user.ticket_amount,
                        "message": f"추천 횟수 초기화에는 {REFERRAL_QUOTA_RESET_TICKET_COST}개의 티켓이 필요합니다.",
                    },
                )

            # 티켓 차감
            locked_user.ticket_amount -= REFERRAL_QUOTA_RESET_TICKET_COST
            locked_user.used_ticket_amount += REFERRAL_QUOTA_RESET_TICKET_COST

            # 추천 횟수 초기화
            locked_user.remaining_referral_quota = REFERRAL_QUOTA_MAX
            locked_user.last_exhausted_referral_quota_at = None

            locked_user.save(
                update_fields=[
                    "ticket_amount",
                    "used_ticket_amount",
                    "remaining_referral_quota",
                    "last_exhausted_referral_quota_at",
                ]
            )

            TicketLog.objects.create(
                user=locked_user,
                amount=-REFERRAL_QUOTA_RESET_TICKET_COST,
                category=TicketLogCategory.USE,
                description="추천 횟수 초기화",
            )

            logger.info(
                "Referral quota reset successfully",
                user_id=user.id,
                ticket_cost=REFERRAL_QUOTA_RESET_TICKET_COST,
                new_quota=REFERRAL_QUOTA_MAX,
            )

            user = locked_user
            return user

        except ValidationError:
            raise
        except Exception as e:
            logger.error(
                "Failed to reset referral quota",
                exception=e,
                user_id=user.id,
            )
            raise
