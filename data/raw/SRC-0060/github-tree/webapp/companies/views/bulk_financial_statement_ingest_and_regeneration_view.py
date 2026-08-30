"""
Bulk Financial Statement Ingest and Regeneration View

Admin에서 모든 Company에 대해 특정 연도의 재무제표를 배치 단위로 수집 및 재생성하는 뷰
"""

import logging

from django import forms
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from financial_statements.tasks import bulk_ingest_and_regenerate_financial_statements
from unfold.views import UnfoldModelAdminViewMixin

from companies.models import Company

logger = logging.getLogger(__name__)


class BulkFinancialStatementIngestAndRegenerationForm(forms.Form):
  """전체 회사 재무제표 수집 및 재생성 폼"""

  fiscal_year = forms.IntegerField(
    label=_("Fiscal Year"),
    min_value=2000,
    max_value=2100,
    initial=timezone.now().year,
    widget=forms.NumberInput(attrs={"class": "form-control"}),
    help_text=_("Enter fiscal year (e.g., 2024) to collect all quarters for that year."),
    required=True,
  )

  quarters = forms.CharField(
    label=_("Quarters"),
    initial="1,2,3,4",
    widget=forms.TextInput(attrs={"class": "form-control"}),
    help_text=_("Enter comma-separated quarters (1-4), e.g. 1,2,3,4"),
    required=True,
  )

  is_listed_only = forms.BooleanField(
    label=_("Listed companies only"),
    initial=False,
    required=False,
    help_text=_("If checked, only processes companies with listed stocks."),
  )

  is_financial_excluded = forms.BooleanField(
    label=_("Exclude financial companies"),
    initial=False,
    required=False,
    help_text=_("If checked, excludes financial companies (is_financial=True)."),
  )

  batch_size = forms.IntegerField(
    label=_("Batch size"),
    min_value=1,
    max_value=100,
    initial=25,
    widget=forms.NumberInput(attrs={"class": "form-control"}),
    help_text=_("Number of companies to process in each batch. Recommended: 20-30"),
    required=True,
  )

  sleep_seconds = forms.IntegerField(
    label=_("Sleep between batches (seconds)"),
    min_value=0,
    max_value=600,
    initial=180,
    widget=forms.NumberInput(attrs={"class": "form-control"}),
    help_text=_("Wait time between batches to avoid API rate limits. Recommended: 180 (3 minutes)"),
    required=True,
  )

  page_count = forms.IntegerField(
    label=_("Page count"),
    min_value=1,
    max_value=1000,
    initial=100,
    widget=forms.NumberInput(attrs={"class": "form-control"}),
    help_text=_("Maximum number of rows to request per DART response."),
    required=True,
  )


class BulkFinancialStatementIngestAndRegenerationView(UnfoldModelAdminViewMixin, FormView):
  """전체 회사 재무제표 수집 및 재생성 커스텀 페이지

  API 요청 제한을 고려하여 배치 단위로 나누어 처리합니다.
  """

  title = _("Bulk Collect Financial Statements for All Companies")
  permission_required = ()
  template_name = "admin/companies/company/bulk_financial_statement_ingest_and_regeneration_form.html"
  form_class = BulkFinancialStatementIngestAndRegenerationForm

  def get_initial(self):
    """초기값 설정"""
    return {
      "fiscal_year": timezone.now().year,
      "quarters": "1,2,3,4",
      "is_listed_only": False,
      "is_financial_excluded": False,
      "batch_size": 25,
      "sleep_seconds": 180,
      "page_count": 100,
    }

  def get_context_data(self, **kwargs):
    """컨텍스트 데이터 추가"""
    context = super().get_context_data(**kwargs)
    context["opts"] = self.model_admin.model._meta

    # 통계 정보 제공
    total_companies = Company.objects.filter(corp_code__isnull=False).exclude(corp_code="").count()
    listed_companies = Company.objects.filter(
      corp_code__isnull=False,
      stocks__is_listed=True,
    ).exclude(corp_code="").distinct().count()
    non_financial_companies = Company.objects.filter(
      corp_code__isnull=False,
      is_financial=False,
    ).exclude(corp_code="").count()
    listed_non_financial = Company.objects.filter(
      corp_code__isnull=False,
      stocks__is_listed=True,
      is_financial=False,
    ).exclude(corp_code="").distinct().count()

    context["stats"] = {
      "total": total_companies,
      "listed": listed_companies,
      "non_financial": non_financial_companies,
      "listed_non_financial": listed_non_financial,
    }

    return context

  def form_valid(self, form: BulkFinancialStatementIngestAndRegenerationForm) -> HttpResponse:
    """폼 검증 성공 시 배치 Task 실행"""
    fiscal_year = form.cleaned_data.get("fiscal_year")
    quarters = self._parse_int_list(form.cleaned_data.get("quarters"))
    is_listed_only = form.cleaned_data.get("is_listed_only")
    is_financial_excluded = form.cleaned_data.get("is_financial_excluded")
    batch_size = form.cleaned_data.get("batch_size")
    sleep_seconds = form.cleaned_data.get("sleep_seconds")
    page_count = form.cleaned_data.get("page_count")

    try:
      # 단일 배치 Task 실행 (내부에서 배치 단위로 나누어 처리)
      task = bulk_ingest_and_regenerate_financial_statements.delay(
        fiscal_year=fiscal_year,
        quarters=quarters,
        is_listed_only=is_listed_only,
        is_financial_excluded=is_financial_excluded,
        batch_size=batch_size,
        sleep_seconds=sleep_seconds,
        page_count=page_count,
      )

      # 예상 배치 수 계산
      from django.db.models import Q
      queryset = Company.objects.filter(corp_code__isnull=False).exclude(corp_code="")
      if is_listed_only:
        queryset = queryset.filter(stocks__is_listed=True).distinct()
      if is_financial_excluded:
        queryset = queryset.filter(Q(is_financial=False) | Q(is_financial__isnull=True))

      total_companies = queryset.count()
      estimated_batches = (total_companies + batch_size - 1) // batch_size
      estimated_hours = (estimated_batches - 1) * sleep_seconds / 3600

      messages.success(
        self.request,
        _(
          "Queued bulk financial statement collection for %(year)d (quarters: %(quarters)s). "
          "Task ID: %(task_id)s. Estimated: %(companies)d companies in %(batches)d batches, "
          "~%(hours).1f hours for batch delays (batch_size=%(batch_size)d, sleep=%(sleep)ds)."
        ) % {
          "year": fiscal_year,
          "quarters": ",".join(str(q) for q in quarters),
          "task_id": task.id,
          "companies": total_companies,
          "batches": estimated_batches,
          "hours": estimated_hours,
          "batch_size": batch_size,
          "sleep": sleep_seconds,
        },
      )

      # 리스트 페이지로 리다이렉트
      return redirect("admin:companies_company_changelist")

    except Exception as e:
      logger.exception(f"전체 회사 재무제표 수집 실패: {e}")
      messages.error(self.request, f"수집 실패: {str(e)}")
      return self.form_invalid(form)

  @staticmethod
  def _parse_int_list(value: str) -> list[int]:
    """쉼표로 구분된 문자열을 정수 리스트로 파싱"""
    parts = [segment.strip() for segment in value.split(",") if segment.strip()]
    return [int(p) for p in parts]
