from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import WatchlistItemViewSet, WatchlistViewSet

router = DefaultRouter()
router.register(r"watchlist", WatchlistViewSet, basename="watchlist")
router.register(r"watchlist-items", WatchlistItemViewSet, basename="watchlist-item")

urlpatterns = [
  path("", include(router.urls)),
]
