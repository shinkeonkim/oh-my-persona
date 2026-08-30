from django.db.models.signals import post_save
from django.dispatch import receiver

from common.utils.logger import get_logger
from matchmakings.models import Referral, ReferralLog

logger = get_logger(__name__)


@receiver(post_save, sender=Referral)
def create_referral_log(sender, instance, created, **kwargs):
  """Referral이 생성될 때 ReferralLog를 자동으로 생성합니다."""
  if created:
    try:
      ReferralLog.objects.create(
        referral=instance,
        user=instance.user,
        referral_user=instance.referral_user,
        referred_at=instance.referred_at,
        referred_algorithm=instance.referred_algorithm,
      )
      logger.info(
        "Created ReferralLog for Referral",
        referral_id=instance.id,
        user_id=instance.user.id,
        referral_user_id=instance.referral_user.id,
      )
    except Exception as e:
      logger.error(
        "Failed to create ReferralLog for Referral",
        exception=e,
        referral_id=instance.id,
      )
