"""
직업 정보 Factory 클래스들
"""

import factory
from factory.django import DjangoModelFactory

from profiles.models import JobInfo

from .job_factory import JobFactory


class JobInfoFactory(DjangoModelFactory):
    """직업 정보 Factory"""

    class Meta:
        model = JobInfo

    job = factory.SubFactory(JobFactory)
    job_category = factory.SelfAttribute("job.job_category")
    manual_job = ""
    manual_job_category = ""
