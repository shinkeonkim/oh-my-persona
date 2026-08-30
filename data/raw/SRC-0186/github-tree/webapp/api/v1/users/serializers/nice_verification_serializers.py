"""
NICE API 본인인증 관련 Serializers
"""

from rest_framework import serializers


class NiceVerificationInitSerializer(serializers.Serializer):
    """본인인증 초기화 요청 Serializer"""

    return_url = serializers.URLField(
        required=False,
        help_text="본인인증 완료 후 콜백 URL (선택)",
    )


class NiceVerificationInitResponseSerializer(serializers.Serializer):
    """본인인증 초기화 응답 Serializer"""

    token_version_id = serializers.CharField(
        help_text="토큰 버전 ID",
    )
    enc_data = serializers.CharField(
        help_text="암호화된 데이터",
    )
    integrity_value = serializers.CharField(
        help_text="무결성 값",
    )
    session_key = serializers.CharField(
        help_text="세션 키 (복호화에 필요)",
    )


class NiceVerificationCallbackSerializer(serializers.Serializer):
    """본인인증 콜백 요청 Serializer"""

    enc_data = serializers.CharField(
        required=True,
        help_text="NICE API에서 받은 암호화된 데이터",
    )
    integrity_value = serializers.CharField(
        required=True,
        help_text="NICE API에서 받은 무결성 값",
    )
    session_key = serializers.CharField(
        required=True,
        help_text="초기화 시 받은 세션 키",
    )


class NiceVerificationResultSerializer(serializers.Serializer):
    """본인인증 결과 Serializer"""

    success = serializers.BooleanField(
        help_text="본인인증 성공 여부",
    )
    data = serializers.DictField(
        required=False,
        help_text="본인인증 결과 데이터",
    )
    error = serializers.DictField(
        required=False,
        help_text="오류 정보",
    )
