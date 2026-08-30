from rest_framework import serializers


class EmailUpdateSerializer(serializers.Serializer):
    """
    사용자의 email을 수정하는 Serializer.
    """

    email = serializers.EmailField(required=True)
