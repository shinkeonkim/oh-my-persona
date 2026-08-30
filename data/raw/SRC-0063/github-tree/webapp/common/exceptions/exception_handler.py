from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError as DjangoIntegrityError

from rest_framework.exceptions import NotFound as DRFNotFound
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.views import exception_handler

from .base_api_exception import BaseAPIException
from .common_error_code import CommonErrorCode
from .forbidden_error import ForbiddenError
from .not_found_error import NotFoundError
from .validation_error import ValidationError


def custom_exception_handler(exc, context):
    """
    Custom exception handler that converts all exceptions to standardized error format
    """
    # Convert Django ValidationError to our custom ValidationError
    if isinstance(exc, DjangoValidationError):
        # Django ValidationError의 message_dict 또는 message를 처리
        if hasattr(exc, "message_dict"):
            # Field-specific errors
            details = exc.message_dict
            message = exc.message_dict.get("__all__", ["Validation failed"])[0]
        else:
            # General validation error
            details = None
            message = str(exc.message) if hasattr(exc, "message") else str(exc)

        exc = ValidationError(
            message=message,
            details=details,
        )
    # Convert Django IntegrityError to our custom ValidationError
    elif isinstance(exc, DjangoIntegrityError):
        # IntegrityError 메시지에서 중복 키 정보 추출
        error_message = str(exc)
        if "unique constraint" in error_message.lower():
            message = "중복된 데이터가 이미 존재합니다."
            details = {"constraint": "unique_constraint"}
        else:
            message = "데이터 무결성 오류가 발생했습니다."
            details = {"error": error_message}

        exc = ValidationError(
            message=message,
            details=details,
        )
    # Convert DRF exceptions to our custom exceptions
    elif isinstance(exc, DRFValidationError):
        exc = ValidationError(
            message=(
                exc.detail.get("non_field_errors", [str(exc.detail)])[0]
                if isinstance(exc.detail, dict)
                else str(exc.detail)
            ),
            details=exc.detail if isinstance(exc.detail, dict) else None,
        )
    elif isinstance(exc, DRFNotFound):
        exc = NotFoundError()
    elif isinstance(exc, DRFPermissionDenied):
        exc = ForbiddenError()

    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # If it's our custom exception, use its standardized format
        if isinstance(exc, BaseAPIException):
            custom_response_data = exc.get_full_details()
            response.data = custom_response_data
            # Use the HTTP status from the exception
            response.status_code = exc.http_status
        else:
            # For other DRF exceptions, convert to standardized format
            # Map DRF status codes to our ErrorCodes
            error_code = _map_drf_status_to_error_code(response.status_code)
            custom_response_data = {
                "status": "FAIL",
                "message": response.data.get("detail", error_code.message),
                "error_code": error_code.code,
                "description": error_code.description,
                "details": response.data if isinstance(response.data, dict) else None,
            }
            response.data = custom_response_data

    return response


def _map_drf_status_to_error_code(status_code):
    """Map DRF status codes to our ErrorCodes"""
    status_to_error_code = {
        400: CommonErrorCode.COMMON_400,
        401: CommonErrorCode.COMMON_401,
        403: CommonErrorCode.COMMON_403,
        404: CommonErrorCode.COMMON_404,
        405: CommonErrorCode.COMMON_405,
        409: CommonErrorCode.COMMON_409,
        413: CommonErrorCode.COMMON_413,
        422: CommonErrorCode.COMMON_422,
        500: CommonErrorCode.COMMON_500,
        503: CommonErrorCode.COMMON_503,
        504: CommonErrorCode.COMMON_504,
    }
    return status_to_error_code.get(status_code, CommonErrorCode.COMMON_500)
