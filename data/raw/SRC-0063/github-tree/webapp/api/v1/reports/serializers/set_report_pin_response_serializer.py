from rest_framework import serializers


class SetReportPinResponseSerializer(serializers.Serializer):
    is_success = serializers.BooleanField()
    message = serializers.CharField()

    class Meta:
        fields = [
            "is_success",
            "message",
        ]
        read_only_fields = [
            "is_success",
            "message",
        ]
