from django.contrib.auth import get_user_model

from dj_rest_auth.registration.serializers import RegisterSerializer as DefaultRegisterSerializer
from rest_framework import serializers

from users.validators import validate_password, validate_username

User = get_user_model()


class RegisterSerializer(DefaultRegisterSerializer):
    """
    username과 password만으로 회원가입을 진행하는 커스텀 Serializer.
    email은 선택 사항입니다.
    """

    username = serializers.CharField(
        max_length=20,
        min_length=4,
        required=True,
        help_text="4자리 이상의 영문과 숫자 조합",
    )
    email = serializers.EmailField(required=False, allow_blank=True)

    def validate_username(self, value):
        """
        Username 검증: 4자리 이상의 영문과 숫자 조합
        """
        validate_username(value)
        return value

    def validate_password1(self, value):
        """
        Password 검증: 8자리 이상의 영문과 숫자 조합
        """
        validate_password(value)
        return value

    def get_cleaned_data(self):
        return {
            "username": self.validated_data.get("username", ""),
            "password1": self.validated_data.get("password1", ""),
            "email": self.validated_data.get("email", ""),
        }

    def save(self, _request):
        """
        username과 password로 유저를 생성합니다.
        """
        return User.objects.create_user(
            username=self.validated_data.get("username"),
            password=self.validated_data.get("password1"),
            email=self.validated_data.get("email", ""),
        )
