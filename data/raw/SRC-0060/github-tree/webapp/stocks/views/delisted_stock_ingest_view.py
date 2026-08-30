"""
Delisted Stock Ingest View

상장 폐지 종목 정보 수집 커스텀 페이지
"""

import logging
from datetime import date, timedelta

from django import forms
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import FormView

from unfold.views import UnfoldModelAdminViewMixin

logger = logging.getLogger(__name__)


class DelistedStockIngestForm(forms.Form):
  """상장 폐지 종목 정보 수집 테스트 폼"""

  start_date = forms.DateField(
    label="조회 시작일",
    initial=date.today() - timedelta(days=365),
    widget=forms.DateInput(attrs={
      "type": "date",
      "class": "form-control"
    }),
    help_text="YYYY-MM-DD 형식",
  )
  end_date = forms.DateField(
    label="조회 종료일",
    initial=date.today(),
    widget=forms.DateInput(attrs={
      "type": "date",
      "class": "form-control"
    }),
    help_text="YYYY-MM-DD 형식",
  )
  market_id = forms.ChoiceField(
    label="시장 구분",
    choices=[
      ("ALL", "전체"),
      ("STK", "KOSPI"),
      ("KSQ", "KOSDAQ"),
    ],
    initial="ALL",
    widget=forms.Select(attrs={"class": "form-control"}),
    help_text="조회할 시장을 선택하세요",
  )


class DelistedStockIngestView(UnfoldModelAdminViewMixin, FormView):
  """상장 폐지 종목 정보 수집 테스트 커스텀 페이지"""

  title = "상장 폐지 종목 정보 수집 테스트"
  permission_required = ()
  template_name = "admin/companies/delisted_stock_ingest.html"
  form_class = DelistedStockIngestForm

  def form_valid(self, form: DelistedStockIngestForm) -> HttpResponse:
    """폼 검증 성공 시 수집 실행"""
    start_date = form.cleaned_data["start_date"]
    end_date = form.cleaned_data["end_date"]
    market_id = form.cleaned_data["market_id"]

    try:
      from stocks.tasks import ingest_delisted_stocks_long_period

      # 비동기 태스크 실행
      ingest_delisted_stocks_long_period.delay(
        start_date=start_date.strftime("%Y%m%d"),
        end_date=end_date.strftime("%Y%m%d"),
        market_id=market_id,
      )

      # 성공 메시지
      messages.success(self.request, "상장 폐지 종목 정보 수집을 시작했습니다.")

      # 리스트 페이지로 리다이렉트
      return redirect("admin:stocks_delistedstock_changelist")

    except Exception as e:
      logger.error(f"상장 폐지 종목 정보 수집 실패: {e}")
      messages.error(self.request, f"수집 실패: {str(e)}")
      return self.form_invalid(form)

  def get_context_data(self, **kwargs):
    """컨텍스트 데이터 추가"""
    context = super().get_context_data(**kwargs)
    context["opts"] = self.model_admin.model._meta
    return context
