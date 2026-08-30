from disclosures.models import CompanyDisclosure
from rest_framework import generics

from ..serializers import CompanyDisclosureSerializer


class CompanyDisclosureDetailAPIView(generics.RetrieveAPIView):
  """
    GET /api/v1/company-disclosures/:id/

    Retrieve a single company disclosure by ID.
    """

  queryset = CompanyDisclosure.objects.select_related("company").all()
  serializer_class = CompanyDisclosureSerializer
