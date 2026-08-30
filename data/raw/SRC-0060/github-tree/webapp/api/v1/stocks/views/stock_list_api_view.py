from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from stocks.models import Stock

from common.pagination import StandardPagination

from ..filters import StockDerivedIndicatorFilter
from ..serializers import StockSerializer


class StockListAPIView(generics.ListAPIView):
  """
    GET /api/v1/stocks/

    List all stocks with filtering and ordering capabilities.

    Query Parameters:
    - company: Filter by company ID
    - market: Filter by market ID
    - category: Filter by stock category (COMMON, PREFERRED, OTHER)
    - is_primary: Filter by primary stock flag (true/false)
    - is_listed: Filter by listed status (true/false)
    - search: Search by stock code or name
    - ordering: Order by fields (e.g., 'name', '-created_at')

    Derived Indicator Filters (파생지표 필터):
    각 지표에 대해 다음과 같은 필터를 사용할 수 있습니다:
    - {field}__gte: 크거나 같음 (>=)
    - {field}__gt: 큼 (>)
    - {field}__lte: 작거나 같음 (<=)
    - {field}__lt: 작음 (<)
    - {field}__range: 범위 (min,max)

    사용 가능한 지표:
    - latest_per: PER (주가수익비율)
    - latest_eps: EPS (주당순이익)
    - latest_pbr: PBR (주가순자산비율)
    - latest_bps: BPS (주당순자산)
    - latest_roe: ROE (자기자본이익률, %)
    - latest_roa: ROA (총자산이익률, %)
    - latest_dividend_yield: 배당수익률 (%)
    - latest_dps: DPS (주당배당금)

    예시:
    - ?latest_per__gte=10&latest_per__lte=20  # 10 <= PER <= 20
    - ?latest_roe__gte=15  # ROE >= 15%
    - ?latest_pbr__lt=1&latest_roe__gte=10  # PBR < 1 AND ROE >= 10%
    """

  queryset = Stock.objects.select_related("company", "market").listed()
  serializer_class = StockSerializer
  filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
  pagination_class = StandardPagination
  filterset_class = StockDerivedIndicatorFilter
  search_fields = ["code", "name", "company__name", "company__corp_code"]
  ordering_fields = [
    "name",
    "code",
    "created_at",
    "updated_at",
    "latest_per",
    "latest_eps",
    "latest_pbr",
    "latest_bps",
    "latest_roe",
    "latest_roa",
    "latest_dividend_yield",
    "latest_dps",
  ]
  ordering = ["code"]
