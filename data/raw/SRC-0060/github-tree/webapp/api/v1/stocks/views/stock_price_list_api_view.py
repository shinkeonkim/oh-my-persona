from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from stocks.models import Stock, StockPrice

from ..serializers import StockPriceSerializer


class StockPriceListAPIView(generics.ListAPIView):
  """
    GET /api/v1/companies/:company_id/stocks/:stock_id/prices/

    List all stock prices for a specific stock.

    Query Parameters:
    - trade_date: Filter by specific trade date (YYYY-MM-DD)
    - trade_date__gte: Filter by trade date greater than or equal to
    - trade_date__lte: Filter by trade date less than or equal to
    - ordering: Order by fields (e.g., '-trade_date', 'close_price')
    """

  serializer_class = StockPriceSerializer
  filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
  filterset_fields = {
    "trade_date": ["exact", "gte", "lte"],
  }
  ordering_fields = [
    "trade_date",
    "close_price",
    "volume",
    "market_cap",
  ]
  ordering = ["-trade_date"]

  def get_queryset(self):
    stock_code = self.kwargs["code"]

    # Validate company and stock relationship
    stock = get_object_or_404(Stock, code=stock_code)

    return StockPrice.objects.select_related("stock", "market").filter(stock=stock)
