from django.urls import include, path

urlpatterns = [
    path("health-check/", include("api.v1.health_check.urls")),
    path("users/", include("api.v1.users.urls")),
    path("reports/", include("api.v1.reports.urls")),
    path("games/", include("api.v1.games.urls")),
]
