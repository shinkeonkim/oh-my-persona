import logging

import requests
from allauth.socialaccount.models import SocialAccount, SocialToken
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView


class UserDeleteView(APIView):
    """사용자 계정 삭제를 위한 전용 뷰"""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description="사용자 계정 및 연결된 소셜 계정을 삭제합니다.",
        responses={
            204: OpenApiResponse(
                description="사용자 계정이 성공적으로 삭제되었습니다."
            ),
            500: OpenApiResponse(description="삭제 중 오류가 발생했습니다."),
        },
        operation_id="delete_user_account",
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

            return Response(
                {"detail": _("Account successfully deleted.")},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            logging.error(f"Error during account deletion: {e}")
            return Response(
                {"detail": _("An error occurred during account deletion.")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _unlink_kakao_account(self, user):
        """카카오 계정 연결 해제 - 어드민 키 방식 사용"""
        kakao_account = SocialAccount.objects.filter(
            user=user, provider="kakao"
        ).first()
        if kakao_account and settings.KAKAO_ADMIN_KEY:
            try:
                headers = {
                    "Authorization": f"KakaoAK {settings.KAKAO_ADMIN_KEY}",
                    "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
                }
                data = {"target_id_type": "user_id", "target_id": kakao_account.uid}

                response = requests.post(
                    "https://kapi.kakao.com/v1/user/unlink", headers=headers, data=data
                )

                if response.status_code == 200:
                    logging.info(
                        f"Successfully unlinked Kakao account for user {user.email}"
                    )
                    return True
                else:
                    logging.warning(
                        f"Failed to unlink Kakao account: {response.status_code} - {response.text}"
                    )
            except Exception as e:
                logging.error(f"Error unlinking Kakao account: {e}")

        return False
