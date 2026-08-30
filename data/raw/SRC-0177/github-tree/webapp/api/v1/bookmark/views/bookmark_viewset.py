from api.v1.bookmark.serializers import BookmarkSerializer
from bookmark.models import Bookmark
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


@extend_schema_view(
    list=extend_schema(
        tags=["bookmark"],
    ),
    retrieve=extend_schema(
        tags=["bookmark"],
    ),
    create=extend_schema(
        tags=["bookmark"],
    ),
    update=extend_schema(
        tags=["bookmark"],
    ),
    partial_update=extend_schema(
        tags=["bookmark"],
    ),
    destroy=extend_schema(
        tags=["bookmark"],
    ),
)
class BookmarkViewSet(viewsets.ModelViewSet):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]
    ordering = ("-id",)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
