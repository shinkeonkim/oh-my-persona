from financial_statements.models import FinancialStatement, FinancialStatementAccount, FinancialStatementItem
from rest_framework import serializers


class FinancialStatementAccountSerializer(serializers.ModelSerializer):
  """Financial statement account serializer"""

  class Meta:
    model = FinancialStatementAccount
    fields = [
      "id",
      "account_id",
      "account_name",
      "account_category",
      "category_name",
      "account_detail",
    ]
    read_only_fields = fields


class FinancialStatementItemSerializer(serializers.ModelSerializer):
  """Financial statement item serializer"""

  account = FinancialStatementAccountSerializer(read_only=True)

  class Meta:
    model = FinancialStatementItem
    fields = [
      "id",
      "account",
      "current_amount",
      "cumulative_amount",
      "order",
      "created_at",
      "updated_at",
    ]
    read_only_fields = fields


class FinancialStatementSerializer(serializers.ModelSerializer):
  """Financial statement serializer for list view (without items)"""

  company_name = serializers.CharField(source="company.name", read_only=True)
  report_type_display = serializers.CharField(source="get_report_type_display", read_only=True)
  source_display = serializers.CharField(source="get_source_display", read_only=True)

  class Meta:
    model = FinancialStatement
    fields = [
      "id",
      "company_name",
      "fiscal_year",
      "fiscal_quarter",
      "report_type",
      "report_type_display",
      "currency",
      "is_consolidated",
      "submission_date",
      "receipt_no",
      "source",
      "source_display",
      "created_at",
      "updated_at",
    ]
    read_only_fields = fields
