from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from financial_statements.models import FinancialStatement
from rest_framework import filters, generics

from api.v1.financial_statements.serializers import FinancialStatementSerializer
from companies.models import Company


class CompanyFinancialStatementListAPIView(generics.ListAPIView):
  """
    GET /api/v1/companies/:company_id/financial_statements/

    List all financial statements for a specific company.

    Query Parameters:
    - fiscal_year: Filter by fiscal year
    - fiscal_quarter: Filter by fiscal quarter (1, 2, 3, 4)
    - report_type: Filter by report type (annual, half, q3, q1)
    - source: Filter by source (CFS, OFS)
    - is_consolidated: Filter by consolidation status (true/false)
    - ordering: Order by fields (e.g., '-fiscal_year', '-fiscal_quarter')
    """

  serializer_class = FinancialStatementSerializer
  filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
  filterset_fields = {
    "fiscal_year": ["exact", "gte", "lte"],
    "fiscal_quarter": ["exact"],
    "report_type": ["exact"],
    "source": ["exact"],
    "is_consolidated": ["exact"],
  }
  ordering_fields = ["fiscal_year", "fiscal_quarter", "created_at", "updated_at"]
  ordering = ["-fiscal_year", "-fiscal_quarter"]

  def get_queryset(self):
    corp_code = self.kwargs["corp_code"]
    company = get_object_or_404(Company, corp_code=corp_code)
    return FinancialStatement.objects.filter(company=company)
