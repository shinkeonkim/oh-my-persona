"""Stocks 앱 시그널"""
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from stocks.models import DerivedIndicator


@receiver(post_save, sender=DerivedIndicator)
def update_stock_latest_indicators_on_save(sender, instance, created, **kwargs):
  """DerivedIndicator 저장 시 Stock의 최신 지표 캐시 업데이트"""
  if instance.stock:
    instance.stock.update_latest_indicators()


@receiver(post_delete, sender=DerivedIndicator)
def update_stock_latest_indicators_on_delete(sender, instance, **kwargs):
  """DerivedIndicator 삭제 시 Stock의 최신 지표 캐시 업데이트"""
  if instance.stock:
    instance.stock.update_latest_indicators()
