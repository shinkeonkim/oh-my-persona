"""Stock API 필터"""
import django_filters
from stocks.models import Stock


class StockDerivedIndicatorFilter(django_filters.FilterSet):
  """파생지표 필터

  각 지표에 대해 다음 필터를 지원합니다:
  - {field}: 정확한 값
  - {field}__gte: 크거나 같음 (>=)
  - {field}__gt: 큼 (>)
  - {field}__lte: 작거나 같음 (<=)
  - {field}__lt: 작음 (<)
  - {field}__range: 범위 (min,max 형식으로 전달)

  예시:
  - ?latest_per__gte=10&latest_per__lte=20  # 10 <= PER <= 20
  - ?latest_roe__gte=15  # ROE >= 15%
  - ?latest_pbr__lt=1  # PBR < 1
  """

  # PER (주가수익비율) 필터
  latest_per = django_filters.NumberFilter(field_name="latest_per")
  latest_per__gte = django_filters.NumberFilter(field_name="latest_per", lookup_expr="gte")
  latest_per__gt = django_filters.NumberFilter(field_name="latest_per", lookup_expr="gt")
  latest_per__lte = django_filters.NumberFilter(field_name="latest_per", lookup_expr="lte")
  latest_per__lt = django_filters.NumberFilter(field_name="latest_per", lookup_expr="lt")
  latest_per__range = django_filters.RangeFilter(field_name="latest_per")

  # EPS (주당순이익) 필터
  latest_eps = django_filters.NumberFilter(field_name="latest_eps")
  latest_eps__gte = django_filters.NumberFilter(field_name="latest_eps", lookup_expr="gte")
  latest_eps__gt = django_filters.NumberFilter(field_name="latest_eps", lookup_expr="gt")
  latest_eps__lte = django_filters.NumberFilter(field_name="latest_eps", lookup_expr="lte")
  latest_eps__lt = django_filters.NumberFilter(field_name="latest_eps", lookup_expr="lt")
  latest_eps__range = django_filters.RangeFilter(field_name="latest_eps")

  # PBR (주가순자산비율) 필터
  latest_pbr = django_filters.NumberFilter(field_name="latest_pbr")
  latest_pbr__gte = django_filters.NumberFilter(field_name="latest_pbr", lookup_expr="gte")
  latest_pbr__gt = django_filters.NumberFilter(field_name="latest_pbr", lookup_expr="gt")
  latest_pbr__lte = django_filters.NumberFilter(field_name="latest_pbr", lookup_expr="lte")
  latest_pbr__lt = django_filters.NumberFilter(field_name="latest_pbr", lookup_expr="lt")
  latest_pbr__range = django_filters.RangeFilter(field_name="latest_pbr")

  # BPS (주당순자산) 필터
  latest_bps = django_filters.NumberFilter(field_name="latest_bps")
  latest_bps__gte = django_filters.NumberFilter(field_name="latest_bps", lookup_expr="gte")
  latest_bps__gt = django_filters.NumberFilter(field_name="latest_bps", lookup_expr="gt")
  latest_bps__lte = django_filters.NumberFilter(field_name="latest_bps", lookup_expr="lte")
  latest_bps__lt = django_filters.NumberFilter(field_name="latest_bps", lookup_expr="lt")
  latest_bps__range = django_filters.RangeFilter(field_name="latest_bps")

  # ROE (자기자본이익률) 필터
  latest_roe = django_filters.NumberFilter(field_name="latest_roe")
  latest_roe__gte = django_filters.NumberFilter(field_name="latest_roe", lookup_expr="gte")
  latest_roe__gt = django_filters.NumberFilter(field_name="latest_roe", lookup_expr="gt")
  latest_roe__lte = django_filters.NumberFilter(field_name="latest_roe", lookup_expr="lte")
  latest_roe__lt = django_filters.NumberFilter(field_name="latest_roe", lookup_expr="lt")
  latest_roe__range = django_filters.RangeFilter(field_name="latest_roe")

  # ROA (총자산이익률) 필터
  latest_roa = django_filters.NumberFilter(field_name="latest_roa")
  latest_roa__gte = django_filters.NumberFilter(field_name="latest_roa", lookup_expr="gte")
  latest_roa__gt = django_filters.NumberFilter(field_name="latest_roa", lookup_expr="gt")
  latest_roa__lte = django_filters.NumberFilter(field_name="latest_roa", lookup_expr="lte")
  latest_roa__lt = django_filters.NumberFilter(field_name="latest_roa", lookup_expr="lt")
  latest_roa__range = django_filters.RangeFilter(field_name="latest_roa")

  # 배당수익률 필터
  latest_dividend_yield = django_filters.NumberFilter(field_name="latest_dividend_yield")
  latest_dividend_yield__gte = django_filters.NumberFilter(field_name="latest_dividend_yield", lookup_expr="gte")
  latest_dividend_yield__gt = django_filters.NumberFilter(field_name="latest_dividend_yield", lookup_expr="gt")
  latest_dividend_yield__lte = django_filters.NumberFilter(field_name="latest_dividend_yield", lookup_expr="lte")
  latest_dividend_yield__lt = django_filters.NumberFilter(field_name="latest_dividend_yield", lookup_expr="lt")
  latest_dividend_yield__range = django_filters.RangeFilter(field_name="latest_dividend_yield")

  # DPS (주당배당금) 필터
  latest_dps = django_filters.NumberFilter(field_name="latest_dps")
  latest_dps__gte = django_filters.NumberFilter(field_name="latest_dps", lookup_expr="gte")
  latest_dps__gt = django_filters.NumberFilter(field_name="latest_dps", lookup_expr="gt")
  latest_dps__lte = django_filters.NumberFilter(field_name="latest_dps", lookup_expr="lte")
  latest_dps__lt = django_filters.NumberFilter(field_name="latest_dps", lookup_expr="lt")
  latest_dps__range = django_filters.RangeFilter(field_name="latest_dps")

  class Meta:
    model = Stock
    fields = {
      "company__corp_code": ["exact"],
      "category": ["exact"],
      "is_primary": ["exact"],
      "is_listed": ["exact"],
    }
