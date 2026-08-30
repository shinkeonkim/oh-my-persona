"""
프로필 Factory 클래스들
"""

import factory
from factory.django import DjangoModelFactory

from common.choices import BirthTime, Gender, Mbti
from profiles.models import Profile

from .job_info_factory import JobInfoFactory


class ProfileFactory(DjangoModelFactory):
    """프로필 Factory"""

    class Meta:
        model = Profile

    # user는 외부에서 주입받거나 기본값으로 생성
    user = factory.LazyFunction(lambda: None)  # 외부에서 user를 주입받아야 함

    mbti = factory.Faker("random_element", elements=[choice[0] for choice in Mbti.choices])
    gender = factory.Faker("random_element", elements=[choice[0] for choice in Gender.choices])
    region = factory.Faker("city")
    city = factory.Faker("city")
    birth_time = factory.Faker("random_element", elements=[choice[0] for choice in BirthTime.choices])
    introduction = factory.Faker("text", max_nb_chars=500)
    one_liner = factory.Faker("text", max_nb_chars=100)
    tmi = factory.Faker("text", max_nb_chars=300)
    job_info = factory.SubFactory(JobInfoFactory)
