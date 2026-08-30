from .referral_creation_service import ReferralCreationService
from .referral_query_service import ReferralQueryService


class ReferralService:
    """추천 관련 비즈니스 로직 서비스 (Facade)"""

    @staticmethod
    def create_referral(user, algorithm_type):
        """새로운 추천 생성"""
        return ReferralCreationService.create_referral(user, algorithm_type)

    @staticmethod
    def get_latest_referral(user, algorithm_type=None):
        """가장 최근 추천 조회"""
        return ReferralQueryService.get_latest_referral(user, algorithm_type)
