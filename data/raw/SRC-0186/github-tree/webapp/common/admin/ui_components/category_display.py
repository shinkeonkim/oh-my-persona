from django.utils.safestring import mark_safe


class AdminCategoryDisplay:
    """카테고리 표시 컴포넌트"""

    @staticmethod
    def create(category, choices, color_mapping=None):
        """카테고리 표시 (색상 포함)"""
        if not category:
            return "-"

        # 기본 색상 매핑
        default_colors = {
            "purchase": ("green", "#d4edda"),
            "publish": ("purple", "#d8b4fe"),
            "use": ("red", "#f8d7da"),
            "refund": ("blue", "#d1ecf1"),
            "active": ("green", "#d4edda"),
            "inactive": ("gray", "#e9ecef"),
            "pending": ("orange", "#fff3cd"),
            "approved": ("green", "#d4edda"),
            "rejected": ("red", "#f8d7da"),
        }

        colors = color_mapping or default_colors
        color, bg_color = colors.get(category, ("gray", "#e9ecef"))

        # choices에서 display 값 찾기
        display_text = dict(choices).get(category, category)

        return mark_safe(
            f'<span style="background-color: {bg_color}; color: {color}; padding: 4px 8px; '
            f'border-radius: 4px; font-weight: bold;">{display_text}</span>'
        )
