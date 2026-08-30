from .matching_action_service import MatchingActionService
from .matching_creation_service import MatchingCreationService
from .matching_query_service import MatchingQueryService


class MatchingService:
    """매칭 관련 비즈니스 로직 서비스"""

    @staticmethod
    def get_sent_matchings(user):
        """사용자가 보낸 호감 목록 조회"""
        return MatchingQueryService.get_sent_matchings(user)

    @staticmethod
    def get_received_matchings(user):
        """사용자가 받은 호감 목록 조회"""
        return MatchingQueryService.get_received_matchings(user)

    @staticmethod
    def get_completed_matchings(user):
        """매칭 완료 목록 조회"""
        return MatchingQueryService.get_completed_matchings(user)

    @staticmethod
    def get_past_connections(user):
        """지난 인연 목록 조회"""
        return MatchingQueryService.get_past_connections(user)

    @staticmethod
    def process_matching_action(matching, action):
        """매칭 액션 처리 (승인/거부)"""
        return MatchingActionService.process_matching_action(matching, action)

    @staticmethod
    def create_matching_from_referral(user, referral_id, ticket_amount=None):
        """추천으로부터 매칭 생성"""
        return MatchingCreationService.create_matching_from_referral(user, referral_id, ticket_amount)

    @staticmethod
    def check_ticket_availability(user, ticket_amount=None):
        """사용자의 티켓 보유량 확인"""
        return MatchingCreationService.check_ticket_availability(user, ticket_amount)

    @staticmethod
    def get_required_ticket_amount():
        """매칭 생성에 필요한 티켓 수량 반환"""
        return MatchingCreationService.get_required_ticket_amount()
