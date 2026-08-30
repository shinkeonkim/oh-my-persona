"""
Financial Statement Regeneration View
"""

import logging

from django import forms
from django.contrib import messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from financial_statements.tasks import regenerate_financial_statements
from unfold.views import UnfoldModelAdminViewMixin

from companies.models import Company

logger = logging.getLogger(__name__)


class FinancialStatementRegenerationForm(forms.Form):
  """재무제표 재생성 폼"""

  years = forms.CharField(
    label=_("Years (optional)"),
    required=False,
    widget=forms.TextInput(attrs={
      "class": "form-control",
      "placeholder": "2023,2024 (비워두면 전체)"
    }),
    help_text=_("Enter comma-separated fiscal years, e.g. 2023,2024. Leave empty to regenerate all years."),
  )
  quarters = forms.CharField(
    label=_("Quarters (optional)"),
    required=False,
    widget=forms.TextInput(attrs={
      "class": "form-control",
      "placeholder": "1,2,3,4 (비워두면 전체)"
    }),
    help_text=_("Enter comma-separated quarters (1-4), e.g. 1,2,3,4. Leave empty to regenerate all quarters."),
  )


class FinancialStatementRegenerationView(UnfoldModelAdminViewMixin, FormView):
  """재무제표 재생성 커스텀 페이지"""

  title = _("Regenerate financial statements")
  permission_required = ()
  template_name = "admin/companies/company/financial_statement_regeneration_form.html"
  form_class = FinancialStatementRegenerationForm

  def get_initial(self):
    """초기값 설정"""
    return {
      "years": "",
      "quarters": "",
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
    context["action"] = self.request.POST.get("action") or "queue_financial_statement_regeneration"
    return context

  def form_valid(self, form: FinancialStatementRegenerationForm) -> HttpResponse:
    """폼 검증 성공 시 재생성 실행"""
    years_str = form.cleaned_data.get("years", "").strip()
    quarters_str = form.cleaned_data.get("quarters", "").strip()

    years = self._parse_int_list(years_str) if years_str else []
    quarters = self._parse_int_list(quarters_str) if quarters_str else []

    companies = self.get_selected_companies()

    if not companies:
      messages.warning(
        self.request,
        _("Select at least one company to regenerate financial statements."),
      )
      return redirect("admin:companies_company_changelist")

    try:
      async_results = []

      for company in companies:
        # 연도/분기별로 Task 실행
        if years and quarters:
          # 특정 연도/분기 조합
          for year in years:
            for quarter in quarters:
              task = regenerate_financial_statements.delay(
                company_id=company.pk,
                year=year,
                quarter=quarter,
              )
              async_results.append((company, f"{year}Q{quarter}", task.id))
        elif years:
          # 특정 연도 전체
          for year in years:
            task = regenerate_financial_statements.delay(
              company_id=company.pk,
              year=year,
            )
            async_results.append((company, f"{year}(전체)", task.id))
        elif quarters:
          # 특정 분기만 (모든 연도)
          for quarter in quarters:
            task = regenerate_financial_statements.delay(
              company_id=company.pk,
              quarter=quarter,
            )
            async_results.append((company, f"Q{quarter}(전체)", task.id))
        else:
          # 전체 재생성
          task = regenerate_financial_statements.delay(company_id=company.pk, )
          async_results.append((company, "전체", task.id))

      if async_results:
        summary = ", ".join(f"{company.name}({period})→{task_id}" for company, period, task_id in async_results)
        messages.success(
          self.request,
          _("Queued financial statement regeneration for %(count)d task(s): %(summary)s") % {
            "count": len(async_results),
            "summary": summary,
          },
        )

      # 리스트 페이지로 리다이렉트
      return redirect("admin:companies_company_changelist")

    except Exception as e:
      logger.error(f"재무제표 재생성 실패: {e}")
      messages.error(self.request, f"재생성 실패: {str(e)}")
      return self.form_invalid(form)

  @staticmethod
  def _parse_int_list(value: str) -> list[int]:
    """쉼표로 구분된 문자열을 정수 리스트로 파싱"""
    if not value:
      return []
    parts = [segment.strip() for segment in value.split(",") if segment.strip()]
    return [int(p) for p in parts]
