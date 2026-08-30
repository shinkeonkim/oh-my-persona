from disclosures.models import CompanyDisclosure
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics

from ..serializers import CompanyDisclosureListSerializer


class CompanyDisclosureListAPIView(generics.ListAPIView):
  """
    GET /api/v1/disclosures/

    List all disclosures for a specific company.

    Query Parameters:
    - company__corp_code: Filter by company corp code
    - receipt_no: Filter by receipt number
    - disclosure_type: Filter by disclosure type
    - published_at: Filter by published date (YYYY-MM-DD)
    - published_at__gte: Filter by published date greater than or equal to
    - published_at__lte: Filter by published date less than or equal to
    - search: Search by title
    - ordering: Order by fields (e.g., '-published_at', 'title')
    """

  queryset = CompanyDisclosure.objects.select_related("company").all()
  serializer_class = CompanyDisclosureListSerializer
  filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
  filterset_fields = {
    "company__corp_code": ["exact"],
    "receipt_no": ["exact"],
    "disclosure_type": ["exact"],
    "published_at": ["exact", "gte", "lte"],
  }
  search_fields = ["title", "text_body"]
  ordering_fields = ["published_at", "created_at", "updated_at"]
  ordering = ["-published_at"]
