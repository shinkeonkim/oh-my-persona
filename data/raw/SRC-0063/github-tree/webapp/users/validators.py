import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_username(value):
    """
    Username 검증:
    - 4자리 이상
    - 영문과 숫자 조합 (둘 다 포함되어야 함)
    """
    if len(value) < 4:
        raise ValidationError(
            _("Username must be at least 4 characters long."),
            code="username_too_short",
        )

    # 영문만 있는지 체크
    if value.isalpha():
        raise ValidationError(
            _("Username must contain both letters and numbers."),
            code="username_no_numbers",
        )

    # 숫자만 있는지 체크
    if value.isdigit():
        raise ValidationError(
            _("Username must contain both letters and numbers."),
            code="username_no_letters",
        )

    # 영문과 숫자만 허용 (특수문자 제외)
    if not re.match(r"^[a-zA-Z0-9]+$", value):
        raise ValidationError(
            _("Username must contain only letters and numbers."),
            code="username_invalid_characters",
        )


def validate_password(value):
    """
    Password 검증:
    - 8자리 이상
    - 영문과 숫자 조합 (둘 다 포함되어야 함)
    """
    if len(value) < 8:
        raise ValidationError(
            _("Password must be at least 8 characters long."),
            code="password_too_short",
        )

    # 영문이 포함되어 있는지 체크
    if not re.search(r"[a-zA-Z]", value):
        raise ValidationError(
            _("Password must contain both letters and numbers."),
            code="password_no_letters",
        )

    # 숫자가 포함되어 있는지 체크
    if not re.search(r"[0-9]", value):
        raise ValidationError(
            _("Password must contain both letters and numbers."),
            code="password_no_numbers",
        )
