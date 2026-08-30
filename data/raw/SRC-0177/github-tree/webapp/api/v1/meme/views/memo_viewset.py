from api.v1.meme.serializers import MemoSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view
from meme.models import Meme
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


@extend_schema_view(
    list=extend_schema(
        tags=["meme-memo"],
    ),
    retrieve=extend_schema(
        tags=["meme-memo"],
    ),
    create=extend_schema(
        tags=["meme-memo"],
    ),
    update=extend_schema(
        tags=["meme-memo"],
    ),
    partial_update=extend_schema(
        tags=["meme-memo"],
    ),
    destroy=extend_schema(
        tags=["meme-memo"],
    ),
)
class MemoViewSet(viewsets.ModelViewSet):
    serializer_class = MemoSerializer
    permission_classes = [IsAuthenticated]

    ordering_fields = ["id", "created_at", "updated_at"]
    search_fields = []
    filterset_fields = []
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        meme_id = self.kwargs["meme_pk"]
        meme = Meme.objects.get(id=meme_id)
        serializer.save(creator=self.request.user, meme=meme)

    def get_queryset(self):
        meme_id = self.kwargs["meme_pk"]
        return self.request.user.memos.filter(meme_id=meme_id)
