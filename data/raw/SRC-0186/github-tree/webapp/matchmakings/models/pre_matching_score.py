from django.conf import settings
from django.db import models

from common.models import BaseModel
from matchmakings.models.pre_matching import PreMatching


def get_algorithm_choices():
    """알고리즘 선택지를 동적으로 반환"""
    algorithm_names = getattr(settings, "MATCHING_ALGORITHM_NAMES", [])
    return [(key, key) for key in algorithm_names]


def get_default_algorithm():
    """기본 알고리즘을 반환"""
    algorithm_names = getattr(settings, "MATCHING_ALGORITHM_NAMES", [])
    return algorithm_names[0] if algorithm_names else None


class PreMatchingScore(BaseModel):
    class Meta:
        db_table = "pre_matching_scores"
        verbose_name = "Pre Matching Score"
        verbose_name_plural = "Pre Matching Scores"
        unique_together = [["prematching", "algorithm_category"]]

    score = models.IntegerField(default=0)
    prematching = models.ForeignKey(PreMatching, on_delete=models.CASCADE, related_name="pre_matching_scores")
    algorithm_category = models.CharField(
        max_length=20,
        choices=get_algorithm_choices,
        default=get_default_algorithm,
    )
