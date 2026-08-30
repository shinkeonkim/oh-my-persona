"""LangChain을 사용하는 LLM Provider"""

from typing import Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from django.conf import settings
from common.utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_LLM_PROVIDER = settings.DEFAULT_LLM_PROVIDER
OPENAPI_KEY = settings.OPENAI_API_KEY
ANTHROPIC_API_KEY = settings.ANTHROPIC_API_KEY


class LangChainProvider:
    """
    LangChain을 사용하는 통합 LLM Provider

    OpenAI와 Anthropic을 지원하며 설정에 따라 자동으로 선택됩니다.
    """

    PROVIDER_OPENAI = "openai"
    PROVIDER_ANTHROPIC = "anthropic"

    def __init__(
        self,
        provider: str = DEFAULT_LLM_PROVIDER,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ):
        """
        Args:
            provider: 사용할 provider ("openai" 또는 "anthropic")
            model: 사용할 모델 이름 (None일 경우 기본 모델 사용)
            temperature: 생성 온도 (0.0 ~ 1.0)
            max_tokens: 최대 토큰 수
            api_key: API 키 (None일 경우 환경변수에서 가져옴)
        """
        self.provider = provider
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = self._get_api_key(provider)

        # 모델 설정
        if model:
            self.model = model
        else:
            self.model = self._get_default_model(provider)

        # LLM 인스턴스 생성
        self.llm = self._create_llm()
    
    @staticmethod
    def _get_api_key(provider: str) -> Optional[str]:
        """API 키 반환"""
        if provider == LangChainProvider.PROVIDER_ANTHROPIC:
            return ANTHROPIC_API_KEY
        return OPENAPI_KEY

    @staticmethod
    def _get_default_model(provider: str) -> str:
        """기본 모델 반환"""
        if provider == LangChainProvider.PROVIDER_ANTHROPIC:
            return "claude-haiku-4-5-20251001"
        return "gpt-4.1-mini"

    def _create_llm(self):
        """LangChain LLM 인스턴스 생성"""
        kwargs = {
            "model": self.model,
            "temperature": self.temperature,
        }

        if self.max_tokens:
            kwargs["max_tokens"] = self.max_tokens

        if self.api_key:
            kwargs["api_key"] = self.api_key

        try:
            if self.provider == self.PROVIDER_ANTHROPIC:
                return ChatAnthropic(**kwargs)
            else:
                return ChatOpenAI(**kwargs)
        except Exception as e:
            logger.error(
                "Failed to create LLM instance",
                provider=self.provider,
                model=self.model,
                exception=e,
            )
            raise

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        텍스트를 생성합니다.

        Args:
            system_prompt: 시스템 프롬프트
            user_prompt: 사용자 프롬프트

        Returns:
            생성된 텍스트
        """
        try:
            # 프롬프트 템플릿 생성
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("user", user_prompt),
            ])

            # 체인 생성 및 실행
            chain = prompt | self.llm
            response = chain.invoke({})

            content = response.content.strip()

            logger.info(
                "Text generation successful",
                provider=self.provider,
                model=self.model,
                prompt_length=len(user_prompt),
                response_length=len(content),
            )

            return content

        except Exception as e:
            logger.error(
                "Text generation failed",
                provider=self.provider,
                model=self.model,
                exception=e,
            )
            raise

    def generate_with_parser(self, system_prompt: str, user_prompt: str, parser: PydanticOutputParser) -> dict:
        """
        Pydantic parser를 사용하여 구조화된 출력을 생성합니다.

        Args:
            system_prompt: 시스템 프롬프트
            user_prompt: 사용자 프롬프트
            parser: Pydantic output parser

        Returns:
            파싱된 딕셔너리
        """
        try:
            # 포맷 지시사항을 user_prompt에 추가
            format_instructions = parser.get_format_instructions()
            enhanced_user_prompt = f"{user_prompt}\n\n{format_instructions}"

            # 메시지 직접 생성 (템플릿 변수 파싱 회피)
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=enhanced_user_prompt),
            ]

            # 체인 생성 및 실행
            chain = self.llm | parser
            result = chain.invoke(messages)

            logger.info(
                "Structured generation successful",
                provider=self.provider,
                model=self.model,
            )

            return result.dict()

        except Exception as e:
            logger.error(
                "Structured generation failed",
                provider=self.provider,
                model=self.model,
                exception=e,
            )
            raise
