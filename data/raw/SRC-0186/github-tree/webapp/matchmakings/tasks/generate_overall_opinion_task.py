"""추천 종합의견 생성 Celery 태스크"""

from celery import shared_task

from common.utils.logger import get_logger
from matchmakings.choices import GenerationStatusChoice
from matchmakings.models import Referral, ReferralOverallOpinion
from matchmakings.services import (
  OpinionForFemaleCreationService,
  OpinionForMaleCreationService,
)

logger = get_logger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_overall_opinion(self, referral_id: int):
  """
    추천에 대한 중개인의 종합의견을 생성합니다.

    Args:
        referral: Referral 객체
    """
  try:
    referral = Referral.objects.select_related('user__profile', 'referral_user__profile').get(id=referral_id)

    # 종합의견 레코드 생성 또는 가져오기
    opinion, _ = ReferralOverallOpinion.objects.get_or_create(
      referral=referral, defaults={'generation_status': GenerationStatusChoice.PENDING})

    # 이미 생성 중이거나 완료된 경우 중복 실행 방지
    if opinion.generation_status in [GenerationStatusChoice.GENERATING, GenerationStatusChoice.COMPLETED]:
      logger.info(
        "Overall opinion already generated",
        referral_id=referral.id,
      )
      return

    # 상태를 생성 중으로 변경
    opinion.generation_status = GenerationStatusChoice.GENERATING
    opinion.save(update_fields=['generation_status', 'updated_at'])

    if referral.user.profile.gender == "M":
      male_user_profile = referral.user.profile
      female_user_profile = referral.referral_user.profile
    else:
      male_user_profile = referral.referral_user.profile
      female_user_profile = referral.user.profile

    # 분리된 서비스를 사용하여 종합의견 생성
    opinion_for_male_service = OpinionForMaleCreationService(male_user_profile=male_user_profile,
                                                             female_user_profile=female_user_profile)
    opinion_for_female_service = OpinionForFemaleCreationService(male_user_profile=male_user_profile,
                                                                 female_user_profile=female_user_profile)

    opinion_for_male = opinion_for_male_service.generate()
    opinion_for_female = opinion_for_female_service.generate()

    # 결과 저장
    opinion.opinion_for_male = opinion_for_male
    opinion.opinion_for_female = opinion_for_female
    opinion.generation_status = GenerationStatusChoice.COMPLETED
    opinion.save(update_fields=['opinion_for_male', 'opinion_for_female', 'generation_status', 'updated_at'])

    logger.info(
      "Overall opinion generated successfully",
      referral_id=referral.id,
    )
  except Referral.DoesNotExist:
    logger.error(
      "Referral not found for overall opinion generation",
      referral_id=referral.id,
    )
  except Exception as e:
    logger.error(
      "Failed to generate overall opinion",
      referral_id=referral.id,
      exception=e,
    )

    opinion = ReferralOverallOpinion.objects.filter(referral=referral).first()
    if opinion:
      opinion.generation_status = GenerationStatusChoice.FAILED
      opinion.error_message = str(e)
      opinion.save(update_fields=['generation_status', 'error_message', 'updated_at'])

    # Retry the task
    raise self.retry(exc=e, countdown=60)
