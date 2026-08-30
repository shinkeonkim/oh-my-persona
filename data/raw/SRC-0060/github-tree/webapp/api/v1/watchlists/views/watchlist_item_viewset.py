from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from watchlists.models import WatchlistItem

from common.pagination import StandardPagination
from common.views import BaseViewSet

from ..serializers import WatchlistItemSerializer


class WatchlistItemFilter(filters.FilterSet):
  watchlist_id = filters.NumberFilter(field_name="watchlist_id")

  class Meta:
    model = WatchlistItem
    fields = ["watchlist_id"]


@extend_schema(tags=["Watchlist"], )
class WatchlistItemViewSet(BaseViewSet):
  """자신의 WatchlistItem에 대한 CRUD ViewSet"""

  serializer_class = WatchlistItemSerializer
  pagination_class = StandardPagination
  filter_backends = [DjangoFilterBackend]
  filterset_class = WatchlistItemFilter

  def get_queryset(self):
    queryset = WatchlistItem.objects.select_related("watchlist", "stock").filter(watchlist__user=self.request.user)
    return queryset.order_by("-created_at")

  def perform_create(self, serializer):
    serializer.save()
