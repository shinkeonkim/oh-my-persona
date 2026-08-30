from django.utils.html import format_html


class AdminDescriptionPreview:
    """설명 미리보기 컴포넌트 (XSS 방지)"""

    @staticmethod
    def create(description, max_length=50, show_tooltip=True):
        """설명 미리보기 (XSS 방지)"""
        if not description:
            return "-"

        if len(description) <= max_length:
            return description

        preview = description[:max_length] + "..."

        if show_tooltip:
            return format_html('<span title="{}">{}</span>', description, preview)

        return preview
