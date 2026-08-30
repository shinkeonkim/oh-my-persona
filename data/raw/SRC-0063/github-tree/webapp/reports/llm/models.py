"""Pydantic models for LLM response parsing."""

from typing import List

from pydantic import BaseModel, Field


class AdviceItem(BaseModel):
    """Single advice item with title and description."""

    title: str = Field(..., description="조언 제목 (30글자 이내)")
    description: str = Field(..., description="조언 설명 (2문장 이내)")


class GameReportAdviceResponse(BaseModel):
    """Response model for game report advice."""

    analysis: List[AdviceItem] = Field(
        ...,
        description="분석 결과 및 조언 리스트",
        min_length=2,
        max_length=2,
    )
