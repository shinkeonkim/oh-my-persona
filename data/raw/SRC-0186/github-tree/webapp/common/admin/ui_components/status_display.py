from django.utils.html import format_html


class AdminStatusDisplay:
    """어드민용 상태 표시 컴포넌트"""

    STATUSES = [
        "success",
        "warning",
        "danger",
        "info",
        "neutral",
    ]

    @staticmethod
    def create(
        text,
        text_color=None,
        bg_color=None,
        **kwargs,
    ):
        """상태 표시 생성"""
        if not text:
            return format_html('<span style="color: #6c757d;">-</span>')

        if text_color and bg_color:
            return AdminStatusDisplay._create_badge(text, text_color, bg_color, **kwargs)

        return AdminStatusDisplay._create_badge(text, "#6c757d", "#ffffff", **kwargs)

    @staticmethod
    def create_from_status_type(text, status_type, **kwargs):
        """상태 타입에 따른 상태 표시 생성"""
        if status_type in AdminStatusDisplay.STATUSES:
            return getattr(AdminStatusDisplay, status_type)(text, **kwargs)
        return AdminStatusDisplay.neutral(text, **kwargs)

    @staticmethod
    def _create_badge(text, text_color, bg_color, **kwargs):
        """배지 생성"""

        return format_html(
            "<div>"
            '<span style="display: inline-flex; align-items: center; padding: 4px 8px; '
            "background-color: {}; color: {}; border-radius: 12px; font-size: 11px; "
            'font-weight: 500;">{}</span>'
            "</div>",
            bg_color,
            text_color,
            text,
        )

    @staticmethod
    def success(text, **kwargs):
        """성공 상태 표시 (녹색)"""
        return AdminStatusDisplay.create(text, text_color="#155724", bg_color="#28a745")

    @staticmethod
    def warning(text, **kwargs):
        """경고 상태 표시 (노란색)"""
        return AdminStatusDisplay.create(text, text_color="#856404", bg_color="#ffc107")

    @staticmethod
    def danger(text, **kwargs):
        """위험 상태 표시 (빨간색)"""
        return AdminStatusDisplay.create(text, text_color="#721c24", bg_color="#dc3545")

    @staticmethod
    def info(text, **kwargs):
        """정보 상태 표시 (파란색)"""
        return AdminStatusDisplay.create(text, text_color="#0c5460", bg_color="#17a2b8")

    @staticmethod
    def neutral(text, **kwargs):
        """중립 상태 표시 (회색)"""
        return AdminStatusDisplay.create(text, text_color="#ffffff", bg_color="#6c757d")
