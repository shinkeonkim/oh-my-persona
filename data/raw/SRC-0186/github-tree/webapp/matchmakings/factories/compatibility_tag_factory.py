"""
CompatibilityTag Factory 클래스
"""

import factory
from factory.django import DjangoModelFactory

from matchmakings.models import CompatibilityTag


class CompatibilityTagFactory(DjangoModelFactory):
    """CompatibilityTag Factory"""

    class Meta:
        model = CompatibilityTag

    name = factory.Sequence(lambda n: f"궁합태그{n}")

    class Params:
        # 트레이트: 성격 관련 태그
        personality = factory.Trait(
            name="성격이 잘 맞아요",
        )

        # 트레이트: 취미 관련 태그
        hobby = factory.Trait(
            name="취미가 비슷해요",
        )

        # 트레이트: 가치관 관련 태그
        values = factory.Trait(
            name="가치관이 비슷해요",
        )

        # 트레이트: 라이프스타일 관련 태그
        lifestyle = factory.Trait(
            name="라이프스타일이 비슷해요",
        )

        # 트레이트: 의사소통 관련 태그
        communication = factory.Trait(
            name="대화가 잘 통해요",
        )

        # 트레이트: 보완적 성격 태그
        complementary = factory.Trait(
            name="성격이 보완적이에요",
        )
