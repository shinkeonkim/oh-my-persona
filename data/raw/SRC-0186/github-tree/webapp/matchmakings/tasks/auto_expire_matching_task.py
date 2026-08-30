from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from celery import shared_task

from api.v1.matchmakings.services import MatchingRefundService
from common.utils.logger import get_logger
from matchmakings.models import Matching

logger = get_logger(__name__)

MATCHING_AUTO_REJECT_DAYS = settings.MATCHING_AUTO_REJECT_DAYS


@shared_task
def auto_expire_matching_task():
    """
    1주일이 지난 미수락 호감을 자동으로 거절하고 티켓을 환불하는 태스크
    """
    try:
        # 1주일 전 시간 계산
        expiry_time = timezone.now() - timedelta(days=MATCHING_AUTO_REJECT_DAYS)

        # 자동 거절 대상: 보낸지 1주일이 지났는데 received_at, rejected_at 모두 NULL인 경우
        expired_matchings = Matching.objects.filter(
            sent_at__lte=expiry_time, received_at__isnull=True, rejected_at__isnull=True
        ).select_related("sender", "receiver").iterator()

        auto_rejected_count = 0
        refunded_count = 0

        for matching in expired_matchings:
            try:
                with transaction.atomic():
                    # 매칭을 만료 상태로 변경
                    matching.expire()
                    auto_rejected_count += 1

                    # 티켓 환불
                    refund_success = MatchingRefundService.refund_matching_ticket(matching)

                    if refund_success:
                        refunded_count += 1

                    logger.info(
                        "Auto-Expire matching",
                        matching_id=matching.id,
                        sender_id=matching.sender.id,
                        receiver_id=matching.receiver.id,
                        sent_at=matching.sent_at,
                        refunded=refund_success,
                    )

            except Exception as e:
                logger.error(
                    "Failed to auto-reject matching",
                    exception=e,
                    matching_id=matching.id,
                )
                continue

        result_message = f"Auto-Expire {auto_rejected_count} matchings, " f"refunded {refunded_count} tickets"

        logger.info(result_message)
        return result_message

    except Exception as e:
        error_message = f"Error in auto_expire_matchings task: {str(e)}"
        logger.error(error_message, exception=e)
        return error_message
