from django.contrib.auth import authenticate

from dj_rest_auth.serializers import LoginSerializer as DefaultLoginSerializer
from rest_framework import serializers


class LoginSerializer(DefaultLoginSerializer):
    """
    username과 password로 로그인하는 커스텀 Serializer.
    email 필드는 사용하지 않습니다.
    """

    username = serializers.CharField(required=True)
    email = None  # email 필드 제거
    password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
    )

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            user = authenticate(
                request=self.context.get("request"),
                username=username,
                password=password,
            )

            if not user:
                msg = "Unable to log in with provided credentials."
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = "Must include 'username' and 'password'."
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs
