from django.urls import include, path

app_name = "v1"

urlpatterns = [
    path("", include("api.v1.meme.urls")),
    path("", include("api.v1.account.urls")),
    path("", include("api.v1.tag.urls")),
    path("", include("api.v1.bookmark.urls")),
]
