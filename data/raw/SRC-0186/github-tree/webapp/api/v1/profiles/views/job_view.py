from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import FloatField, Value
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import (
  OpenApiParameter,
  OpenApiResponse,
  extend_schema,
)
from rest_framework import filters
from rest_framework.generics import ListAPIView

from common.schemas.error_schemas import get_not_found_error_schema
from profiles.models.job import Job
from profiles.models.job_category import JobCategory

from ..serializers import JobSerializer


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

    queryset = queryset.annotate(similarity=TrigramSimilarity(
      "name", search_term), ).filter(similarity__gt=self.similarity_threshold)

    queryset = queryset.order_by("-similarity")

    return queryset


@extend_schema(tags=["프로필 데이터"])
class JobListView(ListAPIView):
  """
  List jobs for a specific job category with fuzzy search functionality on name field using trigram similarity.
  """

  serializer_class = JobSerializer
  filter_backends = [TrigramSimilaritySearchFilter, filters.OrderingFilter]
  ordering_fields = ["name", "created_at", "similarity"]

  def get_queryset(self):
    """
    Filter jobs by job_category_id from URL path
    """
    job_category_id = self.kwargs["job_category_id"]
    job_category = get_object_or_404(JobCategory, id=job_category_id)
    return Job.objects.filter(job_category=job_category).select_related("job_category")

  @extend_schema(
    operation_id="list_jobs_by_category",
    summary="List Jobs by Category",
    description="Retrieve a list of jobs for a specific job category.",
    parameters=[
      OpenApiParameter(
        name="job_category_id",
        description="Job category ID to filter jobs",
        required=True,
        type=int,
        location=OpenApiParameter.PATH,
      ),
      OpenApiParameter(
        name="search",
        description="Search term to filter by job name",
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
    responses={
      200: OpenApiResponse(
        response=JobSerializer(many=True),
        description="List of jobs for the specified category",
      ),
      404: get_not_found_error_schema("Job category"),
    },
  )
  def get(self, request, *args, **kwargs):
    return super().get(request, *args, **kwargs)
