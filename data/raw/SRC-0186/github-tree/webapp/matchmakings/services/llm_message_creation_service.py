from abc import ABC, abstractmethod
from typing import Optional

from langchain_core.output_parsers import PydanticOutputParser

from common.utils.logger import get_logger
from matchmakings.llm_providers.langchain_provider import LangChainProvider
from saju.services import UserSajuChartService

logger = get_logger(__name__)

class LLMMessageCreationService(ABC):
    """LLM을 활용한 메시지 생성 서비스의 추상 클래스"""

    def __init__(self, llm_provider: Optional[LangChainProvider] = None):
        """
        Args:
            llm_provider: 사용할 LLM Provider (None일 경우 기본 provider 사용)
        """
        self.llm_provider = llm_provider or self._get_default_provider()

    @staticmethod
    def _get_default_provider() -> LangChainProvider:
        """기본 LLM Provider 반환"""
        return LangChainProvider()
    
    @staticmethod
    @abstractmethod
    def _get_system_prompt() -> str:
        """시스템 프롬프트 반환"""
        pass

    @abstractmethod
    def _get_user_prompt(self) -> str:
        """사용자 프롬프트 반환"""
        pass

    @staticmethod
    def _get_user_data(profile) -> dict:
        """사용자 데이터를 LLM에 전달할 형식으로 준비"""
        saju_chart = UserSajuChartService(profile).get_saju_chart()

        return {
            "saju_chart": {
                "stems": saju_chart.stems,
                "branches": saju_chart.branches,
            },
            "profile": {
                "gender": profile.gender,
                "age": getattr(profile, 'age', None),
                "region": getattr(profile, 'region', None),
                "city": getattr(profile, 'city', None),
                "mbti": getattr(profile, 'mbti', None),
            }
        }

    @staticmethod
    @abstractmethod
    def _get_pydantic_output_model() -> type:
        """Pydantic 출력 모델 반환"""
        pass
    
    def generate_llm_response(self):
        """LLM 응답 생성"""
        system_prompt = self._get_system_prompt()
        user_prompt = self._get_user_prompt()
        pydantic_output_model = self._get_pydantic_output_model()
        parser = PydanticOutputParser(pydantic_object=pydantic_output_model)

        result = self.llm_provider.generate_with_parser(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            parser=parser,
        )
        return result

    @abstractmethod
    def generate(self) -> str:
        """결과물 생성"""
        pass
