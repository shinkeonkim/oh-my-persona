from django.urls import path

from .views import TodaySajuScoreAPIView

urlpatterns = [
    path("today-score/", TodaySajuScoreAPIView.as_view(), name="today_saju_score"),
]
