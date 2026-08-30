from api.v1.bookmark.serializers import BookmarkingSerializer
from bookmark.models import Bookmark, Bookmarking
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated


@extend_schema_view(
    list=extend_schema(
        tags=["bookmarking"],
    ),
    retrieve=extend_schema(
        tags=["bookmarking"],
    ),
    create=extend_schema(
        tags=["bookmarking"],
    ),
    update=extend_schema(
        tags=["bookmarking"],
    ),
    partial_update=extend_schema(
        tags=["bookmarking"],
    ),
    destroy=extend_schema(
        tags=["bookmarking"],
    ),
)
class BookmarkingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bookmarking.objects.all()
    serializer_class = BookmarkingSerializer
    permission_classes = (IsAuthenticated,)
    search_fields = ["meme__title"]
    ordering_fields = ["created_at", "updated_at", "meme__title"]
    ordering = ("-id",)

    def get_queryset(self):
        bookmark_pk = self.kwargs.get("bookmark_pk")
        bookmark = get_object_or_404(Bookmark, pk=bookmark_pk, user=self.request.user)

        return self.queryset.filter(user=self.request.user, bookmark=bookmark)
