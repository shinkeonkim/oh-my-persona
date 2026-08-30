"""추천 천생연분 시너지 생성 Celery 태스크"""

from django.db import transaction

from celery import shared_task

from common.utils.logger import get_logger
from matchmakings.choices import GenerationStatusChoice
from matchmakings.models import Referral, ReferralSynergy
from matchmakings.services import SynergyService

logger = get_logger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_synergy(self, referral_id: int):
  """
    추천에 대한 천생연분 시너지 정보 3개를 생성합니다.

    Args:
        referral_id: Referral ID
    """
  try:
    referral = Referral.objects.select_related('user__profile', 'referral_user__profile').get(id=referral_id)

    # Referral의 synergy_generation_status 확인
    if referral.synergy_generation_status in [
        GenerationStatusChoice.GENERATING,
        GenerationStatusChoice.COMPLETED,
    ]:
      logger.info(
        "Synergy already generated or generating",
        referral_id=referral.id,
        status=referral.synergy_generation_status,
      )
      return

    # 상태를 생성 중으로 변경
    referral.synergy_generation_status = GenerationStatusChoice.GENERATING
    referral.save(update_fields=['synergy_generation_status', 'updated_at'])

    if referral.user.profile.gender == "M":
      male_user_profile = referral.user.profile
      female_user_profile = referral.referral_user.profile
    else:
      male_user_profile = referral.referral_user.profile
      female_user_profile = referral.user.profile

    # SynergyService를 사용하여 시너지 생성 (3번)
    synergy_service = SynergyService(male_user_profile=male_user_profile, female_user_profile=female_user_profile)

    # 3개의 시너지 생성
    contents = synergy_service.generate()

    with transaction.atomic():
      for content in contents[:3]:
        title = content["title"].strip()
        description = content["description"].strip()

        # ReferralSynergy 생성
        ReferralSynergy.objects.create(
          referral=referral,
          title=title,
          description=description,
          generation_status=GenerationStatusChoice.COMPLETED,
        )

      # Referral의 생성 상태를 완료로 변경
      referral.synergy_generation_status = GenerationStatusChoice.COMPLETED
      referral.save(update_fields=['synergy_generation_status', 'updated_at'])

    logger.info(
      "Synergies generated successfully",
      referral_id=referral.id,
    )
  except Referral.DoesNotExist:
    logger.error(
      "Referral not found for synergy generation",
      referral_id=referral_id,
    )
  except Exception as e:
    logger.error(
      "Failed to generate synergy",
      referral_id=referral_id,
      exception=e,
    )

    # 에러 상태로 업데이트
    try:
      referral = Referral.objects.get(id=referral_id)
      referral.synergy_generation_status = GenerationStatusChoice.FAILED
      referral.save(update_fields=['synergy_generation_status', 'updated_at'])
    except Exception:
      pass

    # Retry the task
    raise self.retry(exc=e, countdown=60)
