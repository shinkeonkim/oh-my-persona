from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class AdminActions:
    """어드민용 액션 버튼 컴포넌트"""

    # 공통 버튼 스타일
    BASE_BUTTON_STYLE = (
        "display: inline-flex; align-items: center; padding: 4px 8px; "
        "text-decoration: none; border-radius: 4px; font-size: 11px; "
        "font-weight: 500; transition: all 0.2s;"
    )

    @staticmethod
    def _create_button(url, text, border_color, text_color, bg_color):
        """공통 버튼 생성 메서드 (XSS 방지)"""
        return format_html(
            '<a href="{}" style="{} border: 1px solid {}; color: {}; background: {};">{}</a>',
            url,
            AdminActions.BASE_BUTTON_STYLE,
            border_color,
            text_color,
            bg_color,
            text,
        )

    @staticmethod
    def create(buttons):
        """액션 버튼들 생성"""
        if not buttons:
            return format_html("<div></div>")

        # 각 버튼이 이미 format_html로 생성된 안전한 HTML이므로
        # format_html을 사용하여 안전하게 연결
        return format_html(
            '<div style="display: flex; gap: 4px; flex-wrap: wrap;">{}</div>',
            mark_safe("".join(buttons)),
        )

    @staticmethod
    def edit_button(obj, app_label, model_name, text="수정"):
        """수정 버튼"""
        url = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.pk])
        return AdminActions._create_button(url, text, "#d1d5db", "#374151", "white")

    @staticmethod
    def view_button(obj, app_label, model_name, text="보기"):
        """보기 버튼"""
        url = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.pk])
        return AdminActions._create_button(url, text, "#3b82f6", "white", "#3b82f6")

    @staticmethod
    def filter_button(url, text, color="#6b7280"):
        """필터 버튼"""
        return AdminActions._create_button(url, text, color, "white", color)

    @staticmethod
    def success_button(url, text):
        """성공 버튼 (녹색)"""
        return AdminActions._create_button(url, text, "#16a34a", "white", "#16a34a")

    @staticmethod
    def warning_button(url, text):
        """경고 버튼 (주황색)"""
        return AdminActions._create_button(url, text, "#ea580c", "white", "#ea580c")

    @staticmethod
    def danger_button(url, text):
        """위험 버튼 (빨간색)"""
        return AdminActions._create_button(url, text, "#dc2626", "white", "#dc2626")

    @staticmethod
    def info_button(url, text):
        """정보 버튼 (파란색)"""
        return AdminActions._create_button(url, text, "#3b82f6", "white", "#3b82f6")

    @staticmethod
    def profile_button(profile_id, text="프로필"):
        """프로필 버튼 (reverse 사용)"""
        url = reverse("admin:profiles_profile_change", args=[profile_id])
        return AdminActions.info_button(url, text)

    @staticmethod
    def create_buttons_from_types(obj, app_label, model_name, button_types):
        """버튼 타입 리스트로부터 버튼들 생성"""
        button_methods = {
            "edit": lambda: AdminActions.edit_button(obj, app_label, model_name),
            "view": lambda: AdminActions.view_button(obj, app_label, model_name),
            "success": lambda: AdminActions.success_button(f"/admin/{app_label}/{model_name}/{obj.pk}/change/", "성공"),
            "warning": lambda: AdminActions.warning_button(f"/admin/{app_label}/{model_name}/{obj.pk}/change/", "경고"),
            "danger": lambda: AdminActions.danger_button(f"/admin/{app_label}/{model_name}/{obj.pk}/change/", "위험"),
            "info": lambda: AdminActions.info_button(f"/admin/{app_label}/{model_name}/{obj.pk}/change/", "정보"),
        }

        buttons = []
        for button_type in button_types:
            if method := button_methods.get(button_type):
                buttons.append(method())

        return AdminActions.create(buttons)
