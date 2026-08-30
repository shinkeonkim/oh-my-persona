from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from meme.models import Meme
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class MemeBookmarkIdsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="meme_id",
                description="ID of the meme for which bookmark IDs are fetched",
                required=True,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
            ),
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "bookmark_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of bookmark IDs for the specified meme.",
                    }
                },
            },
        },
        tags=["meme"],
        description="Retrieve a list of bookmark IDs for a specific meme.",
    )
    def get(self, request, meme_id):
        current_user = request.user
        meme = get_object_or_404(Meme, pk=meme_id)
        bookmark_ids = meme.bookmark_ids_by(user=current_user)

        return Response({"bookmark_ids": bookmark_ids}, status=200)
