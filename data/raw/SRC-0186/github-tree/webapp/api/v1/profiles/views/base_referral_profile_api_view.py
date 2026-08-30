from django.db.models import Q

from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from api.v1.matchmakings.exceptions import ReferralNotFoundError
from common.utils.logger import get_logger
from matchmakings.models import Referral
from profiles.models import Profile

from .base_profile_api_view import BaseProfileAPIView

logger = get_logger(__name__)


class BaseReferralProfileAPIView(BaseProfileAPIView):
  """Referral 기반 프로필 API 뷰"""

  permission_classes = [IsAuthenticated]

  def get_latest_referral(self, profile_id):
    referral_user_profile = get_object_or_404(Profile, id=profile_id)

    latest_referral = Referral.objects.filter(
      Q(user=self.current_user, referral_user=referral_user_profile.user)
      | Q(user=referral_user_profile.user, referral_user=self.current_user)).order_by("-referred_at").first()

    if not latest_referral:
      raise ReferralNotFoundError()

    return latest_referral
