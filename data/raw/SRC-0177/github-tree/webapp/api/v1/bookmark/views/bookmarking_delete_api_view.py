from bookmark.models import Bookmarking
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class BookmarkingDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Delete a Bookmarking",
        description=(
            "Removes the specified Bookmarking if it belongs to the current user. "
            "Returns 204 on success."
        ),
        operation_id="bookmarking_delete",
        parameters=[
            OpenApiParameter(
                name="bookmarking_id",
                location=OpenApiParameter.PATH,
                description="The ID of the Bookmarking to delete.",
                required=True,
                type=int,
            )
        ],
        responses={
            204: None,
            404: {
                "description": "Bookmarking not found, or doesn't belong to the user.",
                "content": {"application/json": {"example": {"detail": "Not found."}}},
            },
        },
        tags=["bookmarking"],
    )
    def delete(self, request, bookmarking_id, *args, **kwargs):
        user = request.user
        bookmarking = get_object_or_404(Bookmarking, pk=bookmarking_id, user=user)
        bookmarking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
