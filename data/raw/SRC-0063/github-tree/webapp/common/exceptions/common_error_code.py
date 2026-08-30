from enum import Enum


class CommonErrorCode(Enum):
    """Standardized error codes for API exceptions"""

    COMMON_400 = (
        "COMMON_400",
        "Bad request",
        "The request could not be understood or was missing required parameters.",
        400,
    )
    COMMON_401 = (
        "COMMON_401",
        "Unauthorized",
        "Authentication is required and has failed or has not yet been provided.",
        401,
    )
    COMMON_403 = ("COMMON_403", "Forbidden", "You do not have permission to access this resource.", 403)
    COMMON_404 = ("COMMON_404", "Not found", "The requested resource could not be found.", 404)
    COMMON_405 = ("COMMON_405", "Method not allowed", "The request method is not allowed for the resource.", 405)
    COMMON_409 = (
        "COMMON_409",
        "Conflict",
        "The request could not be completed due to a conflict with the current state of the resource.",
        409,
    )
    COMMON_413 = (
        "COMMON_413",
        "Payload too large",
        "The request is larger than the server is willing or able to process.",
        413,
    )
    COMMON_422 = (
        "COMMON_422",
        "Unprocessable entity",
        "The request was well-formed but was unable to be processed.",
        422,
    )
    COMMON_429 = ("COMMON_429", "Too many requests", "You have sent too many requests in a given amount of time.", 429)
    COMMON_500 = ("COMMON_500", "Internal server error", "An unexpected error occurred on the server.", 500)
    COMMON_503 = ("COMMON_503", "Service unavailable", "The server is currently unavailable (overloaded or down).", 503)
    COMMON_504 = (
        "COMMON_504",
        "Gateway timeout",
        "The server was acting as a gateway or proxy and did not receive a timely response from the upstream server.",
        504,
    )

    @property
    def code(self):
        return self.value[0]

    @property
    def message(self):
        return self.value[1]

    @property
    def description(self):
        return self.value[2]

    @property
    def status_code(self):
        return self.value[3]
