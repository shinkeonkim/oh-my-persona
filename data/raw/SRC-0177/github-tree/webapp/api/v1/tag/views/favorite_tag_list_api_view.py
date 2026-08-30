from api.v1.tag.serializers import TagSerializer
from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from tag.models import Tag, TagUserCounter


@extend_schema(
    tags=["tag"],
)
class FavoriteTagListAPIView(ListAPIView):
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Tag.objects.none()
        tags = (
            TagUserCounter.objects.prefetch_related("tag")
            .filter(user=self.request.user)
            .order_by("-bookmarkings_count")
            .values_list("tag", flat=True)[:10]
        )

        return Tag.objects.filter(id__in=tags)
