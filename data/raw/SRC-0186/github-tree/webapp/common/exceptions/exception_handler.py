from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError as DjangoIntegrityError

from rest_framework.exceptions import NotFound as DRFNotFound
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.views import exception_handler

from common.enums.error_codes import ErrorCodes
from common.exceptions.custom_exceptions import (
    BaseAPIException,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)


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
            if "unique_sender_receiver" in error_message:
                message = "이미 해당 사용자에게 호감을 보낸 적이 있습니다."
                details = {"constraint": "unique_sender_receiver"}
            else:
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
        400: ErrorCodes.SRV_400,
        401: ErrorCodes.AUTH_401,
        403: ErrorCodes.AUTH_403,
        404: ErrorCodes.USR_404,
        405: ErrorCodes.SRV_400,  # Method not allowed -> Bad request
        406: ErrorCodes.SRV_400,  # Not acceptable -> Bad request
        408: ErrorCodes.SRV_400,  # Request timeout -> Bad request
        409: ErrorCodes.USR_409,
        410: ErrorCodes.USR_404,  # Gone -> Not found
        413: ErrorCodes.FILE_413,
        414: ErrorCodes.SRV_400,  # URI too long -> Bad request
        415: ErrorCodes.FILE_415,
        422: ErrorCodes.VAL_422,
        429: ErrorCodes.SRV_429,
        500: ErrorCodes.SRV_500,
        501: ErrorCodes.SRV_500,  # Not implemented -> Internal server error
        502: ErrorCodes.SRV_500,  # Bad gateway -> Internal server error
        503: ErrorCodes.SRV_503,
        504: ErrorCodes.SRV_500,  # Gateway timeout -> Internal server error
    }
    return status_to_error_code.get(status_code, ErrorCodes.SRV_500)
