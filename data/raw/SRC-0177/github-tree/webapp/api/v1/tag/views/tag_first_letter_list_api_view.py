from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from tag.models import Tag


class TagFirstLetterListAPIView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        responses={200: {"type": "array", "items": {"type": "string"}}},
        tags=["tag"],
        description="Retrieve a list of distinct first letters from available tags.",
    )
    def get(self, request):
        first_letters = Tag.objects.values_list("first_letter", flat=True).distinct()

        return Response(first_letters)
