"""
Trigram similarity based search filter
"""

from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import FloatField, Value
from django.db.models.functions import Greatest
from django.utils.encoding import force_str

from rest_framework import filters


class TrigramSimilaritySearchMaxFilter(filters.BaseFilterBackend):
  """
    Trigram similarity based search filter.

    Searches and sorts by the maximum similarity among specified fields.

    Usage:
        class MyView(ListAPIView):
            filter_backends = [TrigramSimilaritySearchMaxFilter]
            trigram_similarity_search_fields = ["name", "code", "description"]
            trigram_similarity_threshold = 0.1  # Optional, defaults to 0.1

    Query Parameters:
        - search: search term
        - ordering: ordering field (can use 'similarity')
    """

  search_param = "search"
  default_similarity_threshold = 0.1
  search_title = "Search"
  search_description = "A search term for trigram similarity matching."

  def filter_queryset(self, request, queryset, view):  # noqa: ARG002
    search_term = request.query_params.get(self.search_param)

    # Get search fields defined in the view
    search_fields = getattr(view, "trigram_similarity_search_fields", [])
    if not search_fields:
      msg = (f"{view.__class__.__name__} must define "
             f"'trigram_similarity_search_fields' attribute")
      raise AttributeError(msg)

    # Get threshold from view (use default if not specified)
    threshold = getattr(
      view,
      "trigram_similarity_threshold",
      self.default_similarity_threshold,
    )

    # If no search term, set similarity to 0
    if not search_term:
      queryset = queryset.annotate(similarity=Value(0.0, output_field=FloatField()))
      return queryset

    # Calculate similarity for each field
    annotations = {}
    for field in search_fields:
      similarity_field_name = f"{field}_similarity"
      annotations[similarity_field_name] = TrigramSimilarity(field, search_term)

    # Annotate with individual similarities
    queryset = queryset.annotate(**annotations)

    # Calculate maximum similarity using Greatest
    similarity_fields = [f"{field}_similarity" for field in search_fields]
    queryset = queryset.annotate(similarity=Greatest(*similarity_fields), )

    # Filter by threshold
    queryset = queryset.filter(similarity__gt=threshold)
    queryset = queryset.order_by("-similarity")

    print(queryset.values_list('name', 'similarity'))

    return queryset

  def get_schema_operation_parameters(self, view):
    """
        Return OpenAPI schema parameters for the search field.
        """
    search_fields = getattr(view, "trigram_similarity_search_fields", [])
    if not search_fields:
      return []

    fields_str = ", ".join(search_fields)
    description = (
      f"{force_str(self.search_description)} "
      f"Searches across fields: {fields_str} using trigram similarity."
    )

    return [
      {
        "name": self.search_param,
        "required": False,
        "in": "query",
        "description": description,
        "schema": {
          "type": "string",
        },
      },
    ]
