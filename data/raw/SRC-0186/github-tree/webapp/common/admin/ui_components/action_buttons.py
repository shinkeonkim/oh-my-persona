from django.urls import reverse
from django.utils.html import format_html

from .buttons import AdminButton


class AdminActionButtons:
    """액션 버튼 컴포넌트"""

    @staticmethod
    def detail_button(obj, app_label, model_name, text="상세 보기"):
        """상세보기 버튼"""
        url = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.pk])
        return AdminButton.detail_button(url, text)

    @staticmethod
    def edit_button(obj, app_label, model_name, text="수정"):
        """수정 버튼"""
        url = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.pk])
        return AdminButton.edit_button(url, text)

    @staticmethod
    def delete_button(obj, app_label, model_name, text="삭제"):
        """삭제 버튼"""
        url = reverse(f"admin:{app_label}_{model_name}_delete", args=[obj.pk])
        return AdminButton.delete_button(url, text)

    @staticmethod
    def history_button(obj, app_label, model_name, text="이력"):
        """이력 버튼"""
        url = reverse(f"admin:{app_label}_{model_name}_history", args=[obj.pk])
        return AdminButton.detail_button(url, text, color="#6c757d")

    @staticmethod
    def duplicate_button(obj, app_label, model_name, text="복제"):
        """복제 버튼"""
        url = reverse(f"admin:{app_label}_{model_name}_add") + f"?duplicate={obj.pk}"
        return AdminButton.edit_button(url, text, color="#17a2b8")

    @staticmethod
    def combined_buttons(obj, app_label, model_name, buttons=None):
        """복합 버튼 (상세보기 + 수정)"""
        if buttons is None:
            buttons = ["detail", "edit"]

        # 버튼 타입과 생성 메서드 매핑 (확장 가능)
        button_methods = {
            "detail": AdminActionButtons.detail_button,
            "edit": AdminActionButtons.edit_button,
            "delete": AdminActionButtons.delete_button,
            "history": AdminActionButtons.history_button,
            "duplicate": AdminActionButtons.duplicate_button,
        }

        button_htmls = []
        for button_type in buttons:
            if method := button_methods.get(button_type):
                button_htmls.append(method(obj, app_label, model_name))

        return format_html('<div style="display: flex; gap: 5px;">{}</div>', "".join(button_htmls))
