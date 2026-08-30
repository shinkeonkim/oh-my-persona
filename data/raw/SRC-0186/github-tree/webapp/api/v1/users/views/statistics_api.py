from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse

from users.services.statistics import UserRegistrationStatistics


@staff_member_required
def registration_statistics_api(request):
    """회원가입 통계 API (AJAX용)"""
    period = request.GET.get("period", "daily")
    oauth_only = request.GET.get("oauth_only", "true").lower() == "true"

    if period == "daily":
        data = UserRegistrationStatistics.get_daily_registrations(oauth_only=oauth_only)
    elif period == "monthly":
        data = UserRegistrationStatistics.get_monthly_registrations(oauth_only=oauth_only)
    elif period == "quarterly":
        data = UserRegistrationStatistics.get_quarterly_registrations(oauth_only=oauth_only)
    else:
        data = []

    return JsonResponse({"data": data})
