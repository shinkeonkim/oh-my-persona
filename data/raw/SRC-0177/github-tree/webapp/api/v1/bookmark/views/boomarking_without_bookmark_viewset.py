from api.v1.bookmark.serializers import BookmarkingSerializer
from bookmark.models import Bookmark, Bookmarking
from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from tag.tasks.tag_counter_tasks import update_counters_for_bookmarking


class BookmarkingWithoutBookmarkViewset(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin
):
    permission_classes = (IsAuthenticated,)
    queryset = Bookmarking.objects.without_bookmark()
    serializer_class = BookmarkingSerializer

    @extend_schema(
        description="북마크가 없는 북마킹들을 조회합니다.",
        tags=["bookmarking"],
    )
    def list(self, request):
        """
        List all bookmarkings without associated memes for the authenticated user.
        """
        user = self.request.user
        bookmarkings = self.queryset.filter(user=user)
        serializer = self.get_serializer(bookmarkings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="북마크가 없는 북마킹들에 대해 북마크를 일괄로 추가합니다.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "meme_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "북마크를 추가할 밈 ID 목록",
                    },
                    "bookmark_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "추가할 북마크 ID 목록",
                    },
                },
                "required": ["meme_ids", "bookmark_ids"],
            }
        },
        responses={
            201: BookmarkingSerializer(many=True),
            400: "잘못된 요청 데이터",
            404: "존재하지 않는 밈 또는 북마크",
        },
        tags=["bookmarking"],
    )
    def create(self, request):
        """
        북마크가 없는 북마킹들에 대해 북마크를 일괄로 추가하는 작업
        """
        meme_ids = request.data.get("meme_ids", [])
        bookmark_ids = request.data.get("bookmark_ids", [])

        # 입력 데이터 검증
        if not meme_ids or not bookmark_ids:
            raise ValidationError("meme_ids와 bookmark_ids는 필수입니다.")

        if not isinstance(meme_ids, list) or not isinstance(bookmark_ids, list):
            raise ValidationError("meme_ids와 bookmark_ids는 배열 형태여야 합니다.")

        user = request.user

        # 북마크 소유권 검증
        valid_bookmark_ids = set(
            Bookmark.objects.filter(user=user, pk__in=bookmark_ids).values_list(
                "id", flat=True
            )
        )

        # 북마크가 없는 북마킹에 해당하는 meme_id만 있는지 검증
        valid_meme_ids = set(
            Bookmarking.objects.filter(
                user=user, meme_id__in=meme_ids, bookmark__isnull=True
            ).values_list("meme_id", flat=True)
        )

        if not valid_meme_ids or len(valid_meme_ids) != len(meme_ids):
            invalid_ids = set(meme_ids) - valid_meme_ids
            raise ValidationError(detail=f"유효하지 않은 밈 ID: {invalid_ids}")

        if len(valid_bookmark_ids) != len(bookmark_ids):
            invalid_ids = set(bookmark_ids) - valid_bookmark_ids
            raise ValidationError(detail=f"유효하지 않은 북마크 ID: {invalid_ids}")

        with transaction.atomic():
            Bookmarking.objects.filter(
                user=user, meme_id__in=meme_ids, bookmark__isnull=True
            ).delete()

            new_bookmarkings = []
            # FIXME: bulk create로 변경하는 로직을 이후에 고려할 것
            for meme_id in meme_ids:
                for bookmark_id in valid_bookmark_ids:
                    new_bookmarkings.append(
                        Bookmarking(meme_id=meme_id, bookmark_id=bookmark_id, user=user)
                    )

            if new_bookmarkings:
                created_bookmarkings = []
                for new_bookmarking in new_bookmarkings:
                    created_bookmarking = Bookmarking.objects.create(
                        meme_id=new_bookmarking.meme_id,
                        bookmark_id=new_bookmarking.bookmark_id,
                        user=new_bookmarking.user,
                    )
                    created_bookmarkings.append(created_bookmarking)

                refreshed_bookmarkings = Bookmarking.objects.filter(
                    id__in=[obj.id for obj in created_bookmarkings]
                ).select_related("bookmark", "meme")

                for bookmark_id in valid_bookmark_ids:
                    bookmark = Bookmark.objects.get(id=bookmark_id)
                    bookmark.reset_bookmarkings_count()

                for meme_id in meme_ids:
                    update_counters_for_bookmarking.delay(user.id, meme_id)

                serializer = self.get_serializer(refreshed_bookmarkings, many=True)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response([], status=status.HTTP_201_CREATED)
