"""천생연분 시너지 생성 서비스"""

from typing import Optional

from common.utils.logger import get_logger
from matchmakings.llm_providers.langchain_provider import LangChainProvider
from matchmakings.llm_schemas import SynergyOutput
from matchmakings.prompts import SynergyPrompt

from .llm_message_creation_service import LLMMessageCreationService

logger = get_logger(__name__)


class SynergyService(LLMMessageCreationService):
  """천생연분 시너지를 생성하는 서비스"""

  def __init__(self, male_user_profile, female_user_profile, llm_provider: Optional[LangChainProvider] = None):
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
    return SynergyPrompt.SYSTEM_PROMPT

  def _get_user_prompt(self) -> str:
    """사용자 프롬프트 반환"""
    return SynergyPrompt.get_synergy_prompt(male_user_data=self._get_user_data(profile=self.male_user_profile),
                                            female_user_data=self._get_user_data(profile=self.female_user_profile))

  @staticmethod
  def _get_pydantic_output_model() -> type:
    """Pydantic 출력 모델 반환"""
    return SynergyOutput

  def generate(self) -> tuple[str, str]:
    """
        천생연분 시너지를 생성합니다.

        Returns:
            생성된 시너지 설명

        Raises:
            Exception: LLM 호출 실패 시
        """
    try:
      # 프롬프트 생성
      result = self.generate_llm_response()
      contents = result["content"]
      return contents

    except Exception as e:
      logger.error(
        "Synergy generation failed",
        male_user_profile_id=self.male_user_profile.id,
        female_user_profile_id=self.female_user_profile.id,
        exception=e,
      )
      raise
