"""기존 Stock 데이터의 최신 파생지표 캐시 업데이트"""
from django.core.management.base import BaseCommand
from django.db import transaction

from stocks.models import Stock


class Command(BaseCommand):
  help = "모든 Stock의 최신 파생지표 캐시를 업데이트합니다."

  def add_arguments(self, parser):
    parser.add_argument(
      "--stock-id",
      type=int,
      help="특정 Stock ID만 업데이트",
    )
    parser.add_argument(
      "--batch-size",
      type=int,
      default=100,
      help="배치 크기 (기본값: 100)",
    )

  def handle(self, *args, **options):
    stock_id = options.get("stock_id")
    batch_size = options.get("batch_size")

    if stock_id:
      # 특정 Stock만 업데이트
      try:
        stock = Stock.objects.get(pk=stock_id)
        self.stdout.write(f"Updating stock: {stock.name} ({stock.code})")
        stock.update_latest_indicators()
        self.stdout.write(self.style.SUCCESS(f"Successfully updated stock {stock_id}"))
      except Stock.DoesNotExist:
        self.stdout.write(self.style.ERROR(f"Stock with ID {stock_id} does not exist"))
        return

    else:
      # 모든 Stock 업데이트
      stocks = Stock.objects.all()
      total_count = stocks.count()
      self.stdout.write(f"Updating {total_count} stocks...")

      updated_count = 0
      for i in range(0, total_count, batch_size):
        batch = stocks[i:i + batch_size]

        with transaction.atomic():
          for stock in batch:
            stock.update_latest_indicators()
            updated_count += 1

            if updated_count % 10 == 0:
              self.stdout.write(f"Progress: {updated_count}/{total_count} ({updated_count * 100 // total_count}%)")

      self.stdout.write(self.style.SUCCESS(f"Successfully updated {updated_count} stocks"))
