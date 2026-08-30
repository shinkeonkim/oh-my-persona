from django.db import models


class CurrencyChoice(models.TextChoices):
  KRW = "KRW", "대한민국 원"
  USD = "USD", "미국 달러"
  EUR = "EUR", "유로"
  JPY = "JPY", "일본 엔"
  GBP = "GBP", "영국 파운드"
  CNY = "CNY", "중국 위안"
  HKD = "HKD", "홍콩 달러"
  AUD = "AUD", "호주 달러"
  CAD = "CAD", "캐나다 달러"
  CHF = "CHF", "스위스 프랑"
