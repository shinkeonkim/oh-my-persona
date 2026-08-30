"""
Company Disclosure Ingest View
"""

import logging
from datetime import datetime, timedelta

from django import forms
from django.contrib import messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from disclosures.tasks import ingest_company_disclosures
from unfold.views import UnfoldModelAdminViewMixin

from companies.models import Company

logger = logging.getLogger(__name__)


class DisclosureDateRangeForm(forms.Form):
  """공시 수집 날짜 범위 폼"""

  start_date = forms.DateField(
    label=_("시작 날짜"),
    widget=forms.DateInput(attrs={
      "type": "date",
      "class": "form-control"
    }),
    help_text=_("공시 수집을 시작할 날짜입니다. (YYYYMMDD 형식으로 변환되어 DART API에 전달됩니다)"),
  )

  end_date = forms.DateField(
    label=_("종료 날짜"),
    widget=forms.DateInput(attrs={
      "type": "date",
      "class": "form-control"
    }),
    help_text=_("공시 수집을 종료할 날짜입니다. (YYYYMMDD 형식으로 변환되어 DART API에 전달됩니다)"),
  )

  def clean(self):
    cleaned_data = super().clean()
    start_date = cleaned_data.get("start_date")
    end_date = cleaned_data.get("end_date")

    if start_date and end_date:
      if start_date > end_date:
        raise forms.ValidationError(_("시작 날짜는 종료 날짜보다 이전이어야 합니다."))

      # 최대 1년 범위 체크
      if (end_date - start_date).days > 365:
        raise forms.ValidationError(_("날짜 범위는 최대 1년까지 가능합니다."))

    return cleaned_data


class DisclosureIngestView(UnfoldModelAdminViewMixin, FormView):
  """공시 정보 수집 커스텀 페이지"""

  title = _("Queue disclosure ingestion")
  permission_required = ()
  template_name = "admin/companies/company/disclosure_ingest_form.html"
  form_class = DisclosureDateRangeForm

  def get_initial(self):
    """초기값 설정 - 기본값: 최근 30일"""
    today = timezone.now().date()
    start_date = today - timedelta(days=30)
    return {
      "start_date": start_date,
      "end_date": today,
    }

  def get_selected_companies(self):
    """선택된 회사 목록 가져오기"""
    selected_ids = self.request.POST.getlist("_selected_action") or self.request.GET.getlist("ids")
    if selected_ids:
      return list(Company.objects.filter(pk__in=selected_ids))
    return []

  def get_context_data(self, **kwargs):
    """컨텍스트 데이터 추가"""
    context = super().get_context_data(**kwargs)
    context["opts"] = self.model_admin.model._meta
    context["companies"] = self.get_selected_companies()
    context["selected_ids"] = self.request.POST.getlist("_selected_action") or self.request.GET.getlist("ids")
    context["action_checkbox_name"] = ACTION_CHECKBOX_NAME
    context["action"] = self.request.POST.get("action") or "queue_disclosure_ingest"
    return context

  def form_valid(self, form: DisclosureDateRangeForm) -> HttpResponse:
    """폼 검증 성공 시 수집 실행"""
    start_date = form.cleaned_data.get("start_date")
    end_date = form.cleaned_data.get("end_date")
    companies = self.get_selected_companies()

    if not companies:
      messages.warning(
        self.request,
        _("Select at least one company to queue disclosure ingestion."),
      )
      return redirect("admin:companies_company_changelist")

    try:
      # Date를 YYYYMMDD 문자열로 변환
      begin_date = start_date.strftime("%Y%m%d")
      end_date_str = end_date.strftime("%Y%m%d")

      async_results = []

      for company in companies:
        task = ingest_company_disclosures.delay(
          company_id=company.pk,
          begin_date=begin_date,
          end_date=end_date_str,
        )
        async_results.append((company, task.id))

      if async_results:
        summary = ", ".join(f"{company.name}→{task_id}" for company, task_id in async_results)
        messages.success(
          self.request,
          _("Queued disclosure ingest for %(count)d companies (%(summary)s, from %(start)s to %(end)s).") % {
            "count": len(async_results),
            "summary": summary,
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
          },
        )

      # 리스트 페이지로 리다이렉트
      return redirect("admin:companies_company_changelist")

    except Exception as e:
      logger.error(f"공시 정보 수집 실패: {e}")
      messages.error(self.request, f"수집 실패: {str(e)}")
      return self.form_invalid(form)
