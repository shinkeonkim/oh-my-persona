from common.enums.error_codes import ErrorCodes
from common.exceptions.custom_exceptions import BaseAPIException


class ReferralNotFoundError(BaseAPIException):
    """Referral not found exception"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            error_code=ErrorCodes.MTM_404,
            message=message or "Referral not found",
            details=details,
        )


class ReferralValidationError(BaseAPIException):
    """Referral validation error exception"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            error_code=ErrorCodes.MTM_400,
            message=message or "Referral validation error",
            details=details,
        )


class MatchingNotFoundError(BaseAPIException):
    """Matching not found exception"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            error_code=ErrorCodes.MTM_404,
            message=message or "Matching not found",
            details=details,
        )


class MatchingValidationError(BaseAPIException):
    """Matching validation error exception"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            error_code=ErrorCodes.MTM_400,
            message=message or "Matching validation error",
            details=details,
        )


class MatchingAccessDeniedError(BaseAPIException):
    """Matching access denied exception"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            error_code=ErrorCodes.MTM_403,
            message=message or "Access denied to this matching",
            details=details,
        )


class NoMoreReferralsError(BaseAPIException):
    """No more referrals available exception"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            error_code=ErrorCodes.MTM_404,
            message=message or "No more referrals available",
            details=details,
        )
