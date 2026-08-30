from api.v1.meme.serializers import MemeSerializer
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from meme.models import Meme
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class RelatedMemeListAPIView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="count",
                description="Number of related memes to retrieve",
                required=False,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="meme_id",
                description="ID of the meme for which related memes are fetched",
                required=True,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
            ),
        ],
        responses=MemeSerializer(many=True),
        tags=["meme"],
        description="Retrieve a list of memes related to the given meme ID.",
    )
    def get(self, request, meme_id):
        count = int(request.query_params.get("count", 10))
        meme = get_object_or_404(Meme, pk=meme_id)
        related_memes = meme.related_memes[:count]
        related_memes = MemeSerializer(
            related_memes, many=True, context={"request": request}
        ).data
        return Response(related_memes)
