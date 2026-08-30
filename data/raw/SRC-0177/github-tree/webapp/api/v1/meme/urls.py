from api.v1.meme.views import (
    MemeBookmarkIdsAPIView,
    MemeViewSet,
    MemoViewSet,
    RelatedMemeListAPIView,
)
from django.urls import include, path
from rest_framework_nested.routers import DefaultRouter, NestedSimpleRouter

app_name = "api.v1.meme"

router = DefaultRouter()
router.register(r"memes", MemeViewSet, basename="meme")

meme_router = NestedSimpleRouter(router, r"memes", lookup="meme")
meme_router.register(r"memos", MemoViewSet, basename="meme-memo")

urlpatterns = [
    path("memes/<int:meme_id>/related", RelatedMemeListAPIView.as_view()),
    path("memes/<int:meme_id>/bookmark_ids", MemeBookmarkIdsAPIView.as_view()),
    path("", include(router.urls)),
    path("", include(meme_router.urls)),
]
