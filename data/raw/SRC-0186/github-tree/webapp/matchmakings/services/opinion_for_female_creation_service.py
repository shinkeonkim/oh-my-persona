from common.utils.logger import get_logger
from matchmakings.prompts import OverallOpinionPrompt
from .opinion_creation_service import OpinionCreationService

logger = get_logger(__name__)


class OpinionForFemaleCreationService(OpinionCreationService):
    """여자에게 보여줄 종합의견을 생성하는 서비스"""
    def _get_user_prompt(self) -> str:
        """사용자 프롬프트 반환"""
        return OverallOpinionPrompt.get_female_opinion_prompt(
            user_data=self._get_user_data(self.female_user_profile),
            referral_user_data=self._get_user_data(self.male_user_profile),
        )
