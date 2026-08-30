import json
import time
from abc import ABC, abstractmethod
from typing import Optional

from django.conf import settings

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import ValidationError

from .models import GameReportAdviceResponse
from .prompt import get_bb_star_game_report_prompt, get_kids_traffic_game_report_prompt
from .provider import get_chat_model

LLM_PROVIDER = settings.LLM_PROVIDER


class ReportAdviceGenerator(ABC):
    def __init__(
        self,
        provider_name: Optional[str] = None,
        temperature: float = 0.7,
        max_retries: int = 5,
    ):
        """
        Args:
            provider_name: LLM provider name (ollama, openai, gemini)
            temperature: Sampling temperature
            max_retries: Maximum number of retries on failure
        """
        self.provider_name = provider_name or LLM_PROVIDER
        self.temperature = temperature
        self.max_retries = max_retries

        # LLM Chat 모델 초기화
        self.llm = get_chat_model(self.provider_name, self.temperature)

        # 프롬프트 및 파서 초기화
        self.prompt = self.get_prompt()
        self.parser = JsonOutputParser(pydantic_object=self.get_response_model())

        # 체인 생성
        self.chain = self.prompt | self.llm | self.parser

    def generate_advice(self, report_data: dict) -> list:
        """레포트 데이터를 기반으로 조언 생성 (Template Method)

        Args:
            report_data: 레포트 정보를 담은 딕셔너리

        Returns:
            생성된 조언 딕셔너리 리스트, 각 딕셔너리는 'title'과 'description' 키를 포함
        """
        for attempt in range(self.max_retries):
            try:
                payload = self._prepare_payload(report_data)

                # LLM 체인 실행
                result = self.chain.invoke(payload)

                # 응답 파싱 및 검증
                response = GameReportAdviceResponse(**result)

                return [{"title": item.title, "description": item.description} for item in response.analysis]

            except ValidationError as e:
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                raise ValueError(f"LLM 응답 검증 실패: {e}")

            except json.JSONDecodeError as e:
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                raise ValueError(f"LLM 응답 JSON 파싱 실패: {e}")

            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                raise ValueError(f"조언 생성 중 오류 발생: {e}")

        raise ValueError("최대 재시도 횟수 초과")

    @abstractmethod
    def _prepare_payload(self, report_data: dict) -> dict:
        """레포트 데이터를 LLM 체인에 전달할 payload로 변환

        Args:
            report_data: 레포트 정보를 담은 딕셔너리

        Returns:
            LLM 체인에 전달할 딕셔너리
        """
        pass

    @abstractmethod
    def get_prompt(self):
        """특정 레포트 유형에 대한 프롬프트 템플릿을 가져옵니다.

        Returns:
            ChatPromptTemplate 인스턴스
        """
        pass

    @abstractmethod
    def get_response_model(self):
        """LLM 응답을 파싱하기 위한 Pydantic 모델을 가져옵니다.

        Returns:
            Pydantic 모델 클래스
        """
        pass


class KidsTrafficGameReportAdviceGenerator(ReportAdviceGenerator):
    """꼬마 교통지킴이 게임 레포트 조언 생성기"""

    def get_prompt(self) -> ChatPromptTemplate:
        """꼬마 교통지킴이 게임 레포트에 대한 프롬프트 템플릿을 가져옵니다."""
        return get_kids_traffic_game_report_prompt()

    def get_response_model(self):
        """LLM 응답을 파싱하기 위한 Pydantic 모델을 가져옵니다."""
        return GameReportAdviceResponse

    def _prepare_payload(self, report_data: dict) -> dict:
        """
        꼬마 교통지킴이 게임 레포트 데이터를 LLM payload로 변환

        Args:
            report_data: 레포트 정보를 담은 딕셔너리, 다음 키 포함:
                - total_plays_count: 전체 플레이 횟수
                - total_play_rounds_count: 전체 플레이 라운드 수
                - max_rounds_count: 최대 라운드 도달 횟수
                - max_rounds_ratio: 최대 라운드 도달 비율
                - avg_rounds_count: 평균 도달 라운드
                - total_reaction_ms_avg: 평균 반응시간 (밀리초)
                - total_play_actions_count: 전체 플레이 액션 수
                - total_success_count: 전체 성공 횟수
                - total_wrong_count: 전체 오답 횟수
                - wrong_rate: 오답률 (%)
                - recent_trends: 최근 3개의 게임 결과 리스트

        Returns:
            LLM 체인에 전달할 딕셔너리
        """
        return {
            "total_plays_count": report_data.get("total_plays_count", 0),
            "total_play_rounds_count": report_data.get("total_play_rounds_count", 0),
            "max_rounds_count": report_data.get("max_rounds_count", 0),
            "max_rounds_ratio": report_data.get("max_rounds_ratio", 0),
            "avg_rounds_count": report_data.get("avg_rounds_count", 0),
            "total_reaction_ms_avg": report_data.get("total_reaction_ms_avg", 0),
            "total_play_actions_count": report_data.get("total_play_actions_count", 0),
            "total_success_count": report_data.get("total_success_count", 0),
            "total_wrong_count": report_data.get("total_wrong_count", 0),
            "wrong_rate": report_data.get("wrong_rate", 0),
            "recent_trends": report_data.get("recent_trends", []),
        }


class BBStarGameReportAdviceGenerator(ReportAdviceGenerator):
    """뿅뿅 아기별 게임 레포트 조언 생성기"""

    def get_prompt(self) -> ChatPromptTemplate:
        """뿅뿅 아기별 게임 레포트에 대한 프롬프트 템플릿을 가져옵니다."""
        return get_bb_star_game_report_prompt()

    def get_response_model(self):
        """LLM 응답을 파싱하기 위한 Pydantic 모델을 가져옵니다."""
        return GameReportAdviceResponse

    def _prepare_payload(self, report_data: dict) -> dict:
        """
        뿅뿅 아기별 게임 레포트 데이터를 LLM payload로 변환

        Args:
            report_data: 레포트 정보를 담은 딕셔너리, 다음 키 포함:
                - total_plays_count: 전체 플레이 횟수
                - total_play_rounds_count: 전체 플레이 라운드 수
                - max_rounds_count: 최대 라운드 도달 횟수
                - max_rounds_ratio: 최대 라운드 도달 비율
                - avg_rounds_count: 평균 도달 라운드
                - total_play_actions_count: 전체 플레이 액션 수
                - total_success_count: 전체 성공 횟수
                - total_wrong_count: 전체 오답 횟수
                - wrong_rate: 오답률 (%)
                - recent_trends: 최근 3개의 게임 결과 리스트

        Returns:
            LLM 체인에 전달할 딕셔너리
        """
        return {
            "total_plays_count": report_data.get("total_plays_count", 0),
            "total_play_rounds_count": report_data.get("total_play_rounds_count", 0),
            "max_rounds_count": report_data.get("max_rounds_count", 0),
            "max_rounds_ratio": report_data.get("max_rounds_ratio", 0),
            "avg_rounds_count": report_data.get("avg_rounds_count", 0),
            "total_play_actions_count": report_data.get("total_play_actions_count", 0),
            "total_success_count": report_data.get("total_success_count", 0),
            "total_wrong_count": report_data.get("total_wrong_count", 0),
            "wrong_rate": report_data.get("wrong_rate", 0),
            "recent_trends": report_data.get("recent_trends", []),
        }
