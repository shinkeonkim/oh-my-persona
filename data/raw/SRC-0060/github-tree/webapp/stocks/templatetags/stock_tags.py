from datetime import timedelta

from django import template
from django.utils import timezone

from stocks.models import StockPrice

register = template.Library()


@register.simple_tag
def get_recent_stock_prices(stock, days=10):
  """주식의 최근 N일 가격 데이터 조회 (리스트로 반환)"""
  end_date = timezone.now().date()
  start_date = end_date - timedelta(days=days)

  # list()로 변환하여 반환 - 템플릿에서 |last 필터 사용 가능
  return list(
    StockPrice.objects.filter(stock=stock, trade_date__gte=start_date, trade_date__lte=end_date).order_by('trade_date')
  )


@register.filter
def max_high_price(prices):
  """주가 리스트에서 최고가를 반환"""
  if not prices:
    return 0
  return max(price.high_price for price in prices)


@register.filter
def min_low_price(prices):
  """주가 리스트에서 최저가를 반환"""
  if not prices:
    return 0
  return min(price.low_price for price in prices)
