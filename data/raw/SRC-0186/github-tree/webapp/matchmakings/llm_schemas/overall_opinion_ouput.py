"""LLM 응답을 위한 Pydantic 스키마"""

from pydantic import BaseModel, Field


class OverallOpinionOutput(BaseModel):
  """중개인의 종합의견 출력 스키마"""

  content: str = Field(description="중개인의 종합의견 (약 200-300자, 사주 분석 기반의 구체적인 설명)")
