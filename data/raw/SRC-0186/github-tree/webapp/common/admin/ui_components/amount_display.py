from django.utils.safestring import mark_safe


class AdminAmountDisplay:
    """수량 표시 컴포넌트"""

    @staticmethod
    def create(amount, prefix="", suffix=""):
        """수량 표시 (색상 포함)"""
        if amount > 0:
            color = "green"
            bg_color = "#d4edda"
            display_prefix = "+" if not prefix else prefix
        elif amount < 0:
            color = "red"
            bg_color = "#f8d7da"
            display_prefix = "" if not prefix else prefix
        else:
            color = "gray"
            bg_color = "#e9ecef"
            display_prefix = "" if not prefix else prefix

        return mark_safe(
            f'<span style="background-color: {bg_color}; color: {color}; padding: 4px 8px; '
            f'border-radius: 4px; font-weight: bold;">{display_prefix}{amount}{suffix}</span>'
        )
