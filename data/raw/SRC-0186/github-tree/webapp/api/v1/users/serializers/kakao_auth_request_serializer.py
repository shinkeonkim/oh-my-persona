from rest_framework import serializers


class KakaoAuthRequestSerializer(serializers.Serializer):
    code = serializers.CharField(help_text="카카오 OAuth 인증 후 반환되는 인가 코드")
