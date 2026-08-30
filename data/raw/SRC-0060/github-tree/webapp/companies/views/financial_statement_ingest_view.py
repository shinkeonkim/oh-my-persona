"""
Financial Statement Ingest View
"""

import logging

from django import forms
from django.contrib import messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from financial_statements.tasks import ingest_financial_statements
from unfold.views import UnfoldModelAdminViewMixin

from companies.models import Company

logger = logging.getLogger(__name__)


class FinancialStatementIngestForm(forms.Form):
  """재무제표 수집 폼"""

  years = forms.CharField(
    label=_("Years"),
    widget=forms.TextInput(attrs={"class": "form-control"}),
    help_text=_("Enter comma-separated fiscal years, e.g. 2023,2024"),
  )
  quarters = forms.CharField(
    label=_("Quarters"),
    widget=forms.TextInput(attrs={"class": "form-control"}),
    help_text=_("Enter comma-separated quarters (1-4), e.g. 1,2,3,4"),
  )
  page_count = forms.IntegerField(
    label=_("Page count"),
    min_value=1,
    max_value=1000,
    initial=100,
    widget=forms.NumberInput(attrs={"class": "form-control"}),
    help_text=_("Maximum number of rows to request per DART response."),
  )


class FinancialStatementIngestView(UnfoldModelAdminViewMixin, FormView):
  """재무제표 정보 수집 커스텀 페이지"""

  title = _("Queue financial statement ingestion")
  permission_required = ()
  template_name = "admin/companies/company/financial_statement_ingest_form.html"
  form_class = FinancialStatementIngestForm

  def get_initial(self):
    """초기값 설정"""
    return {
      "years": str(timezone.now().year),
      "quarters": "1,2,3,4",
      "page_count": 100,
    }

  def get_selected_companies(self):
    """선택된 회사 목록 가져오기"""
    # POST에서 체크박스로 선택된 경우
    post_ids = self.request.POST.getlist("_selected_action")

    # GET에서 쉼표로 구분된 ids 파라미터로 전달된 경우
    get_ids_str = self.request.GET.get("ids", "")
    get_ids = [id.strip() for id in get_ids_str.split(",") if id.strip()] if get_ids_str else []

    selected_ids = post_ids or get_ids

    if selected_ids:
      companies = list(Company.objects.filter(pk__in=selected_ids))
      return companies
    return []

  def get_context_data(self, **kwargs):
    """컨텍스트 데이터 추가"""
    context = super().get_context_data(**kwargs)
    context["opts"] = self.model_admin.model._meta
    context["companies"] = self.get_selected_companies()

    # selected_ids를 리스트 형태로 전달 (템플릿에서 사용)
    post_ids = self.request.POST.getlist("_selected_action")
    get_ids_str = self.request.GET.get("ids", "")
    get_ids = [id.strip() for id in get_ids_str.split(",") if id.strip()] if get_ids_str else []
    context["selected_ids"] = post_ids or get_ids

    context["action_checkbox_name"] = ACTION_CHECKBOX_NAME
    context["action"] = self.request.POST.get("action") or "queue_financial_statement_ingest"
    return context

  def form_valid(self, form: FinancialStatementIngestForm) -> HttpResponse:
    """폼 검증 성공 시 수집 실행"""
    years = self._parse_int_list(form.cleaned_data.get("years"))
    quarters = self._parse_int_list(form.cleaned_data.get("quarters"))
    page_count = form.cleaned_data.get("page_count")
    companies = self.get_selected_companies()

    if not companies:
      messages.warning(
        self.request,
        _("Select at least one company to queue financial statement ingestion."),
      )
      return redirect("admin:companies_company_changelist")

    try:
      async_results = []
      for company in companies:
        task = ingest_financial_statements.delay(
          company_id=company.pk,
          years=years,
          quarters=quarters,
          page_count=page_count,
        )
        async_results.append((company, task.id))

      if async_results:
        summary = ", ".join(f"{company.name}→{task_id}" for company, task_id in async_results)
        messages.success(
          self.request,
          _(
            "Queued financial statement ingest for %(count)d companies (%(summary)s)."
            " Years=%(years)s Quarters=%(quarters)s"
          ) % {
            "count": len(async_results),
            "summary": summary,
            "years": ",".join(str(y) for y in years),
            "quarters": ",".join(str(q) for q in quarters),
          },
        )

      # 리스트 페이지로 리다이렉트
      return redirect("admin:companies_company_changelist")

    except Exception as e:
      logger.error(f"재무제표 정보 수집 실패: {e}")
      messages.error(self.request, f"수집 실패: {str(e)}")
      return self.form_invalid(form)

  @staticmethod
  def _parse_int_list(value: str) -> list[int]:
    """쉼표로 구분된 문자열을 정수 리스트로 파싱"""
    parts = [segment.strip() for segment in value.split(",") if segment.strip()]
    return [int(p) for p in parts]
