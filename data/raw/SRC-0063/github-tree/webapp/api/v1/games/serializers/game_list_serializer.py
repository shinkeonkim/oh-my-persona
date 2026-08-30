from rest_framework import serializers


class GameListSerializer(serializers.Serializer):
    """게임 목록 조회 Serializer"""

    id = serializers.IntegerField()
    code = serializers.CharField()
    name = serializers.CharField()
    is_active = serializers.BooleanField()
