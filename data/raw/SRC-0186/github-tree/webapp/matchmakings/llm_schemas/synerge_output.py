"""LLM 응답을 위한 Pydantic 스키마"""

from pydantic import BaseModel, Field


class SynergyItem(BaseModel):
  """천생연분 시너지 항목"""
  title: str = Field(description="시너지 제목 (10-20자, 운명적이고 매력적인 표현)")
  description: str = Field(description="시너지 설명 (2-3문단, 약 200-300자, 사주 분석 기반의 구체적인 설명)")


class SynergyOutput(BaseModel):
  """천생연분 시너지 출력 스키마"""
  content: list[SynergyItem] = Field(
    description="천생연분 시너지 항목 목록 (3개)",
    min_length=3,
    max_length=3,
  )
