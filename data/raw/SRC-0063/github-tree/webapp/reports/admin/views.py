from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import FormView

from reports.admin.forms import SendReportEmailForm
from reports.models import Report
from reports.tasks.report_email_task import send_report_email_task
from unfold.views import UnfoldModelAdminViewMixin

from users.models import BotToken

FRONTEND_REPORT_URL = settings.FRONTEND_REPORT_URL


class SendReportEmailView(UnfoldModelAdminViewMixin, FormView):
    """레포트 이메일 전송 Custom Page"""

    title = "레포트 이메일 전송"
    permission_required = ()
    template_name = "admin/reports/report/send_email_page.html"
    form_class = SendReportEmailForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report_id = self.kwargs.get("object_id")
        report = get_object_or_404(Report, pk=report_id)
        context["report"] = report
        return context

    def form_valid(self, form):
        """폼이 유효할 때 이메일 전송"""
        report_id = self.kwargs.get("object_id")
        report = get_object_or_404(Report, pk=report_id)
        to_email = form.cleaned_data["email"]

        # BOT 토큰 생성
        bot_token = BotToken.create_for_report(report.user)

        # 프론트엔드 URL 생성
        site_url = f"{FRONTEND_REPORT_URL}?BOT_TOKEN={bot_token.token}"

        # 비동기 이메일 전송 작업 시작
        send_report_email_task.delay(
            to_email=to_email,
            site_url=site_url,
            bot_token_id=bot_token.id,
        )

        # 성공 메시지 표시
        messages.success(
            self.request,
            f"레포트 이메일 전송이 시작되었습니다. ({to_email})",
        )

        # detail 페이지로 리다이렉트
        return redirect(reverse("admin:reports_report_change", args=[report_id]))
