from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated

from api.v1.payments.serializers import TicketProductSerializer
from common.views import BaseReadOnlyViewSet
from payments.models import TicketProduct


@extend_schema_view(
    list=extend_schema(
        summary="구매 가능한 티켓 상품 목록",
        description="현재 구매 가능한 티켓 상품 목록을 반환합니다.",
        tags=["Ticket Products"],
    ),
    retrieve=extend_schema(
        summary="티켓 상품 상세 조회",
        tags=["Ticket Products"],
    ),
)
class TicketProductViewSet(BaseReadOnlyViewSet):
    """티켓 상품 ViewSet (읽기 전용)"""

    permission_classes = [IsAuthenticated]
    serializer_class = TicketProductSerializer
    queryset = TicketProduct.objects.active().order_by("display_order", "quantity")
