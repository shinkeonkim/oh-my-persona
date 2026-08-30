import datetime
import random
import string
from collections import defaultdict
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from common.choices.birth_time import BirthTime
from common.choices.gender import Gender
from common.choices.mbti import Mbti
from profiles.choices.profile_status_choices import ProfileStatusChoices
from profiles.models import Address, Job, JobCategory, JobInfo, Profile
from users.models import User
from users.models.identity_verification import IdentityVerification


class Command(BaseCommand):
    help = "Create dummy users and profiles for development environment"

    def generate_random_string(self, length=6):
        """랜덤 문자열 생성"""
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=50,
            help="Number of users to create (default: 50)",
        )
        parser.add_argument(
            "--male-ratio",
            type=float,
            default=0.5,
            help="Ratio of male users (0.0 to 1.0, default: 0.5)",
        )
        parser.add_argument(
            "--clear-existing",
            action="store_true",
            help="Clear existing users and profiles before creating new ones",
        )
        parser.add_argument(
            "--with-profiles",
            action="store_true",
            default=True,
            help="Create profiles for users (default: True)",
        )

    def handle(self, *args, **options):
        count = options["count"]
        male_ratio = options["male_ratio"]
        clear_existing = options["clear_existing"]
        with_profiles = options["with_profiles"]

        if clear_existing:
            self.stdout.write("Clearing existing users and profiles...")
            Profile.objects.all().delete()
            User.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Cleared existing data"))

        regions = Address.objects.values_list("region", flat=True)
        cities = defaultdict(list)

        for city, region in Address.objects.values_list("city", "region"):
            cities[region].append(city)

        if not regions:
            self.stdout.write(self.style.WARNING("No Address data found. Please create address data first."))
            return

        existing_job_categories = list(JobCategory.objects.all())
        existing_jobs = list(Job.objects.select_related("job_category").all())

        if not existing_job_categories:
            self.stdout.write(
                self.style.WARNING("No existing job categories found. Please create job categories first.")
            )
            return

        if not existing_jobs:
            self.stdout.write(self.style.WARNING("No existing jobs found. Please create jobs first."))
            return

        # MBTI 데이터
        mbti_types = [choice[0] for choice in Mbti.choices]

        created_users = []
        created_profiles = []

        with transaction.atomic():
            for i in range(count):
                # 성별 결정
                is_male = random.random() < male_ratio
                gender = Gender.MALE if is_male else Gender.FEMALE

                # 랜덤 문자열 생성
                random_suffix = self.generate_random_string()

                # 유저 생성
                user = User.objects.create_user(
                    email=f"dummy_{random_suffix}@example.com",
                    username=f"dummy_{random_suffix}",
                    real_name=f"더미유저{random_suffix}",
                    phone_number=f"010{random.randint(1000, 9999)}{random.randint(1000, 9999)}",
                    is_active=True,
                    confirmed_at=timezone.now() - timedelta(days=random.randint(1, 365)),
                )

                IdentityVerification.objects.create(
                    user=user,
                    di=f"dummy_di_{random_suffix}",
                    phone_number=user.phone_number,
                    real_name=user.real_name,
                    birth_date=datetime.date(
                        random.randint(1990, 2000),
                        random.randint(1, 12),
                        random.randint(1, 28),
                    ),
                    gender=gender,
                    request_no=f"dummy_request_no_{random_suffix}",
                    is_verified=True,
                    verified_at=timezone.now(),
                )

                created_users.append(user)

                if with_profiles:
                    # 프로필 생성
                    region = random.choice(regions)
                    city = random.choice(cities.get(region, ["기타"]))
                    birth_time = random.choice(BirthTime.values)

                    # 기존 데이터에서 랜덤하게 직업과 카테고리 선택
                    selected_job = random.choice(existing_jobs)
                    selected_job_category = selected_job.job_category

                    # JobInfo 생성
                    job_info = JobInfo.objects.create(job=selected_job, job_category=selected_job_category)

                    profile = Profile.objects.create(
                        user=user,
                        mbti=random.choice(mbti_types),
                        region=region,
                        city=city,
                        job_info=job_info,
                        gender=gender,
                        birth_time=birth_time,
                        status=ProfileStatusChoices.ACTIVE,
                    )
                    created_profiles.append(profile)

        # 결과 출력
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {len(created_users)} users and {len(created_profiles)} profiles")
        )

        # 통계 출력
        if with_profiles:
            male_count = len([p for p in created_profiles if p.gender == Gender.MALE])
            female_count = len([p for p in created_profiles if p.gender == Gender.FEMALE])

            self.stdout.write(f"Male users: {male_count}")
            self.stdout.write(f"Female users: {female_count}")

            # 지역별 통계
            region_stats = {}
            for profile in created_profiles:
                region = profile.region
                region_stats[region] = region_stats.get(region, 0) + 1

            self.stdout.write("\nRegion distribution:")
            for region, count in sorted(region_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
                self.stdout.write(f"  {region}: {count}")

            # MBTI 통계
            mbti_stats = {}
            for profile in created_profiles:
                mbti = profile.mbti
                if mbti:
                    mbti_stats[mbti] = mbti_stats.get(mbti, 0) + 1

            self.stdout.write("\nMBTI distribution:")
            for mbti, count in sorted(mbti_stats.items(), key=lambda x: x[1], reverse=True):
                self.stdout.write(f"  {mbti}: {count}")

            # 직업 카테고리 통계
            job_category_stats = {}
            job_stats = {}
            for profile in created_profiles:
                if profile.job_info:
                    job_category = profile.job_info.job_category
                    job = profile.job_info.job

                    if job_category:
                        job_category_stats[job_category.name] = job_category_stats.get(job_category.name, 0) + 1

                    if job:
                        job_stats[job.name] = job_stats.get(job.name, 0) + 1

            self.stdout.write("\nJob category distribution:")
            for job_category, count in sorted(job_category_stats.items(), key=lambda x: x[1], reverse=True):
                self.stdout.write(f"  {job_category}: {count}")

            self.stdout.write("\nJob distribution (top 10):")
            for job, count in sorted(job_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
                self.stdout.write(f"  {job}: {count}")

        self.stdout.write(self.style.SUCCESS("\nDummy data creation completed!"))
