from meme.models import Memo
from rest_framework.serializers import ModelSerializer


class MemoSerializer(ModelSerializer):
    class Meta:
        model = Memo
        fields = ["id", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
