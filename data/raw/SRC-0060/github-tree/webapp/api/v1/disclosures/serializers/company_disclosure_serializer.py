from disclosures.models import CompanyDisclosure
from rest_framework import serializers


class CompanyDisclosureSerializer(serializers.ModelSerializer):
  """Company disclosure serializer"""

  company_name = serializers.CharField(source="company.name", read_only=True)

  class Meta:
    model = CompanyDisclosure
    fields = [
      "id",
      "company_name",
      "receipt_no",
      "title",
      "published_at",
      "text_body",
      "html_body",
      "disclosure_type",
      "source_url",
      "created_at",
      "updated_at",
    ]
    read_only_fields = fields
