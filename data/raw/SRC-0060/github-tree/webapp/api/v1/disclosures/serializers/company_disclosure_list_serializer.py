from disclosures.models import CompanyDisclosure
from rest_framework import serializers


class CompanyDisclosureListSerializer(serializers.ModelSerializer):
  """Company disclosure serializer for list views without heavy bodies"""

  company_name = serializers.CharField(source="company.name", read_only=True)

  class Meta:
    model = CompanyDisclosure
    fields = [
      "id",
      "company_name",
      "receipt_no",
      "title",
      "published_at",
      "disclosure_type",
      "source_url",
      "created_at",
      "updated_at",
    ]
    read_only_fields = fields
