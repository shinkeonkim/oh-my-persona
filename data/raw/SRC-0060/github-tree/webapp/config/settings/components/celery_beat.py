"""
Celery Beat 주기적 작업 스케줄 설정
"""

from celery.schedules import crontab

# Celery Beat 스케줄 설정
CELERY_BEAT_SCHEDULE = {
  # 오늘 주식 가격 - 30분마다 실행 (09:00, 09:30, 10:00, 10:30, ..., 16:00, 16:30)
  "ingest-today-stock-prices-every-30min": {
    "task": "stocks.tasks.ingest_today_stock_prices",
    "schedule": crontab(minute="*/30", hour="9-16"),
    "options": {
      "expires": 1800,  # 30분 후 만료
    },
  },
  # 어제 주식 가격 - 매일 새벽 1시에 실행
  "ingest-yesterday-stock-prices-daily": {
    "task": "stocks.tasks.ingest_yesterday_stock_prices",
    "schedule": crontab(minute=0, hour=1),
    "options": {
      "expires": 3600,  # 1시간 후 만료
    },
  },
  # 상장폐지 종목 - 12시간마다 실행 (00:30, 12:30)
  "ingest-delisted-stocks-twice-daily": {
    "task": "stocks.tasks.ingest_delisted_stocks_auto",
    "schedule": crontab(minute=30, hour="0,12"),
    "kwargs": {
      "market_id": "ALL"
    },
    "options": {
      "expires": 43200,  # 12시간 후 만료
    },
  },
  # DART 회사 정보 - 매일 새벽 2시에 실행
  "ingest-dart-company-data-daily": {
    "task": "companies.tasks.ingest_dart_company_data",
    "schedule": crontab(minute=0, hour=2),
    "options": {
      "expires": 3600,  # 1시간 후 만료
    },
  },
}

__all__ = [
  "CELERY_BEAT_SCHEDULE",
]
