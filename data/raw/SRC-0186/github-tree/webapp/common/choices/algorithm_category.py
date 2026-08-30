from django.conf import settings
from django.db import models


class AlgorithmCategory(models.TextChoices):
    """알고리즘 카테고리 선택지"""

    @classmethod
    def get_choices(cls):
        """동적으로 알고리즘 선택지를 반환"""
        algorithm_names = getattr(settings, "MATCHING_ALGORITHM_NAMES", [])
        return [(key, key) for key in algorithm_names]

    @classmethod
    def get_labels(cls):
        """알고리즘 라벨 목록을 반환"""
        return [key for key, _ in cls.get_choices()]

    @classmethod
    def get_values(cls):
        """알고리즘 값 목록을 반환"""
        return [key for key, _ in cls.get_choices()]

    @classmethod
    def get_default(cls):
        """기본 알고리즘을 반환"""
        algorithm_names = getattr(settings, "MATCHING_ALGORITHM_NAMES", [])
        return algorithm_names[0] if algorithm_names else None
