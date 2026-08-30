from django.urls import path

from games.views import RankingAPIView, RankingDisplayView

app_name = "games"

urlpatterns = [
    path("ranking/", RankingDisplayView.as_view(), name="ranking-display"),
    path("api/ranking/", RankingAPIView.as_view(), name="ranking-api"),
]
