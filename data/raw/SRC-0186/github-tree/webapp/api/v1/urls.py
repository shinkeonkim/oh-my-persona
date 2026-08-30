from django.urls import include, path

urlpatterns = [
    path("health-check/", include("api.v1.health_check.urls")),
    path("users/", include("api.v1.users.urls")),
    path("profiles/", include("api.v1.profiles.urls")),
    path("matchmakings/", include("api.v1.matchmakings.urls")),
    path("saju/", include("api.v1.saju.urls")),
    path("", include("api.v1.payments.urls")),
]
