"""
DART Company Ingest View
"""

import logging

from django import forms
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from unfold.views import UnfoldModelAdminViewMixin

from companies.tasks.dart_company_ingest_task import ingest_dart_company_data

logger = logging.getLogger(__name__)


class DartCompanyIngestForm(forms.Form):
  """DART 회사 정보 수집 폼"""

  # 폼 필드 없음 - 단순히 수집 작업을 트리거하는 용도
  pass


class DartCompanyIngestView(UnfoldModelAdminViewMixin, FormView):
  """DART 회사 정보 수집 커스텀 페이지"""

  title = _("DART 회사 정보 수집")
  permission_required = ()
  template_name = "admin/companies/company/dart_ingest_form.html"
  form_class = DartCompanyIngestForm

  def form_valid(self, form: DartCompanyIngestForm) -> HttpResponse:
    """폼 검증 성공 시 수집 실행"""
    try:
      # Celery task 실행 (파라미터 없음)
      task = ingest_dart_company_data.delay()

      # 성공 메시지
      message = _("DART 회사 정보 수집 작업이 시작되었습니다. Task ID: %(task_id)s") % {"task_id": task.id}
      messages.success(self.request, message)

      # 리스트 페이지로 리다이렉트
      return redirect("admin:companies_company_changelist")

    except Exception as e:
      logger.error(f"DART 회사 정보 수집 실패: {e}")
      messages.error(self.request, f"수집 실패: {str(e)}")
      return self.form_invalid(form)

  def get_context_data(self, **kwargs):
    """컨텍스트 데이터 추가"""
    context = super().get_context_data(**kwargs)
    context["opts"] = self.model_admin.model._meta
    return context
