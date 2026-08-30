from rest_framework import serializers


class ReportStatusSerializer(serializers.Serializer):
    """레포트 상태 응답 Serializer"""

    status = serializers.CharField(
        read_only=True,
        help_text="레포트 상태",
    )
    description = serializers.CharField(
        read_only=True,
        help_text="상태 설명",
    )
