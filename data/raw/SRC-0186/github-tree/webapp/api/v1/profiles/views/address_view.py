from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import FloatField, Value
from django.db.models.functions import Concat, Greatest

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import filters
from rest_framework.generics import ListAPIView

from profiles.models.address import Address

from ..serializers import AddressSerializer


class TrigramSimilaritySearchFilter(filters.BaseFilterBackend):
  """
    Trigram 유사도 기반 검색 필터.

    city, region, 그리고 region+city 전체 주소에 대한 유사도 중 최댓값을 사용합니다.
    """

  search_param = "search"
  similarity_threshold = 0.1

  def filter_queryset(self, request, queryset, view):
    search_term = request.query_params.get(self.search_param)
    ordering_param = request.query_params.get("ordering")

    if not search_term:
      queryset = queryset.annotate(similarity=Value(0.0, output_field=FloatField()))

      if not ordering_param:
        return queryset.order_by("region", "city")
      return queryset

    queryset = queryset.annotate(
      full_address=Concat("region", Value(" "), "city"),
      city_similarity=TrigramSimilarity("city", search_term),
      region_similarity=TrigramSimilarity("region", search_term),
      full_similarity=TrigramSimilarity("full_address", search_term),
      similarity=Greatest("city_similarity", "region_similarity", "full_similarity"),
    ).filter(similarity__gt=self.similarity_threshold)

    queryset = queryset.order_by("-similarity")

    return queryset


@extend_schema(tags=["프로필 데이터"])
class AddressListView(ListAPIView):
  """
    List addresses with search functionality on region and city fields using trigram similarity.
    """

  serializer_class = AddressSerializer
  queryset = Address.objects.all()
  filter_backends = [TrigramSimilaritySearchFilter, filters.OrderingFilter]
  ordering_fields = ["region", "city", "created_at", "similarity"]

  @extend_schema(
    operation_id="list_addresses",
    summary="List Addresses",
    description="Retrieve a list of addresses. Supports fuzzy search",
    parameters=[
      OpenApiParameter(
        name="search",
        description="Search term to filter by region or city (supports fuzzy matching)",
        required=False,
        type=str,
      ),
      OpenApiParameter(
        name="ordering",
        description="Which field to use when ordering the results (e.g., '-similarity' for best matches first)",
        required=False,
        type=str,
      ),
    ],
    responses={200: OpenApiResponse(
      response=AddressSerializer(many=True),
      description="List of addresses",
    )},
  )
  def get(self, request, *args, **kwargs):
    return super().get(request, *args, **kwargs)
