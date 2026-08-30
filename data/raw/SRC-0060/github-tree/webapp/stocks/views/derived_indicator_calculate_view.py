"""
Derived Indicator Calculate View

Admin에서 특정 Stock과 분기에 대해 파생지표 계산 Task를 실행하는 뷰
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

from stocks.models import Stock
from stocks.tasks import calculate_derived_indicators_for_stock
from unfold.views import UnfoldModelAdminViewMixin

logger = logging.getLogger(__name__)


class DerivedIndicatorCalculateForm(forms.Form):
  """파생지표 계산 폼"""

  fiscal_year = forms.IntegerField(
    label=_("Fiscal Year"),
    min_value=2000,
    max_value=2100,
    initial=timezone.now().year,
    widget=forms.NumberInput(attrs={"class": "form-control"}),
    help_text=_("Enter fiscal year (e.g., 2024). Leave empty to calculate all available periods."),
    required=False,
  )
  fiscal_quarter = forms.ChoiceField(
    label=_("Fiscal Quarter"),
    choices=[("", "All")] + [(str(q), f"Q{q}") for q in range(1, 5)],
    widget=forms.Select(attrs={"class": "form-control"}),
    help_text=_("Select quarter (1-4). Leave empty to calculate all quarters."),
    required=False,
  )
  calculate_all_periods = forms.BooleanField(
    label=_("Calculate all available periods"),
    initial=False,
    required=False,
    help_text=_("If checked, ignores year/quarter and calculates for all periods with financial statements."),
  )


class DerivedIndicatorCalculateView(UnfoldModelAdminViewMixin, FormView):
  """파생지표 계산 커스텀 페이지"""

  title = _("Calculate Derived Indicators")
  permission_required = ()
  template_name = "admin/stocks/stock/derived_indicator_calculate_form.html"
  form_class = DerivedIndicatorCalculateForm

  def get_initial(self):
    """초기값 설정"""
    return {
      "fiscal_year": timezone.now().year,
      "fiscal_quarter": "",
      "calculate_all_periods": False,
    }

  def get_selected_stocks(self):
    """선택된 종목 목록 가져오기"""
    post_ids = self.request.POST.getlist("_selected_action")

    # GET에서 쉼표로 구분된 ids 파라미터로 전달된 경우
    get_ids_str = self.request.GET.get("ids", "")
    get_ids = [id.strip() for id in get_ids_str.split(",") if id.strip()] if get_ids_str else []

    selected_ids = post_ids or get_ids

    if selected_ids:
      return list(Stock.objects.filter(pk__in=selected_ids).select_related("company"))
    return []

  def get_context_data(self, **kwargs):
    """컨텍스트 데이터 추가"""
    context = super().get_context_data(**kwargs)
    context["opts"] = self.model_admin.model._meta
    context["stocks"] = self.get_selected_stocks()

    post_ids = self.request.POST.getlist("_selected_action")
    get_ids_str = self.request.GET.get("ids", "")
    get_ids = [id.strip() for id in get_ids_str.split(",") if id.strip()] if get_ids_str else []
    context["selected_ids"] = post_ids or get_ids

    context["action_checkbox_name"] = ACTION_CHECKBOX_NAME
    context["action"] = self.request.POST.get("action") or "queue_derived_indicator_calculate"
    return context

  def form_valid(self, form: DerivedIndicatorCalculateForm) -> HttpResponse:
    """폼 검증 성공 시 계산 실행"""
    fiscal_year = form.cleaned_data.get("fiscal_year")
    fiscal_quarter_str = form.cleaned_data.get("fiscal_quarter")
    calculate_all = form.cleaned_data.get("calculate_all_periods")
    stocks = self.get_selected_stocks()

    if not stocks:
      messages.warning(
        self.request,
        _("Select at least one stock to calculate derived indicators."),
      )
      return redirect("admin:stocks_stock_changelist")

    fiscal_quarter = int(fiscal_quarter_str) if fiscal_quarter_str else None

    try:
      async_results = []

      for stock in stocks:
        if calculate_all:
          # 모든 기간 계산
          task = calculate_derived_indicators_for_stock.delay(stock_id=stock.pk, )
          async_results.append((stock, task.id, "all periods"))
        elif fiscal_year and fiscal_quarter:
          # 특정 연도/분기 계산
          task = calculate_derived_indicators_for_stock.delay(
            stock_id=stock.pk,
            fiscal_year=fiscal_year,
            fiscal_quarter=fiscal_quarter,
          )
          async_results.append((stock, task.id, f"{fiscal_year}Q{fiscal_quarter}"))
        elif fiscal_year:
          # 특정 연도의 모든 분기 계산
          for quarter in range(1, 5):
            task = calculate_derived_indicators_for_stock.delay(
              stock_id=stock.pk,
              fiscal_year=fiscal_year,
              fiscal_quarter=quarter,
            )
            async_results.append((stock, task.id, f"{fiscal_year}Q{quarter}"))
        else:
          # 모든 기간 계산
          task = calculate_derived_indicators_for_stock.delay(stock_id=stock.pk, )
          async_results.append((stock, task.id, "all periods"))

      if async_results:
        # 요약 메시지 생성 (처음 3개만 표시)
        summary_items = []
        for stock, task_id, period in async_results[:3]:
          summary_items.append(f"{stock.code}({period})→{task_id[:8]}")

        summary = ", ".join(summary_items)
        if len(async_results) > 3:
          summary += f" ... and {len(async_results) - 3} more"

        messages.success(
          self.request,
          _("Queued derived indicator calculation for %(count)d tasks. %(summary)s") % {
            "count": len(async_results),
            "summary": summary,
          },
        )

      # 리스트 페이지로 리다이렉트
      return redirect("admin:stocks_stock_changelist")

    except Exception as e:
      logger.exception(f"파생지표 계산 실패: {e}")
      messages.error(self.request, f"계산 실패: {str(e)}")
      return self.form_invalid(form)
