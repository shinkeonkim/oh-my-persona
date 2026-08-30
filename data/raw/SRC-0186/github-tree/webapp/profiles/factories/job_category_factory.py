"""
직업 카테고리 Factory 클래스
"""

import factory
from factory.django import DjangoModelFactory

from profiles.models import JobCategory


class JobCategoryFactory(DjangoModelFactory):
    """직업 카테고리 Factory"""

    class Meta:
        model = JobCategory

    name = factory.Faker("job")
