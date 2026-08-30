"""
NICE API 본인인증 REST API Views
프론트엔드에서 직접 팝업을 처리할 수 있도록 JSON API 제공
"""

import uuid

from django.contrib.auth import get_user_model
from django.core.cache import cache

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.users.serializers import (
    NiceVerificationCallbackSerializer,
    NiceVerificationInitResponseSerializer,
    NiceVerificationInitSerializer,
)
from common.exceptions.custom_exceptions import (
    NiceServiceError,
    NiceSessionExpiredError,
    NiceVerificationError,
)
from common.utils.logger import get_logger
from users.services.identity_verification_service import IdentityVerificationService
from users.utils.nice_api import NiceAPIError

logger = get_logger(__name__)

User = get_user_model()


@extend_schema(
    tags=["NICE API 본인인증"],
    summary="본인인증 초기화",
    description="NICE API 본인인증에 필요한 암호화 토큰 데이터를 생성합니다.",
    request=NiceVerificationInitSerializer,
    responses={
        200: NiceVerificationInitResponseSerializer,
        400: {"description": "잘못된 요청"},
        500: {"description": "서버 오류"},
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def nice_verification_init_api(request):
    """
    본인인증 초기화 API

    NICE API 본인인증 팝업에 필요한 데이터를 생성합니다.
    프론트엔드는 이 데이터를 사용하여 NICE 팝업을 직접 열 수 있습니다.

    Returns:
        - token_version_id: 토큰 버전 ID
        - enc_data: 암호화된 데이터
        - integrity_value: 무결성 값
        - session_key: 세션 키 (복호화에 필요, 프론트엔드에서 보관)
    """
    serializer = NiceVerificationInitSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    return_url = serializer.validated_data.get("return_url")

    try:
        service = IdentityVerificationService(user=request.user)  # 본인인증 서비스 초기화
        verification_data = service.initiate_verification(return_url=return_url)  # 본인인증 프로세스 시작
        session_key = str(uuid.uuid4())  # 세션 키 생성 (UUID 사용)

        # 복호화에 필요한 키를 Redis 캐시에 저장 (15분 TTL)
        cache_data = {
            "key": verification_data["key"],
            "iv": verification_data["iv"],
            "hmac_key": verification_data["hmac_key"],
            "req_no": verification_data["req_no"],
        }
        cache.set(f"nice_session_{session_key}", cache_data, timeout=900)  # 15분

        # 프론트엔드에 전달할 데이터
        response_data = {
            "token_version_id": verification_data["token_version_id"],
            "enc_data": verification_data["enc_data"],
            "integrity_value": verification_data["integrity_value"],
            "session_key": session_key,
        }

        logger.info(f"본인인증 초기화 성공 - 세션: {session_key}")
        return Response(response_data, status=status.HTTP_200_OK)

    except NiceAPIError as e:
        logger.error(f"NICE API 오류: [{e.code}] {e.message}")
        raise NiceServiceError(
            message=f"본인인증 초기화 실패: {e.message}",
            details={"nice_error_code": e.code},
        )
    except Exception as e:
        logger.exception(f"본인인증 초기화 중 예상치 못한 오류 발생: {str(e)}")
        raise NiceServiceError(message="본인인증 서비스 오류가 발생했습니다.")


@extend_schema(
    tags=["NICE API 본인인증"],
    summary="본인인증 결과 검증",
    description="NICE API에서 받은 암호화된 본인인증 결과를 복호화하고 검증합니다. 로그인한 사용자의 경우 자동으로 IdentityVerification 모델에 저장됩니다.",
    request=NiceVerificationCallbackSerializer,
    responses={
        200: {"description": "본인인증 성공", "example": {"success": True}},
        401: {"description": "세션 만료"},
        422: {"description": "본인인증 실패"},
        500: {"description": "서버 오류"},
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def nice_verification_verify_api(request):
    """
    본인인증 결과 검증 API

    NICE API에서 받은 암호화된 데이터를 복호화하고 검증합니다.
    로그인한 사용자의 경우 본인인증 정보를 IdentityVerification 모델에 자동으로 저장합니다.

    Request:
        - enc_data: NICE API에서 받은 암호화된 데이터
        - integrity_value: NICE API에서 받은 무결성 값
        - session_key: 초기화 시 받은 세션 키

    Returns:
        - success: 본인인증 성공 여부 (True만 반환)

    Note:
        - 성공 시 사용자 상세 정보는 반환하지 않습니다.
        - 성공 시 DB에 자동으로 저장됩니다.
    """
    serializer = NiceVerificationCallbackSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    enc_data = serializer.validated_data["enc_data"]
    integrity_value = serializer.validated_data["integrity_value"]
    session_key = serializer.validated_data["session_key"]

    try:
        # 캐시에서 복호화 키 가져오기
        cache_key = f"nice_session_{session_key}"
        cache_data = cache.get(cache_key)

        if not cache_data:
            logger.warning(f"세션 만료 또는 유효하지 않음: {session_key}")
            raise NiceSessionExpiredError(message="본인인증 세션이 만료되었습니다. 다시 시도해주세요.")

        key = cache_data["key"]
        iv = cache_data["iv"]
        hmac_key = cache_data["hmac_key"]

        user = request.user
        service = IdentityVerificationService(user=user)

        # 응답 데이터 검증 및 복호화 후 데이터 저장
        service.verify_and_save(enc_data, integrity_value, key, iv, hmac_key)

        # 캐시에서 세션 키 삭제 (일회성)
        cache.delete(cache_key)

        return Response({"success": True}, status=status.HTTP_200_OK)

    except NiceAPIError as e:
        logger.error(f"NICE API 검증 오류: [{e.code}] {e.message}")
        raise NiceVerificationError(
            message=f"본인인증 검증 실패: {e.message}",
            details={"nice_error_code": e.code},
        )
    except (NiceSessionExpiredError, NiceVerificationError):
        # 커스텀 예외는 그대로 re-raise
        raise
    except Exception as e:
        logger.exception(f"본인인증 검증 중 예상치 못한 오류 발생: {str(e)}")
        raise NiceServiceError(message="본인인증 서비스 오류가 발생했습니다.")
