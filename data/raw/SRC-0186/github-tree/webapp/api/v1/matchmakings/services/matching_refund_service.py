from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction

from common.utils.logger import get_logger
from matchmakings.models import Matching
from users.models import TicketLog, TicketLogCategory
from users.services import TicketService

User = get_user_model()

logger = get_logger(__name__)

MATCHING_REFUND_TICKET_AMOUNT = settings.MATCHING_REFUND_TICKET_AMOUNT


class MatchingRefundService:
    """매칭 환불 서비스"""

    @staticmethod
    @transaction.atomic
    def refund_matching_ticket(matching: Matching):
        """매칭 만료 시 티켓 환불"""
        try:
            # 이미 환불된 경우 방지 (TicketLog 확인)
            existing_refund = TicketLog.objects.filter(
                user=matching.sender,
                category=TicketLogCategory.REFUND,
                matching=matching,
            ).exists()

            if existing_refund:
                logger.warning(
                    "Refund already processed for matching",
                    matching_id=matching.id,
                    sender_id=matching.sender.id,
                )
                return False

            ticket_service = TicketService(matching.sender)
            # 발신자에게 티켓 환불
            ticket_service.refund_tickets(
                amount=MATCHING_REFUND_TICKET_AMOUNT,
                matching=matching,
                description=f"매칭 자동 거절로 인한 환불 (매칭 ID: {matching.id})",
            )

            return True

        except Exception as e:
            logger.error(
                "Failed to refund matching ticket",
                exception=e,
                matching_id=matching.id,
            )
            raise
