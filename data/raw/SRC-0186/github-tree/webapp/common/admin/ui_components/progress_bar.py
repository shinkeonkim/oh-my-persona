from django.utils.html import format_html
from django.utils.safestring import mark_safe


class AdminProgressBar:
    """어드민용 진행률 표시 컴포넌트"""

    @staticmethod
    def create(percentage, show_text=True, size="normal"):
        """진행률 바 생성"""
        # 색상 결정
        if percentage >= 80:
            color = "green"
        elif percentage >= 50:
            color = "yellow"
        else:
            color = "red"

        # 크기 설정
        height = "4px" if size == "small" else "6px" if size == "large" else "5px"
        font_size = "10px" if size == "small" else "14px" if size == "large" else "12px"

        text_html = ""
        if show_text:
            text_html = format_html(
                '<span style="font-size: {}; color: #666; margin-left: 8px;">{}%</span>',
                font_size,
                percentage,
            )

        return format_html(
            '<div style="display: flex; align-items: center;">'
            '<div style="flex: 1; background-color: #e5e7eb; border-radius: 10px; height: {};">'
            '<div style="background-color: {}; height: {}; border-radius: 10px; width: {}%;"></div>'
            "</div>"
            "{}"
            "</div>",
            height,
            color,
            height,
            percentage,
            text_html,
        )

    @staticmethod
    def profile_completion(profile, size="normal"):
        """프로필 완성도 표시"""
        if not profile:
            return mark_safe('<span style="color: #dc3545;">프로필 없음</span>')

        return AdminProgressBar.create(profile.completion_percentage, show_text=True, size=size)
