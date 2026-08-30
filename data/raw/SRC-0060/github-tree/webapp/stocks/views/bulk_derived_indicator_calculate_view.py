"""
Bulk Derived Indicator Calculate View

Admin에서 모든 Stock에 대해 특정 연도의 파생지표 계산 Task를 실행하는 뷰
"""

import logging

from django import forms
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from stocks.models import Stock
from stocks.tasks import calculate_derived_indicators_for_stock
from unfold.views import UnfoldModelAdminViewMixin

logger = logging.getLogger(__name__)


class BulkDerivedIndicatorCalculateForm(forms.Form):
  """전체 종목 파생지표 계산 폼"""

  fiscal_year = forms.IntegerField(
    label=_("Fiscal Year"),
    min_value=2000,
    max_value=2100,
    initial=timezone.now().year,
    widget=forms.NumberInput(attrs={"class": "form-control"}),
    help_text=_("Enter fiscal year (e.g., 2024) to calculate all quarters for that year."),
    required=True,
  )
  is_listed_only = forms.BooleanField(
    label=_("Listed stocks only"),
    initial=True,
    required=False,
    help_text=_("If checked, only calculates for listed stocks. Uncheck to include delisted stocks."),
  )
  is_primary_only = forms.BooleanField(
    label=_("Primary stocks only"),
    initial=True,
    required=False,
    help_text=_("If checked, only calculates for primary stocks (보통주). Uncheck to include preferred stocks."),
  )


class BulkDerivedIndicatorCalculateView(UnfoldModelAdminViewMixin, FormView):
  """전체 종목 파생지표 계산 커스텀 페이지"""

  title = _("Calculate Derived Indicators for All Stocks")
  permission_required = ()
  template_name = "admin/stocks/stock/bulk_derived_indicator_calculate_form.html"
  form_class = BulkDerivedIndicatorCalculateForm

  def get_initial(self):
    """초기값 설정"""
    return {
      "fiscal_year": timezone.now().year,
      "is_listed_only": True,
      "is_primary_only": True,
    }

  def get_context_data(self, **kwargs):
    """컨텍스트 데이터 추가"""
    context = super().get_context_data(**kwargs)
    context["opts"] = self.model_admin.model._meta

    # 통계 정보 제공
    total_stocks = Stock.objects.count()
    listed_stocks = Stock.objects.filter(is_listed=True).count()
    primary_stocks = Stock.objects.filter(is_primary=True).count()
    listed_primary_stocks = Stock.objects.filter(is_listed=True, is_primary=True).count()

    context["stats"] = {
      "total": total_stocks,
      "listed": listed_stocks,
      "primary": primary_stocks,
      "listed_primary": listed_primary_stocks,
    }

    return context

  def form_valid(self, form: BulkDerivedIndicatorCalculateForm) -> HttpResponse:
    """폼 검증 성공 시 계산 실행"""
    fiscal_year = form.cleaned_data.get("fiscal_year")
    is_listed_only = form.cleaned_data.get("is_listed_only")
    is_primary_only = form.cleaned_data.get("is_primary_only")

    # Stock 필터링
    queryset = Stock.objects.select_related("company")

    if is_listed_only:
      queryset = queryset.filter(is_listed=True)

    if is_primary_only:
      queryset = queryset.filter(is_primary=True)

    stocks = list(queryset)

    if not stocks:
      messages.warning(
        self.request,
        _("No stocks found matching the criteria."),
      )
      return redirect("admin:stocks_stock_changelist")

    try:
      async_results = []

      # 각 종목에 대해 해당 연도의 모든 분기 계산
      for stock in stocks:
        for quarter in range(1, 5):
          task = calculate_derived_indicators_for_stock.delay(
            stock_id=stock.pk,
            fiscal_year=fiscal_year,
            fiscal_quarter=quarter,
          )
          async_results.append((stock, task.id, f"{fiscal_year}Q{quarter}"))

      if async_results:
        # 요약 메시지 생성
        stock_count = len(stocks)
        task_count = len(async_results)

        # 처음 3개 종목만 표시
        summary_items = []
        for stock, task_id, period in async_results[:12]:  # 3종목 x 4분기 = 12개
          summary_items.append(f"{stock.code}({period})→{task_id[:8]}")

        summary = ", ".join(summary_items)
        if len(async_results) > 12:
          summary += f" ... and {len(async_results) - 12} more"

        messages.success(
          self.request,
          _(
            "Queued derived indicator calculation for %(stock_count)d stocks (%(task_count)d tasks for %(year)d). %(summary)s"
          ) % {
            "stock_count": stock_count,
            "task_count": task_count,
            "year": fiscal_year,
            "summary": summary,
          },
        )

      # 리스트 페이지로 리다이렉트
      return redirect("admin:stocks_stock_changelist")

    except Exception as e:
      logger.exception(f"전체 종목 파생지표 계산 실패: {e}")
      messages.error(self.request, f"계산 실패: {str(e)}")
      return self.form_invalid(form)
