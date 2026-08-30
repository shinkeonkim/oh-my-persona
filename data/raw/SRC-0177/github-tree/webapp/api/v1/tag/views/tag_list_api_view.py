from api.v1.tag.serializers import TagSerializer
from django.db.models import ExpressionWrapper, F, FloatField, Value
from django.db.models.functions import Coalesce, Extract, Now
from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from tag.models import Tag

# 태그 인기도 가중치
TAG_POPULARITY_WEIGHTS = {
    "memes_count": 3,
    "bookmarkings_count": 4,
}


@extend_schema(
    tags=["tag"],
)
class TagListAPIView(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    filterset_fields = ["category", "first_letter"]
    search_fields = ["name", "split_name"]
    ordering_fields = ["id", "name", "created_at", "popularity"]
    ordering = ["name"]  # 기본 정렬: 인기도 내림차순, 이름 오름차순

    def get_queryset(self):
        # 인기도 계산을 위한 어노테이션 추가
        return (
            self.queryset.all()
            .prefetch_related("meme_taggings", "tag_counter")
            .annotate(
                # 태그 카운터가 아직 없는 경우를 대비한 안전한 접근
                memes_count=Coalesce(F("tag_counter__memes_count"), Value(0)),
                bookmarkings_count=Coalesce(
                    F("tag_counter__bookmarkings_count"), Value(0)
                ),
                # 인기도 점수 계산
                popularity=ExpressionWrapper(
                    -(
                        F("memes_count") * TAG_POPULARITY_WEIGHTS["memes_count"]
                        + F("bookmarkings_count")
                        * TAG_POPULARITY_WEIGHTS["bookmarkings_count"]
                    )
                    / (Extract(Now() - F("created_at"), "epoch") + 1),
                    output_field=FloatField(),
                ),
            )
            .order_by("-popularity", "name")
        )
