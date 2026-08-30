from rest_framework import serializers

from companies.models import Company

from .company_industry_serializer import IndustrySerializer
from .company_sector_serializer import CompanySectorSerializer
from .country_serializer import CountrySerializer


class CompanyListSerializer(serializers.ModelSerializer):
  """Company list serializer - minimal fields"""

  country = CountrySerializer(read_only=True)
  sector = CompanySectorSerializer(read_only=True)
  industry = IndustrySerializer(read_only=True)

  class Meta:
    model = Company
    fields = [
      "name",
      "corp_code",
      "country",
      "sector",
      "industry",
      "is_financial",
      "website",
      "created_at",
      "updated_at",
    ]
    read_only_fields = fields
