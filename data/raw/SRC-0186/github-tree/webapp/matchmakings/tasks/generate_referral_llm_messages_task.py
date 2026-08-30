"""추천 인사이트 생성을 위한 메인 Celery 태스크"""

from celery import shared_task

from common.utils.logger import get_logger
from matchmakings.models import Referral
from .generate_overall_opinion_task import generate_overall_opinion
from .generate_synergy_task import generate_synergy

logger = get_logger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_referral_llm_messages(self, referral_id: int):
    """
    추천에 대한 종합의견과 시너지 정보를 비동기로 생성합니다.

    Args:
        referral: Referral 객체
    """
    try:
        referral = Referral.objects.select_related(
            'user__profile',
            'referral_user__profile'
        ).get(id=referral_id)

        # 두 작업을 병렬로 실행
        generate_overall_opinion.delay(referral.id)
        generate_synergy.delay(referral.id)

        logger.info(
            "Triggered referral insight generation tasks",
            referral_id=referral_id,
        )

    except Referral.DoesNotExist:
        logger.error(
            "Referral not found for insight generation",
            referral_id=referral_id,
        )
    except Exception as e:
        logger.error(
            "Failed to trigger referral insight generation",
            referral_id=referral_id,
            exception=e,
        )
        # Retry the task
        raise self.retry(exc=e, countdown=60)
