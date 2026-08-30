from django.utils.html import format_html

# 색상 상수
COLOR_GREEN = "#4CAF50"
COLOR_ORANGE = "#FF9800"
COLOR_RED = "#F44336"
COLOR_BLUE = "#2196F3"
COLOR_GREY = "#9E9E9E"

# 레포트 상태별 색상 맵핑
REPORT_STATUS_COLORS = {
    "no_games_played": COLOR_GREY,
    "pending": COLOR_BLUE,
    "generating": COLOR_BLUE,
    "completed": COLOR_GREEN,
    "error": COLOR_RED,
}


# 공통 유틸리티 함수
def render_colored_score(score: int) -> str:
    """점수에 따라 색상이 적용된 HTML 반환"""
    if score >= 80:
        color = COLOR_GREEN
    elif score >= 60:
        color = COLOR_ORANGE
    else:
        color = COLOR_RED

    return format_html(
        '<strong style="color: {}; font-size: 1.1em;">{}</strong>',
        color,
        score,
    )


def render_badge(text: str, color: str) -> str:
    """뱃지 스타일 HTML 반환"""
    return format_html(
        '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 0.85em;">{}</span>',
        color,
        text,
    )


def render_count(count: int, unit: str = "개") -> str:
    """개수 표시 HTML 반환"""
    return format_html(
        "<strong>{}</strong>{}",
        count,
        unit,
    )


def render_colored_text(text: str, color: str) -> str:
    """색상이 적용된 텍스트 HTML 반환"""
    return format_html(
        '<span style="color: {};">{}</span>',
        color,
        text,
    )


def render_two_line_info(main_text: str, sub_text: str) -> str:
    """메인 텍스트와 서브 텍스트를 두 줄로 표시하는 HTML 반환"""
    return format_html(
        "<strong>{}</strong><br/><small>{}</small>",
        main_text,
        sub_text,
    )
