from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from stocks.models import DerivedIndicator

from api.v1.stocks.serializers.derived_indicator_serializer import (
  DerivedIndicatorDetailSerializer,
  DerivedIndicatorSerializer,
)


class DerivedIndicatorFilter(filters.FilterSet):
  """파생지표 필터"""

  stock_code = filters.CharFilter(field_name="stock__code", lookup_expr="iexact")
  company_name = filters.CharFilter(field_name="company__name", lookup_expr="icontains")
  fiscal_year = filters.NumberFilter()
  fiscal_quarter = filters.NumberFilter()
  fiscal_year_gte = filters.NumberFilter(field_name="fiscal_year", lookup_expr="gte")
  fiscal_year_lte = filters.NumberFilter(field_name="fiscal_year", lookup_expr="lte")

  class Meta:
    model = DerivedIndicator
    fields = [
      "stock_code",
      "company_name",
      "fiscal_year",
      "fiscal_quarter",
      "fiscal_year_gte",
      "fiscal_year_lte",
    ]


class DerivedIndicatorListAPIView(generics.ListAPIView):
  """파생지표 목록 조회 API

  GET /api/v1/stocks/<stock_code>/derived-indicators/

  Query Parameters:
  - fiscal_year: 회계연도
  - fiscal_quarter: 분기
  - fiscal_year_gte: 회계연도 이상
  - fiscal_year_lte: 회계연도 이하
  - ordering: 정렬 (-fiscal_year, fiscal_quarter 등)
  """

  serializer_class = DerivedIndicatorSerializer
  filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
  filterset_class = DerivedIndicatorFilter
  ordering_fields = ["fiscal_year", "fiscal_quarter", "created_at"]
  ordering = ["-fiscal_year", "-fiscal_quarter"]

  def get_queryset(self):
    """종목 코드로 필터링"""
    stock_code = self.kwargs.get("code")
    return (
      DerivedIndicator.objects.filter(
        stock__code=stock_code
      ).select_related("stock", "company", "financial_statement").order_by("-fiscal_year", "-fiscal_quarter")
    )


class DerivedIndicatorDetailAPIView(generics.RetrieveAPIView):
  """파생지표 상세 조회 API

  GET /api/v1/stocks/<stock_code>/derived-indicators/<id>/
  """

  serializer_class = DerivedIndicatorDetailSerializer
  lookup_field = "id"

  def get_queryset(self):
    """종목 코드로 필터링"""
    stock_code = self.kwargs.get("code")
    return DerivedIndicator.objects.filter(stock__code=stock_code
                                           ).select_related("stock", "company", "financial_statement")
