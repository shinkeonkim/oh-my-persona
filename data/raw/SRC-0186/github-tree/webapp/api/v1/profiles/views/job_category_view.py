from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import F, FloatField, Max, Value

from drf_spectacular.utils import (
  OpenApiParameter,
  OpenApiResponse,
  extend_schema,
)
from rest_framework import filters
from rest_framework.generics import ListAPIView

from common.pagination.standard_pagination import StandardPagination
from profiles.models.job_category import JobCategory

from ..serializers import JobCategorySerializer


class TrigramSimilaritySearchFilter(filters.BaseFilterBackend):
  """
    Trigram 유사도 기반 검색 필터.

    name 필드에 대한 유사도를 계산하여 검색합니다.
    """

  search_param = "search"
  similarity_threshold = 0.1

  def filter_queryset(self, request, queryset, view):
    search_term = request.query_params.get(self.search_param)
    ordering_param = request.query_params.get("ordering")

    if not search_term:
      queryset = queryset.annotate(similarity=Value(0.0, output_field=FloatField()))

      if not ordering_param:
        return queryset.order_by("name")
      return queryset

    queryset = (
      queryset
      .annotate(
        name_similarity=TrigramSimilarity("name", search_term),
        max_job_name_similarity=Max(TrigramSimilarity("job__name", search_term)))
      .annotate(
        similarity=(F("name_similarity") + F("max_job_name_similarity"))
      )
      .filter(similarity__gt=self.similarity_threshold)
      .order_by("-similarity", "id")
    )

    return queryset


@extend_schema(tags=["프로필 데이터"])
class JobCategoryListView(ListAPIView):
  """
    List job categories with search functionality on name field using trigram similarity.
    """

  serializer_class = JobCategorySerializer
  queryset = JobCategory.objects.all()
  filter_backends = [TrigramSimilaritySearchFilter, filters.OrderingFilter]
  ordering_fields = ["name", "created_at", "similarity"]
  pagination_class = StandardPagination

  @extend_schema(
    operation_id="list_job_categories",
    summary="List Job Categories",
    description="Retrieve a list of job categories. Supports fuzzy search on name field using trigram similarity.",
    parameters=[
      OpenApiParameter(
        name="search",
        description="Search term to filter by job category name",
        required=False,
        type=str,
      ),
      OpenApiParameter(
        name="ordering",
        description="Which field to use when ordering the results",
        required=False,
        type=str,
      ),
    ],
    responses={200: OpenApiResponse(
      response=JobCategorySerializer(many=True),
      description="List of job categories",
    )},
  )
  def get(self, request, *args, **kwargs):
    return super().get(request, *args, **kwargs)
