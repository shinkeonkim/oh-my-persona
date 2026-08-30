import logging

from django.conf import settings
from django.db import transaction

import requests
from allauth.socialaccount.models import SocialAccount, SocialToken
from dj_rest_auth.views import UserDetailsView
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response

from api.v1.users.serializers import UserDetailSerializer
from common.schemas.error_schemas import (
    get_internal_server_error_schema,
    get_unauthorized_error_schema,
)


@extend_schema(
    tags=["User"],
)
class UserView(UserDetailsView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserDetailSerializer

    @extend_schema(
        operation_id="get_user_details",
        summary="Get User Details",
        description="Retrieve detailed information about the authenticated user including social account connections.",
        responses={
            200: OpenApiResponse(
                response=UserDetailSerializer,
                description="User details retrieved successfully",
            ),
            401: get_unauthorized_error_schema(),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @transaction.atomic
    @extend_schema(
        operation_id="delete_user_account",
        summary="Delete User Account",
        description="Delete the authenticated user account. And unlink all connected social accounts (Kakao). "
        + "This action is irreversible.",
        responses={
            204: OpenApiResponse(description="User account successfully deleted"),
            401: get_unauthorized_error_schema(),
            500: get_internal_server_error_schema(),
        },
    )
    def delete(self, request, *args, **kwargs):
        user = request.user
        try:
            # 1. 카카오 계정 연결 해제 - 어드민 키 사용
            self._unlink_kakao_account(user)

            # 2. 소셜 토큰 및 소셜 계정 정보 삭제
            SocialToken.objects.filter(account__user=user).delete()
            SocialAccount.objects.filter(user=user).delete()

            # 3. 사용자 계정 삭제
            user.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            from common.exceptions.custom_exceptions import InternalServerError

            logging.error(f"Error during account deletion: {e}")
            raise InternalServerError(message="Account deletion failed", details={"error": str(e)})

    def _unlink_kakao_account(self, user):
        """카카오 계정 연결 해제 - 어드민 키 방식 사용"""
        kakao_account = SocialAccount.objects.filter(user=user, provider="kakao").first()
        if kakao_account and settings.KAKAO_ADMIN_KEY:
            try:
                headers = {
                    "Authorization": f"KakaoAK {settings.KAKAO_ADMIN_KEY}",
                    "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
                }
                data = {"target_id_type": "user_id", "target_id": kakao_account.uid}

                response = requests.post("https://kapi.kakao.com/v1/user/unlink", headers=headers, data=data)

                if response.status_code == 200:
                    logging.info(f"Successfully unlinked Kakao account for user {user.email}")
                    return True
                else:
                    logging.warning(f"Failed to unlink Kakao account: {response.status_code} - {response.text}")
            except Exception as e:
                logging.error(f"Error unlinking Kakao account: {e}")

        return False
