from rest_framework import generics
from stocks.models import Stock

from api.v1.stocks.serializers.stock_detail_serializer import StockDetailSerializer


class StockDetailAPIView(generics.RetrieveAPIView):
  """
    GET /api/v1/stocks/:code/

    Retrieve a single stock with detailed information by code.
    """

  queryset = Stock.objects.select_related(
    "company",
    "company__country",
    "company__sector",
    "company__industry",
    "market",
  ).prefetch_related("prices").all()
  serializer_class = StockDetailSerializer
  lookup_field = "code"
