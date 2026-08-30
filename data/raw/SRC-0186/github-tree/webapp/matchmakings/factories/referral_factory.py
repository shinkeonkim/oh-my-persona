"""
Referral Factory 클래스
"""

from django.utils import timezone

import factory
from factory.django import DjangoModelFactory

from matchmakings.models import Referral
from users.factories import UserFactory


class ReferralFactory(DjangoModelFactory):
    """Referral Factory"""

    class Meta:
        model = Referral

    user = factory.SubFactory(
        UserFactory,
        confirm_user=True,
    )
    referral_user = factory.SubFactory(
        UserFactory,
        confirm_user=True,
    )
    referred_at = factory.LazyFunction(timezone.now)
    referred_algorithm = "DefaultAlgorithm"

    class Params:
        # 트레이트: 알고리즘 A
        algorithm_a = factory.Trait(
            referred_algorithm="AlgorithmA",
        )

        # 트레이트: 알고리즘 B
        algorithm_b = factory.Trait(
            referred_algorithm="AlgorithmB",
        )

        # 트레이트: 알고리즘 C
        algorithm_c = factory.Trait(
            referred_algorithm="AlgorithmC",
        )

        # 트레이트: 오래된 추천
        old = factory.Trait(
            referred_at=factory.LazyFunction(lambda: timezone.now() - timezone.timedelta(days=10)),
        )

        # 트레이트: 최근 추천
        recent = factory.Trait(
            referred_at=factory.LazyFunction(lambda: timezone.now() - timezone.timedelta(hours=1)),
        )

        # 트레이트: 아주 오래된 추천
        very_old = factory.Trait(
            referred_at=factory.LazyFunction(lambda: timezone.now() - timezone.timedelta(days=30)),
        )
