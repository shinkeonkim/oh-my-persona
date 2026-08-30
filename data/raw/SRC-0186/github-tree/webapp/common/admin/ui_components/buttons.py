from django.utils.html import format_html


class AdminButton:
    """어드민용 버튼 컴포넌트"""

    @staticmethod
    def _create_button(url, text, color):
        """공통 버튼 생성 메서드"""
        style = (
            "padding: 4px 8px; background-color: {}; color: white; "
            "text-decoration: none; border-radius: 3px; font-size: 11px; "
            "border: none; cursor: pointer;"
        )
        return format_html(
            '<a href="{}" class="button" style="{}">{}</a>',
            url,
            style.format(color),
            text,
        )

    @staticmethod
    def detail_button(url, text="상세 보기", color="#417690"):
        """상세보기 버튼"""
        return AdminButton._create_button(url, text, color)

    @staticmethod
    def edit_button(url, text="수정", color="#28a745"):
        """수정 버튼"""
        return AdminButton._create_button(url, text, color)

    @staticmethod
    def delete_button(url, text="삭제", color="#dc3545"):
        """삭제 버튼"""
        return AdminButton._create_button(url, text, color)
