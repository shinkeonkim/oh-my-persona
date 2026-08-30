from rest_framework import serializers


class ReportEmailSerializer(serializers.Serializer):
    """레포트 이메일 전송 요청 Serializer"""

    email = serializers.EmailField(
        required=False,
        help_text="이메일 주소 (선택, 없으면 request.user.email 사용)",
    )

    class Meta:
        fields = ["email"]
