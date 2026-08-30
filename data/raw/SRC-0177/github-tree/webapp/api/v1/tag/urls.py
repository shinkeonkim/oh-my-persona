from django.urls import path

from .views import (
    FavoriteTagListAPIView,
    TagFirstLetterListAPIView,
    TagListAPIView,
    TagListByFirstLetterAPIView,
)

app_name = "api.v1.tag"

urlpatterns = [
    path("tags/", TagListAPIView.as_view(), name="tag-list"),
    path("tags/favorite/", FavoriteTagListAPIView.as_view(), name="favorite-tag-list"),
    path(
        "tags/by-first-letter/",
        TagListByFirstLetterAPIView.as_view(),
        name="tag-list-by-first-letter",
    ),
    path(
        "tags/first-letters/",
        TagFirstLetterListAPIView.as_view(),
        name="tag-first-letter-list",
    ),
]
