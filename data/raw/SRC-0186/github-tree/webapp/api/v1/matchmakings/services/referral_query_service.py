from django.db.models import Exists, OuterRef

from api.v1.matchmakings.exceptions import ReferralNotFoundError
from common.utils.logger import get_logger
from matchmakings.models import PreMatching, Referral

logger = get_logger(__name__)


class ReferralQueryService:
    """추천 조회 관련 서비스"""

    @staticmethod
    def get_latest_referral(user, algorithm_type=None):
        """사용자가 받은 가장 최근 추천 조회 (알고리즘 타입 필터링 가능)"""
        try:
            query = Referral.objects.filter(user=user)

            # 알고리즘 타입이 지정된 경우 필터링
            if algorithm_type:
                # PreMatchingScore를 통해 알고리즘 타입으로 필터링
                query = query.filter(
                    Exists(
                        PreMatching.objects.filter(
                            male_user=OuterRef("referral_user"),
                            female_user=user,
                            pre_matching_scores__algorithm_category=algorithm_type,
                        )
                    )
                    | Exists(
                        PreMatching.objects.filter(
                            male_user=user,
                            female_user=OuterRef("referral_user"),
                            pre_matching_scores__algorithm_category=algorithm_type,
                        )
                    )
                )

            latest_referral = query.select_related("referral_user__profile__job_info").order_by("-referred_at").first()

            if not latest_referral:
                raise ReferralNotFoundError(
                    message="No referrals found",
                    details={"user_id": user.id, "algorithm_type": algorithm_type},
                )

            return latest_referral
        except ReferralNotFoundError:
            # 이미 처리된 예외는 그대로 전파
            raise
        except Exception as e:
            logger.error(
                "Failed to fetch latest referral",
                exception=e,
                user_id=user.id,
                algorithm_type=algorithm_type,
            )
            raise
