from rest_framework.exceptions import APIException

from common.enums.error_codes import ErrorCode


class BaseAPIException(APIException):
  """Base API exception with standardized error format"""

  def __init__(
    self,
    error_code: ErrorCode,
    message: str = None,
    description: str = None,
    details: dict = None,
    http_status: int = None,
  ):
    self.error_code = error_code
    self.message = message or error_code.message
    self.description = description or error_code.description
    self.details = details
    self.http_status = http_status or error_code.http_status

    super().__init__(self.message)

  def get_full_details(self):
    """Return full error details in standardized format"""
    return {
      "status": "FAIL",
      "message": self.message,
      "error_code": self.error_code.code,
      "description": self.description,
      "details": self.details,
    }


# Common exceptions - truly common ones
class ValidationError(BaseAPIException):
  """Validation error exception"""

  def __init__(self, message: str = None, details: dict = None):
    from common.enums.error_codes import ErrorCodes

    super().__init__(
      error_code=ErrorCodes.VAL_422,
      message=message or "Validation error",
      details=details,
    )


class NotFoundError(BaseAPIException):
  """Not found error exception"""

  def __init__(self, message: str = None, details: dict = None):
    from common.enums.error_codes import ErrorCodes

    super().__init__(
      error_code=ErrorCodes.SRV_404,
      message=message or "Resource not found",
      details=details,
    )


class UnauthorizedError(BaseAPIException):
  """Unauthorized error exception"""

  def __init__(self, message: str = None, details: dict = None):
    from common.enums.error_codes import ErrorCodes

    super().__init__(
      error_code=ErrorCodes.AUTH_401,
      message=message or "Authentication required",
      details=details,
    )


class ForbiddenError(BaseAPIException):
  """Forbidden error exception"""

  def __init__(self, message: str = None, details: dict = None):
    from common.enums.error_codes import ErrorCodes

    super().__init__(
      error_code=ErrorCodes.AUTH_403,
      message=message or "Access forbidden",
      details=details,
    )


class InternalServerError(BaseAPIException):
  """Internal server error exception"""

  def __init__(self, message: str = None, details: dict = None):
    from common.enums.error_codes import ErrorCodes

    super().__init__(
      error_code=ErrorCodes.SRV_500,
      message=message or "Internal server error",
      details=details,
    )


# NICE API Identity Verification exceptions
class NiceVerificationError(BaseAPIException):
  """NICE API identity verification error exception"""

  def __init__(self, message: str = None, details: dict = None):
    from common.enums.error_codes import ErrorCodes

    super().__init__(
      error_code=ErrorCodes.NICE_422,
      message=message or "Identity verification failed",
      details=details,
    )


class NiceSessionExpiredError(BaseAPIException):
  """NICE API session expired error exception"""

  def __init__(self, message: str = None, details: dict = None):
    from common.enums.error_codes import ErrorCodes

    super().__init__(
      error_code=ErrorCodes.NICE_401,
      message=message or "Verification session expired",
      details=details,
    )


class NiceServiceError(BaseAPIException):
  """NICE API service error exception"""

  def __init__(self, message: str = None, details: dict = None):
    from common.enums.error_codes import ErrorCodes

    super().__init__(
      error_code=ErrorCodes.NICE_500,
      message=message or "Verification service error",
      details=details,
    )
