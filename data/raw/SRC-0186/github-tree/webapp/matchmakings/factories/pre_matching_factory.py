"""
PreMatching Factory 클래스
"""

from django.utils import timezone

import factory
from factory.django import DjangoModelFactory

from matchmakings.models import PreMatching, PreMatchingStatus
from users.factories import UserFactory


class PreMatchingFactory(DjangoModelFactory):
    """PreMatching Factory"""

    class Meta:
        model = PreMatching

    male_user = factory.SubFactory(
        UserFactory,
        confirm_user=True,
    )
    female_user = factory.SubFactory(
        UserFactory,
        confirm_user=True,
    )
    status = PreMatchingStatus.PENDING
    matching_reason = None
    last_calculated_at = None
    compatibility_score = 0

    class Params:
        # 트레이트: PENDING 상태
        pending = factory.Trait(
            status=PreMatchingStatus.PENDING,
        )

        # 트레이트: CALCULATING 상태
        calculating = factory.Trait(
            status=PreMatchingStatus.CALCULATING,
        )

        # 트레이트: COMPLETED 상태
        completed = factory.Trait(
            status=PreMatchingStatus.COMPLETED,
            last_calculated_at=factory.LazyFunction(timezone.now),
        )

        # 트레이트: RECOMMENDED 상태
        recommended = factory.Trait(
            status=PreMatchingStatus.RECOMMENDED,
            last_calculated_at=factory.LazyFunction(timezone.now),
        )

        # 트레이트: 높은 궁합 점수
        high_compatibility = factory.Trait(
            compatibility_score=95,
            matching_reason="두 사람은 매우 잘 어울립니다.",
        )

        # 트레이트: 중간 궁합 점수
        medium_compatibility = factory.Trait(
            compatibility_score=70,
            matching_reason="두 사람은 어느 정도 잘 맞습니다.",
        )

        # 트레이트: 낮은 궁합 점수
        low_compatibility = factory.Trait(
            compatibility_score=40,
            matching_reason="두 사람은 노력이 필요합니다.",
        )

        # 트레이트: 최근 계산됨
        recently_calculated = factory.Trait(
            last_calculated_at=factory.LazyFunction(lambda: timezone.now() - timezone.timedelta(minutes=5)),
        )

        # 트레이트: 오래전 계산됨
        old_calculation = factory.Trait(
            last_calculated_at=factory.LazyFunction(lambda: timezone.now() - timezone.timedelta(days=7)),
        )
