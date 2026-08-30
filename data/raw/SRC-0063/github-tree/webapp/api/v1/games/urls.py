from django.urls import path

from .views import (
    BBStarFinishAPIView,
    BBStarStartAPIView,
    GameListAPIView,
    KidsTrafficFinishAPIView,
    KidsTrafficStartAPIView,
)

app_name = "api.v1.games"

urlpatterns = [
    path("", GameListAPIView.as_view(), name="game_list"),
    path("bb-star/start/", BBStarStartAPIView.as_view(), name="bb_star_start"),
    path("bb-star/finish/", BBStarFinishAPIView.as_view(), name="bb_star_finish"),
    path("kids-traffic/start/", KidsTrafficStartAPIView.as_view(), name="kids_traffic_start"),
    path("kids-traffic/finish/", KidsTrafficFinishAPIView.as_view(), name="kids_traffic_finish"),
]
