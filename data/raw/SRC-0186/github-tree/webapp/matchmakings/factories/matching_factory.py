"""
Matching Factory 클래스
"""

from django.utils import timezone

import factory
from factory.django import DjangoModelFactory

from common.choices import Gender
from matchmakings.models import Matching
from users.factories import UserFactory


class MatchingFactory(DjangoModelFactory):
    """Matching Factory"""

    class Meta:
        model = Matching

    sender = factory.SubFactory(
        UserFactory,
        confirm_user=True,
        confirm_user__profile_gender=Gender.MALE,
    )
    receiver = factory.SubFactory(
        UserFactory,
        confirm_user=True,
        confirm_user__profile_gender=Gender.FEMALE,
    )
    ticket_amount = 10
    sent_at = factory.LazyFunction(timezone.now)
    received_at = None
    rejected_at = None
    expired_at = None
    referral = None

    class Params:
        # 트레이트: 승인된 매칭
        accepted = factory.Trait(
            received_at=factory.LazyFunction(timezone.now),
            rejected_at=None,
        )

        # 트레이트: 거절된 매칭
        rejected = factory.Trait(
            received_at=None,
            rejected_at=factory.LazyFunction(timezone.now),
        )

        # 트레이트: 만료된 매칭
        expired = factory.Trait(
            expired_at=factory.LazyFunction(timezone.now),
        )

        # 트레이트: 보낸 상태 (기본)
        sent = factory.Trait(
            received_at=None,
            rejected_at=None,
            expired_at=None,
        )

        # 트레이트: 높은 티켓 수량
        high_ticket = factory.Trait(
            ticket_amount=50,
        )

        # 트레이트: 낮은 티켓 수량
        low_ticket = factory.Trait(
            ticket_amount=5,
        )

        # 트레이트: 오래된 매칭
        old = factory.Trait(
            sent_at=factory.LazyFunction(lambda: timezone.now() - timezone.timedelta(days=7)),
        )

        # 트레이트: 최근 매칭
        recent = factory.Trait(
            sent_at=factory.LazyFunction(lambda: timezone.now() - timezone.timedelta(hours=1)),
        )
