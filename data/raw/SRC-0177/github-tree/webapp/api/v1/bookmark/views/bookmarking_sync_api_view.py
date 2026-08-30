from api.v1.base_api_view import BaseAPIView
from bookmark.models import Bookmark, Bookmarking
from django.db import transaction
from django.db.models.signals import post_save
from drf_spectacular.utils import OpenApiExample, extend_schema
from meme.models import Meme
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from tag.tasks.tag_counter_tasks import update_counters_for_bookmarking


class BookmarkingSyncAPIView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    @property
    def current_meme(self):
        meme_id = self.request.data.get("meme_id")
        return get_object_or_404(Meme, pk=meme_id)

    @extend_schema(
        summary="bulk sync bookmarkings",
        description=("단일 밈과 여러 북마크에 대해서 동시에 다룹니다."),
        operation_id="bookmarking_sync",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "meme_id": {
                        "type": "integer",
                        "description": "The ID of the Meme to sync.",
                    },
                    "bookmark_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of Bookmark IDs belonging to the user.",
                    },
                    "without_bookmark": {
                        "type": "boolean",
                        "default": False,
                        "description": (
                            "If true, Bookmarkings without a Bookmark will be saved. "
                        ),
                    },
                },
                "required": ["meme_id", "bookmark_ids"],
            }
        },
        responses={
            200: {
                "description": "Successful synchronization.",
                "content": {
                    "application/json": {
                        "example": {"detail": "Bookmarkings synced successfully."}
                    }
                },
            },
            400: {
                "description": "Bad Request (e.g. missing fields).",
                "content": {
                    "application/json": {
                        "example": {"detail": "meme_id and bookmark_ids are required."}
                    }
                },
            },
            404: {
                "description": "Meme not found or invalid resource.",
                "content": {"application/json": {"example": {"detail": "Not found."}}},
            },
        },
        tags=["bookmarking"],
        examples=[
            OpenApiExample(
                "Example",
                summary="A valid request",
                value={
                    "meme_id": 10,
                    "bookmark_ids": [101, 102, 103],
                    "without_bookmark": False,
                },
            ),
            OpenApiExample(
                "Example",
                summary="A valid request",
                value={"meme_id": 10, "bookmark_ids": [], "without_bookmark": True},
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        data = request.data
        without_bookmark = data.get("without_bookmark", False)

        # NOTE: bookmark가 있는 경우와 없는 경우는 서로 다른 로직을 사용합니다.
        # 특정 밈에 대해서, bookmark가 있는 경우와 없는 bookmarking은 공존할 수 없습니다.
        if without_bookmark:
            self.sync_without_bookmark()
        else:
            self.sync_bookmarking_with_bookmarks()

        return Response(
            {"detail": "Bookmarkings synced successfully."}, status=status.HTTP_200_OK
        )

    @transaction.atomic
    def sync_without_bookmark(self):
        meme = self.current_meme

        self.delete_bookmarking_with_bookmark()

        Bookmarking.objects.create(meme=meme, user=self.current_user, bookmark=None)

    @transaction.atomic
    def sync_bookmarking_with_bookmarks(self):
        meme = self.current_meme
        bookmark_ids = self.request.data.get("bookmark_ids", [])

        if not bookmark_ids:
            raise ValidationError("At least one bookmark_id must be provided.")
        valid_bookmark_ids = set(
            Bookmark.objects.filter(
                user=self.current_user, pk__in=bookmark_ids
            ).values_list("id", flat=True)
        )

        if len(valid_bookmark_ids) != len(bookmark_ids) or set(
            valid_bookmark_ids
        ) != set(bookmark_ids):
            raise ValidationError("Invalid bookmark IDs provided.")

        self.delete_bookmarking_without_bookmark()

        existing_bookmark_ids = set(
            Bookmarking.objects.filter(user=self.current_user, meme=meme).values_list(
                "bookmark_id", flat=True
            )
        )

        to_remove = existing_bookmark_ids - valid_bookmark_ids
        to_add = valid_bookmark_ids - existing_bookmark_ids

        if to_remove:
            Bookmarking.objects.filter(
                user=self.current_user, meme=meme, bookmark_id__in=to_remove
            ).delete()

        new_objects = []
        for bk_id in to_add:
            new_objects.append(
                Bookmarking(meme=meme, bookmark_id=bk_id, user=self.current_user)
            )

        if new_objects:
            created_objects = Bookmarking.objects.bulk_create(new_objects)

            bookmark_ids = [obj.bookmark_id for obj in created_objects]
            refreshed_objects = Bookmarking.objects.filter(
                bookmark_id__in=bookmark_ids, meme=meme, user=self.current_user
            ).select_related("bookmark", "meme")

            for obj in refreshed_objects:
                post_save.send(sender=Bookmarking, instance=obj, created=True)

        if to_remove:
            update_counters_for_bookmarking.delay(self.current_user.id, meme.id)

    def delete_bookmarking_with_bookmark(self):
        Bookmarking.objects.filter(
            user=self.current_user, meme=self.current_meme, bookmark__isnull=False
        ).delete()

    def delete_bookmarking_without_bookmark(self):
        Bookmarking.objects.filter(
            user=self.current_user, meme=self.current_meme, bookmark__isnull=True
        ).delete()
