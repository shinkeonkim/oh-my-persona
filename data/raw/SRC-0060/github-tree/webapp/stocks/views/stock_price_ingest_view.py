"""
Stock Price Ingest View
"""

import logging
from datetime import datetime, timedelta

from django import forms
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from stocks.tasks import (
  ingest_stock_prices_for_date,
  ingest_stock_prices_for_date_range,
)
from unfold.views import UnfoldModelAdminViewMixin

logger = logging.getLogger(__name__)


class StockPriceIngestForm(forms.Form):
  """주식 가격 수집 폼"""

  ingest_type = forms.ChoiceField(
    label=_("수집 유형"),
    choices=[
      ("single", _("단일 날짜")),
      ("range", _("날짜 범위")),
    ],
    initial="single",
    widget=forms.RadioSelect,
  )

  trade_date = forms.DateField(
    label=_("거래일"),
    initial=lambda: (datetime.now() - timedelta(days=1)).date(),
    widget=forms.DateInput(attrs={
      "type": "date",
      "class": "form-control"
    }),
    help_text=_("수집할 거래일을 선택하세요 (단일 날짜 수집 시)"),
  )

  start_date = forms.DateField(
    label=_("시작일"),
    required=False,
    widget=forms.DateInput(attrs={
      "type": "date",
      "class": "form-control"
    }),
    help_text=_("수집 시작일 (날짜 범위 수집 시)"),
  )

  end_date = forms.DateField(
    label=_("종료일"),
    required=False,
    widget=forms.DateInput(attrs={
      "type": "date",
      "class": "form-control"
    }),
    help_text=_("수집 종료일 (날짜 범위 수집 시)"),
  )

  def clean(self):
    cleaned_data = super().clean()
    ingest_type = cleaned_data.get("ingest_type")

    if ingest_type == "range":
      start_date = cleaned_data.get("start_date")
      end_date = cleaned_data.get("end_date")

      if not start_date or not end_date:
        raise forms.ValidationError(_("날짜 범위 수집 시 시작일과 종료일을 모두 입력해야 합니다."))

      if start_date > end_date:
        raise forms.ValidationError(_("시작일은 종료일보다 이전이어야 합니다."))

    return cleaned_data


class StockPriceIngestView(UnfoldModelAdminViewMixin, FormView):
  """주식 가격 수집 커스텀 페이지"""

  title = _("주식 가격 데이터 수집")
  permission_required = ()
  template_name = "admin/companies/stockprice/ingest_form.html"
  form_class = StockPriceIngestForm

  def form_valid(self, form: StockPriceIngestForm) -> HttpResponse:
    """폼 검증 성공 시 수집 실행"""
    ingest_type = form.cleaned_data.get("ingest_type")

    try:
      if ingest_type == "single":
        # 단일 날짜 수집
        trade_date = form.cleaned_data["trade_date"]
        task = ingest_stock_prices_for_date.delay(trade_date_str=trade_date.strftime("%Y-%m-%d"), markets=None)

        message = _("주식 가격 수집 작업이 시작되었습니다. 날짜: %(date)s, Task ID: %(task_id)s") % {
          "date": trade_date,
          "task_id": task.id
        }
      else:
        # 날짜 범위 수집
        start_date = form.cleaned_data["start_date"]
        end_date = form.cleaned_data["end_date"]
        task = ingest_stock_prices_for_date_range.delay(
          start_date_str=start_date.strftime("%Y-%m-%d"), end_date_str=end_date.strftime("%Y-%m-%d"), markets=None
        )

        message = _("주식 가격 범위 수집 작업이 시작되었습니다. 기간: %(start)s ~ %(end)s, Task ID: %(task_id)s") % {
          "start": start_date,
          "end": end_date,
          "task_id": task.id
        }

      messages.success(self.request, message)

      # 리스트 페이지로 리다이렉트
      return redirect("admin:stocks_stockprice_changelist")

    except Exception as e:
      logger.error(f"주식 가격 수집 실패: {e}")
      messages.error(self.request, f"수집 실패: {str(e)}")
      return self.form_invalid(form)

  def get_context_data(self, **kwargs):
    """컨텍스트 데이터 추가"""
    context = super().get_context_data(**kwargs)
    context["opts"] = self.model_admin.model._meta
    return context
