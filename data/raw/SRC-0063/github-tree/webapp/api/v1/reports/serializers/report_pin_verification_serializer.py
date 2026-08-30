from rest_framework import serializers


class ReportPinVerificationSerializer(serializers.Serializer):
    """
    레포트 PIN 검증 Serializer
    """

    pin = serializers.CharField(
        required=True,
        min_length=4,
        max_length=6,
        write_only=True,
        help_text="레포트 조회를 위한 PIN 번호 (4-6자리)",
    )

    class Meta:
        fields = ["pin"]
