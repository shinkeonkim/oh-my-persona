from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics

from api.v1.common.filters import TrigramSimilaritySearchMaxFilter
from api.v1.companies.serializers import CompanyListSerializer
from companies.models import Company


class CompanyListAPIView(generics.ListAPIView):
  """
    GET /api/v1/companies/

    List all companies with filtering, searching, and ordering capabilities.
    """

  queryset = Company.objects.select_related("country", "sector", "industry").all()
  serializer_class = CompanyListSerializer
  filter_backends = [
    DjangoFilterBackend,
    TrigramSimilaritySearchMaxFilter,
    filters.OrderingFilter,
  ]
  filterset_fields = ["country", "sector", "industry", "is_financial"]
  ordering_fields = [
    "name",
    "created_at",
    "updated_at",
    "similarity",
  ]

  # Trigram 유사도 검색 설정
  trigram_similarity_search_fields = ["name", "corp_code"]
  trigram_similarity_threshold = 0.2
