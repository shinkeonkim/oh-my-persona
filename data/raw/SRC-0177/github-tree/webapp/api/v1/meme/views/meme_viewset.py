from api.v1.meme.serializers import MemeSerializer
from bookmark.models import Bookmarking
from django.db.models import ExpressionWrapper, F, FloatField, Prefetch, Value
from django.db.models.functions import Exp, Extract, Now
from drf_spectacular.utils import extend_schema, extend_schema_view
from meme.models import Meme
from meme.services.increase_meme_view_count_service import IncreaseMemeViewCountService
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

POPULARITY_WEIGHTS = {
    "bookmarkings_count": 3,
    "bookmarking_users_count": 6,
    "views_count": 1,
    "viewers_count": 2,
}

EXPO_SCALE = 86400.0


@extend_schema_view(
    list=extend_schema(
        tags=["meme"],
    ),
    retrieve=extend_schema(
        tags=["meme"],
    ),
    create=extend_schema(
        tags=["meme"],
    ),
    update=extend_schema(
        tags=["meme"],
    ),
    partial_update=extend_schema(
        tags=["meme"],
    ),
    destroy=extend_schema(
        tags=["meme"],
    ),
)
class MemeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MemeSerializer
    permission_classes = [AllowAny]

    ordering_fields = ["id", "created_at", "title", "popularity"]
    search_fields = ["title", "tags__name"]
    filterset_fields = ["type", "tags__category__name"]
    ordering = ["-id"]

    def get_queryset(self):
        return (
            Meme.objects.prefetch_related(
                "tags", "tags__category", "meme_counter", "thumbnail"
            )
            .prefetch_related(
                Prefetch(
                    "bookmarkings",
                    queryset=Bookmarking.objects.filter(
                        user=(
                            self.request.user
                            if self.request.user.is_authenticated
                            else None
                        )
                    ),
                    to_attr="user_bookmarkings",
                )
            )
            .published()
            .annotate(
                popularity_score=ExpressionWrapper(
                    -(
                        F("meme_counter__bookmarkings_count")
                        * POPULARITY_WEIGHTS["bookmarkings_count"]
                        + F("meme_counter__bookmarking_users_count")
                        * POPULARITY_WEIGHTS["bookmarking_users_count"]
                        + F("meme_counter__views_count")
                        * POPULARITY_WEIGHTS["views_count"]
                        + F("meme_counter__viewers_count")
                        * POPULARITY_WEIGHTS["viewers_count"]
                        + F("id") * 0.1
                    ),
                    output_field=FloatField(),
                ),
                popularity_decay=ExpressionWrapper(
                    Exp(-Extract(Now() - F("updated_at"), "epoch") / Value(EXPO_SCALE)),
                    output_field=FloatField(),
                ),
                popularity=ExpressionWrapper(
                    F("popularity_score") / F("popularity_decay"),
                    output_field=FloatField(),
                ),
            )
        )

    def retrieve(self, request, *args, **kwargs):
        meme = self.get_object()
        IncreaseMemeViewCountService(meme, request.user).perform()

        return super().retrieve(request, *args, **kwargs)
