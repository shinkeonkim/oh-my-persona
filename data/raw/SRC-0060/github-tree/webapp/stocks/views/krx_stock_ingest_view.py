"""
KRX Stock Ingest View
"""

import logging

from django import forms
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from stocks.tasks.krx_stock_ingest_task import ingest_krx_stock_data
from unfold.views import UnfoldModelAdminViewMixin

logger = logging.getLogger(__name__)


class KrxStockIngestForm(forms.Form):
  """KRX 주식 정보 수집 폼"""

  trade_date = forms.DateField(
    label=_("거래일"),
    required=False,
    widget=forms.DateInput(attrs={
      "type": "date",
      "class": "form-control"
    }),
    help_text=_("수집할 거래일을 선택하세요 (선택하지 않으면 현재일 기준)"),
  )


class KrxStockIngestView(UnfoldModelAdminViewMixin, FormView):
  """KRX 주식 정보 수집 커스텀 페이지"""

  title = _("KRX 주식 정보 수집")
  permission_required = ()
  template_name = "admin/stocks/stock/krx_ingest_form.html"
  form_class = KrxStockIngestForm

  def form_valid(self, form: KrxStockIngestForm) -> HttpResponse:
    """폼 검증 성공 시 수집 실행"""
    trade_date = form.cleaned_data.get("trade_date")

    try:
      # trade_date가 입력되지 않으면 None 전달 (task에서 현재일 사용)
      trade_date_str = trade_date.strftime("%Y%m%d") if trade_date else None

      # Celery task 실행
      task = ingest_krx_stock_data.delay(trade_date=trade_date_str)

      # 성공 메시지
      if trade_date_str:
        message = _("KRX 주식 정보 수집 작업이 시작되었습니다. 거래일: %(date)s, Task ID: %(task_id)s") % {
          "date": trade_date,
          "task_id": task.id
        }
      else:
        message = _("KRX 주식 정보 수집 작업이 시작되었습니다 (현재일 기준). Task ID: %(task_id)s") % {"task_id": task.id}

      messages.success(self.request, message)

      # 리스트 페이지로 리다이렉트
      return redirect("admin:stocks_stock_changelist")

    except Exception as e:
      logger.error(f"KRX 주식 정보 수집 실패: {e}")
      messages.error(self.request, f"수집 실패: {str(e)}")
      return self.form_invalid(form)

  def get_context_data(self, **kwargs):
    """컨텍스트 데이터 추가"""
    context = super().get_context_data(**kwargs)
    context["opts"] = self.model_admin.model._meta
    return context
