from drf_spectacular.utils import extend_schema
from watchlists.models import Watchlist

from common.pagination import StandardPagination
from common.views import BaseViewSet

from ..serializers import WatchlistSerializer


@extend_schema(tags=["Watchlist"], )
class WatchlistViewSet(BaseViewSet):
  """자신의 Watchlist에 대한 CRUD ViewSet"""

  serializer_class = WatchlistSerializer
  pagination_class = StandardPagination

  def get_queryset(self):
    return Watchlist.objects.filter(user=self.request.user).order_by("-created_at")

  def perform_create(self, serializer):
    serializer.save(user=self.request.user)
