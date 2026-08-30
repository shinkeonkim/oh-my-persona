from typing import Optional

from common.utils.logger import get_logger
from matchmakings.llm_providers.langchain_provider import LangChainProvider
from matchmakings.prompts import OverallOpinionPrompt
from matchmakings.llm_schemas import OverallOpinionOutput
from .llm_message_creation_service import LLMMessageCreationService

logger = get_logger(__name__)

class OpinionCreationService(LLMMessageCreationService):
    """종합 의견 생성 서비스의 추상 클래스"""

    def __init__(self, male_user_profile, female_user_profile, llm_provider : Optional[LangChainProvider] = None):
        """
        Args:
            llm_provider: 사용할 LLM Provider (None일 경우 기본 provider 사용)
        """
        self.llm_provider = llm_provider or self._get_default_provider()
        self.male_user_profile = male_user_profile
        self.female_user_profile = female_user_profile

    @staticmethod
    def _get_system_prompt() -> str:
        """시스템 프롬프트 반환"""
        return OverallOpinionPrompt.SYSTEM_PROMPT
    
    @staticmethod
    def _get_pydantic_output_model() -> type:
        """Pydantic 출력 모델 반환"""
        return OverallOpinionOutput

    def generate(self) -> str:
        """
        종합의견을 생성합니다.

        Returns:
            생성된 종합의견

        Raises:
            Exception: LLM 호출 실패 시
        """
        try:
            # 프롬프트 생성
            result = self.generate_llm_response()
            opinion = result["content"]
            return opinion.strip()
    
        except Exception as e:
            logger.error(
                "Opinion generation failed",
                male_user_profile_id=self.male_user_profile.id,
                female_user_profile_id=self.female_user_profile.id,
                exception=e,
            )
            raise
