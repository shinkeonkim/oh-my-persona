"""
직업 Factory 클래스
"""

import factory
from factory.django import DjangoModelFactory

from profiles.models import Job

from .job_category_factory import JobCategoryFactory


class JobFactory(DjangoModelFactory):
    """직업 Factory"""

    class Meta:
        model = Job

    name = factory.Faker("job")
    job_category = factory.SubFactory(JobCategoryFactory)
