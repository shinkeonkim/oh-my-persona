"""
PreMatchingScore Factory 클래스
"""

import factory
from factory.django import DjangoModelFactory

from matchmakings.models import PreMatchingScore

from .pre_matching_factory import PreMatchingFactory


class PreMatchingScoreFactory(DjangoModelFactory):
    """PreMatchingScore Factory"""

    class Meta:
        model = PreMatchingScore

    prematching = factory.SubFactory(PreMatchingFactory)
    algorithm_category = "DefaultAlgorithm"
    score = 75

    class Params:
        # 트레이트: 높은 점수
        high_score = factory.Trait(
            score=factory.Faker("random_int", min=90, max=100),
        )

        # 트레이트: 중간 점수
        medium_score = factory.Trait(
            score=factory.Faker("random_int", min=60, max=89),
        )

        # 트레이트: 낮은 점수
        low_score = factory.Trait(
            score=factory.Faker("random_int", min=30, max=59),
        )

        # 트레이트: 아주 낮은 점수
        very_low_score = factory.Trait(
            score=factory.Faker("random_int", min=0, max=29),
        )

        # 트레이트: 알고리즘 A
        algorithm_a = factory.Trait(
            algorithm_category="AlgorithmA",
        )

        # 트레이트: 알고리즘 B
        algorithm_b = factory.Trait(
            algorithm_category="AlgorithmB",
        )

        # 트레이트: 알고리즘 C
        algorithm_c = factory.Trait(
            algorithm_category="AlgorithmC",
        )

        # 트레이트: 완벽한 점수
        perfect_score = factory.Trait(
            score=100,
        )

        # 트레이트: 최저 점수
        zero_score = factory.Trait(
            score=0,
        )
