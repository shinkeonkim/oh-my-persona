from django.utils.html import format_html


class AdminBadge:
    """어드민용 배지 컴포넌트"""

    @staticmethod
    def create(text, color, bg_color, size="normal"):
        """배지 생성"""
        padding = "6px 12px" if size == "large" else "4px 8px"
        font_size = "12px" if size == "large" else "11px"

        return format_html(
            '<span style="background-color: {}; color: {}; padding: {}; '
            'border-radius: 4px; font-weight: bold; font-size: {};">{}</span>',
            bg_color,
            color,
            padding,
            font_size,
            text,
        )

    @staticmethod
    def success(text, size="normal"):
        """성공 배지 (녹색)"""
        return AdminBadge.create(text, "white", "#28a745", size)

    @staticmethod
    def warning(text, size="normal"):
        """경고 배지 (주황색)"""
        return AdminBadge.create(text, "white", "#ffc107", size)

    @staticmethod
    def danger(text, size="normal"):
        """위험 배지 (빨간색)"""
        return AdminBadge.create(text, "white", "#dc3545", size)

    @staticmethod
    def info(text, size="normal"):
        """정보 배지 (파란색)"""
        return AdminBadge.create(text, "white", "#17a2b8", size)

    @staticmethod
    def secondary(text, size="normal"):
        """보조 배지 (회색)"""
        return AdminBadge.create(text, "white", "#6c757d", size)
