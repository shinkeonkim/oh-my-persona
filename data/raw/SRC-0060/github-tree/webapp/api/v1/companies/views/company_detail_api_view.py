from rest_framework import generics

from api.v1.companies.serializers import CompanySerializer
from companies.models import Company


class CompanyDetailAPIView(generics.RetrieveAPIView):
  """
    GET /api/v1/companies/:corp_code/

    Retrieve a single company with detailed information by corp_code.
    """

  queryset = Company.objects.select_related("country", "sector", "industry").all()
  serializer_class = CompanySerializer
  lookup_field = "corp_code"
