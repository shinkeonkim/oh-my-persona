"""
기본 시장 데이터 생성 커맨드

사용법:
    python manage.py create_default_markets
"""

from django.core.management.base import BaseCommand

from stocks.models import Market

from companies.models import Country

KR_NOT_FOUND_ERROR_MESSAGE = ("국가 데이터(KR)가 존재하지 않습니다. "
                              "먼저 'python manage.py create_default_countries'를 실행하세요.")


class Command(BaseCommand):
  help = "기본 시장 데이터 (KOSPI, KOSDAQ)를 생성합니다"

  def handle(self, *args, **options):
    self.stdout.write("기본 시장 데이터 생성 중...")

    try:
      kr_country = Country.objects.get(code="KR")
    except Country.DoesNotExist:
      self.stdout.write(self.style.ERROR(KR_NOT_FOUND_ERROR_MESSAGE))
      return

    markets = [
      {
        "code": "STK",
        "name": "KOSPI"
      },
      {
        "code": "KSQ",
        "name": "KOSDAQ"
      },
    ]

    created_count = 0
    skipped_count = 0

    for market_data in markets:
      market, created = Market.objects.get_or_create(
        code=market_data["code"],
        defaults={
          "name": market_data["name"],
          "country": kr_country,
        },
      )

      if created:
        self.stdout.write(self.style.SUCCESS(f"시장 생성 완료: {market.name} ({market.code})"))
        created_count += 1
      else:
        self.stdout.write(self.style.WARNING(f"시장 이미 존재: {market.name} ({market.code})"))
        skipped_count += 1

    self.stdout.write(self.style.SUCCESS(f"\n완료! 생성: {created_count}개, 스킵: {skipped_count}개"))
