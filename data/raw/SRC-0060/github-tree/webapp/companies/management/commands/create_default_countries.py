"""
기본 국가 데이터 생성 커맨드

사용법:
    python manage.py create_default_countries
"""

from django.core.management.base import BaseCommand

from companies.models import Country


class Command(BaseCommand):
  help = "기본 국가 데이터 (KR, US)를 생성합니다"

  def handle(self, *args, **options):
    self.stdout.write("기본 국가 데이터 생성 중...")

    countries = [
      {
        "code": "KR",
        "name": "대한민국"
      },
      {
        "code": "US",
        "name": "미국"
      },
    ]

    created_count = 0
    skipped_count = 0

    for country_data in countries:
      country, created = Country.objects.get_or_create(
        code=country_data["code"],
        defaults={"name": country_data["name"]},
      )

      if created:
        self.stdout.write(self.style.SUCCESS(f"국가 생성 완료: {country.name} ({country.code})"))
        created_count += 1
      else:
        self.stdout.write(self.style.WARNING(f"국가 이미 존재: {country.name} ({country.code})"))
        skipped_count += 1

    self.stdout.write(self.style.SUCCESS(f"\n완료! 생성: {created_count}개, 스킵: {skipped_count}개"))
