from django.utils.html import format_html


class AdminScoreDisplay:
    """어드민용 점수 표시 컴포넌트"""

    @staticmethod
    def create(score, thresholds={"high": 80, "medium": 60}, show_bg=True):
        """점수 표시 생성"""
        if score is None:
            return "-"

        category = AdminScoreDisplay._get_category(score, thresholds)
        return AdminScoreDisplay._create_category_badge(score, category)

    @staticmethod
    def high(score, show_bg=True):
        """높은 점수 표시 (녹색)"""
        return AdminScoreDisplay._create_category_badge(score, "high")

    @staticmethod
    def medium(score, show_bg=True):
        """중간 점수 표시 (주황색)"""
        return AdminScoreDisplay._create_category_badge(score, "medium")

    @staticmethod
    def low(score, show_bg=True):
        """낮은 점수 표시 (빨간색)"""
        return AdminScoreDisplay._create_category_badge(score, "low")

    @staticmethod
    def _get_category(score, thresholds):
        if score >= thresholds["high"]:
            return "high"
        elif score >= thresholds["medium"]:
            return "medium"
        else:
            return "low"

    @staticmethod
    def _create_category_badge(score, category=None):
        colors = {
            "high": ("green", "#d4edda"),
            "medium": ("orange", "#fff3cd"),
            "low": ("red", "#f8d7da"),
            "default": ("gray", "#e9ecef"),
        }

        color, bg_color = colors.get(category, colors["default"])
        return AdminScoreDisplay._create_badge(score, color, bg_color)

    @staticmethod
    def _create_badge(score, color, bg_color):
        return format_html(
            '<span style="display: inline-flex; align-items: center;'
            + "padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 500;"
            + f'color: {color}; background-color: {bg_color}; font-weight: bold;">{score}</span>'
        )
