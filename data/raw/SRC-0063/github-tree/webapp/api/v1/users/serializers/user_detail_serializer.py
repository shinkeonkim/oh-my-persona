from dj_rest_auth.serializers import UserDetailsSerializer


class UserDetailSerializer(UserDetailsSerializer):
    """
    UserDetailsSerializer를 custom User 모델에 맞게 재정의합니다.
    """

    class Meta(UserDetailsSerializer.Meta):
        fields = tuple(f for f in UserDetailsSerializer.Meta.fields if f != "pk") + (
            "id",
            "username",
            "email",
        )

        read_only_fields = tuple(f for f in UserDetailsSerializer.Meta.read_only_fields if f != "pk") + (
            "id",
            "username",
        )
