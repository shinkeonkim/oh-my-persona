from dataclasses import dataclass


@dataclass
class ErrorCode:
    """Standardized error code with message and description"""

    code: str
    message: str
    description: str
    http_status: int


class ErrorCodes:
    """Collection of standardized error codes for API responses"""

    # Authentication & Authorization (AUTH-xxx)
    AUTH_401 = ErrorCode(
        code="AUTH-401",
        message="Authentication required",
        description="Authentication credentials were not provided or are invalid",
        http_status=401,
    )
    AUTH_403 = ErrorCode(
        code="AUTH-403",
        message="Access forbidden",
        description="You do not have permission to access this resource",
        http_status=403,
    )
    AUTH_404 = ErrorCode(
        code="AUTH-404",
        message="User not found",
        description="The requested user does not exist",
        http_status=404,
    )
    AUTH_409 = ErrorCode(
        code="AUTH-409",
        message="User already exists",
        description="A user with this information already exists",
        http_status=409,
    )
    AUTH_422 = ErrorCode(
        code="AUTH-422",
        message="Invalid credentials",
        description="The provided credentials are invalid or malformed",
        http_status=422,
    )
    AUTH_500 = ErrorCode(
        code="AUTH-500",
        message="Authentication service error",
        description="An error occurred in the authentication service",
        http_status=500,
    )

    # User Confirmation (CONF-xxx)
    USER_NOT_CONFIRMED = ErrorCode(
        code="CONF-403",
        message="User not confirmed",
        description="User account has not been confirmed by admin",
        http_status=403,
    )

    # Profile Access (PROF-xxx)
    PROFILE_ACCESS_DENIED = ErrorCode(
        code="PROF-403",
        message="Profile access denied",
        description="User does not have permission to access this profile",
        http_status=403,
    )

    # User Management (USR-xxx)
    USR_400 = ErrorCode(
        code="USR-400",
        message="Invalid user data",
        description="The provided user data is invalid or malformed",
        http_status=400,
    )
    USR_404 = ErrorCode(
        code="USR-404",
        message="User not found",
        description="The requested user does not exist",
        http_status=404,
    )
    USR_409 = ErrorCode(
        code="USR-409",
        message="User already exists",
        description="A user with this information already exists",
        http_status=409,
    )
    USR_422 = ErrorCode(
        code="USR-422",
        message="User validation error",
        description="The user data failed validation",
        http_status=422,
    )
    USR_500 = ErrorCode(
        code="USR-500",
        message="User service error",
        description="An error occurred while processing user data",
        http_status=500,
    )

    # Profile Management (PRF-xxx)
    PRF_400 = ErrorCode(
        code="PRF-400",
        message="Invalid profile data",
        description="The provided profile data is invalid or malformed",
        http_status=400,
    )
    PRF_404 = ErrorCode(
        code="PRF-404",
        message="Profile not found",
        description="The requested profile does not exist",
        http_status=404,
    )
    PRF_409 = ErrorCode(
        code="PRF-409",
        message="Profile already exists",
        description="A profile with this information already exists",
        http_status=409,
    )
    PRF_422 = ErrorCode(
        code="PRF-422",
        message="Profile validation error",
        description="The profile data failed validation",
        http_status=422,
    )
    PRF_500 = ErrorCode(
        code="PRF-500",
        message="Profile service error",
        description="An error occurred while processing profile data",
        http_status=500,
    )

    # File Management (FILE-xxx)
    FILE_400 = ErrorCode(
        code="FILE-400",
        message="Invalid file data",
        description="The provided file data is invalid or malformed",
        http_status=400,
    )
    FILE_404 = ErrorCode(
        code="FILE-404",
        message="File not found",
        description="The requested file does not exist",
        http_status=404,
    )
    FILE_413 = ErrorCode(
        code="FILE-413",
        message="File too large",
        description="The uploaded file exceeds the maximum allowed size",
        http_status=413,
    )
    FILE_415 = ErrorCode(
        code="FILE-415",
        message="Unsupported file type",
        description="The file type is not supported",
        http_status=415,
    )
    FILE_422 = ErrorCode(
        code="FILE-422",
        message="File validation error",
        description="The file data failed validation",
        http_status=422,
    )
    FILE_500 = ErrorCode(
        code="FILE-500",
        message="File service error",
        description="An error occurred while processing the file",
        http_status=500,
    )

    # Validation Errors (VAL-xxx)
    VAL_400 = ErrorCode(
        code="VAL-400",
        message="Validation error",
        description="The request data is invalid or malformed",
        http_status=400,
    )
    VAL_422 = ErrorCode(
        code="VAL-422",
        message="Field validation error",
        description="One or more fields failed validation",
        http_status=422,
    )

    # Server Common Errors (SRV-xxx)
    SRV_400 = ErrorCode(
        code="SRV-400",
        message="Bad request",
        description="The request is invalid",
        http_status=400,
    )
    SRV_404 = ErrorCode(
        code="SRV-404",
        message="Not found",
        description="The requested resource was not found",
        http_status=404,
    )
    SRV_409 = ErrorCode(
        code="SRV-409",
        message="Conflict",
        description="The request conflicts with the current state of the resource",
        http_status=409,
    )
    SRV_422 = ErrorCode(
        code="SRV-422",
        message="Unprocessable entity",
        description="The request was well-formed but was unable to be followed due to semantic errors",
        http_status=422,
    )
    SRV_429 = ErrorCode(
        code="SRV-429",
        message="Too many requests",
        description="The user has sent too many requests in a given amount of time",
        http_status=429,
    )
    SRV_500 = ErrorCode(
        code="SRV-500",
        message="Internal server error",
        description="An internal server error occurred",
        http_status=500,
    )
    SRV_503 = ErrorCode(
        code="SRV-503",
        message="Service unavailable",
        description="The service is temporarily unavailable",
        http_status=503,
    )

    # External Service Errors (EXT-xxx)
    EXT_400 = ErrorCode(
        code="EXT-400",
        message="External service error",
        description="An error occurred with an external service",
        http_status=400,
    )
    EXT_500 = ErrorCode(
        code="EXT-500",
        message="External service unavailable",
        description="An external service is temporarily unavailable",
        http_status=500,
    )

    # Matchmaking Errors (MTM-xxx)
    MTM_400 = ErrorCode(
        code="MTM-400",
        message="Matchmaking validation error",
        description="The matchmaking data is invalid or malformed",
        http_status=400,
    )
    MTM_403 = ErrorCode(
        code="MTM-403",
        message="Matchmaking access denied",
        description="You do not have permission to access this matchmaking resource",
        http_status=403,
    )
    MTM_404 = ErrorCode(
        code="MTM-404",
        message="Matchmaking not found",
        description="The requested matchmaking resource does not exist",
        http_status=404,
    )
    MTM_409 = ErrorCode(
        code="MTM-409",
        message="Matchmaking conflict",
        description="The matchmaking request conflicts with the current state",
        http_status=409,
    )
    MTM_422 = ErrorCode(
        code="MTM-422",
        message="Matchmaking validation error",
        description="The matchmaking data failed validation",
        http_status=422,
    )
    MTM_500 = ErrorCode(
        code="MTM-500",
        message="Matchmaking service error",
        description="An error occurred while processing matchmaking data",
        http_status=500,
    )

    # NICE API Identity Verification Errors (NICE-xxx)
    NICE_400 = ErrorCode(
        code="NICE-400",
        message="Invalid verification request",
        description="The identity verification request is invalid or malformed",
        http_status=400,
    )
    NICE_401 = ErrorCode(
        code="NICE-401",
        message="Session expired",
        description="The verification session has expired or is invalid",
        http_status=401,
    )
    NICE_422 = ErrorCode(
        code="NICE-422",
        message="Verification failed",
        description="Identity verification failed or was rejected by NICE API",
        http_status=422,
    )
    NICE_500 = ErrorCode(
        code="NICE-500",
        message="Verification service error",
        description="An error occurred while processing identity verification",
        http_status=500,
    )
    NICE_503 = ErrorCode(
        code="NICE-503",
        message="NICE API unavailable",
        description="NICE API service is temporarily unavailable",
        http_status=503,
    )
