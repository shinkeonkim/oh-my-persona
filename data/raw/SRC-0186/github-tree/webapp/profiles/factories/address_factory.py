"""
Address Factory 클래스
"""

import factory
from factory.django import DjangoModelFactory

from profiles.models import Address


class AddressFactory(DjangoModelFactory):
    """Address Factory"""

    class Meta:
        model = Address

    region = "서울특별시"
    city = "강남구"

    class Params:
        # 트레이트: 서울
        seoul = factory.Trait(
            region="서울특별시",
            city=factory.Faker("random_element", elements=["강남구", "서초구", "송파구", "강동구"]),
        )

        # 트레이트: 경기도
        gyeonggi = factory.Trait(
            region="경기도",
            city=factory.Faker("random_element", elements=["수원시", "성남시", "용인시", "안양시"]),
        )

        # 트레이트: 부산
        busan = factory.Trait(
            region="부산광역시",
            city=factory.Faker("random_element", elements=["해운대구", "부산진구", "동래구", "남구"]),
        )

        # 트레이트: 인천
        incheon = factory.Trait(
            region="인천광역시",
            city=factory.Faker("random_element", elements=["남동구", "부평구", "서구", "연수구"]),
        )

        # 트레이트: 대구
        daegu = factory.Trait(
            region="대구광역시",
            city=factory.Faker("random_element", elements=["중구", "동구", "서구", "남구"]),
        )

        # 트레이트: 대전
        daejeon = factory.Trait(
            region="대전광역시",
            city=factory.Faker("random_element", elements=["유성구", "서구", "동구", "중구"]),
        )
