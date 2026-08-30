"""CSS 값 하나하나를 파이썬 값으로 바꾸는 함수들.

전부 "못 읽으면 기본값" 규칙을 지킨다. CSS 는 모르는 값을 만나면 그 선언을
버릴 뿐 페이지를 멈추지 않기 때문이다.
"""

import skia

NAMED_COLORS = {
    "black": "#000000", "white": "#ffffff", "red": "#ff0000",
    "green": "#008000", "blue": "#0000ff", "gray": "#808080",
    "grey": "#808080", "lightblue": "#add8e6", "lightgreen": "#90ee90",
    "orange": "#ffa500", "purple": "#800080", "yellow": "#ffff00",
    "transparent": "#00000000",
}

BLEND_MODES = {
    "multiply": skia.BlendMode.kMultiply,
    "difference": skia.BlendMode.kDifference,
    "destination-in": skia.BlendMode.kDstIn,
    "source-over": skia.BlendMode.kSrcOver,
}


def parse_color(color):
    if color in NAMED_COLORS:
        color = NAMED_COLORS[color]
    if color.startswith("#") and len(color) == 7:
        return skia.Color(int(color[1:3], 16), int(color[3:5], 16),
                          int(color[5:7], 16))
    if color.startswith("#") and len(color) == 9:
        return skia.Color(int(color[1:3], 16), int(color[3:5], 16),
                          int(color[5:7], 16), int(color[7:9], 16))
    return skia.ColorBLACK


def parse_rgb(color):
    """색을 (r, g, b) 로. 애니메이션이 채널마다 보간할 때 쓴다."""
    color = NAMED_COLORS.get(color, color)
    if color.startswith("#") and len(color) >= 7:
        return (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16))
    return (0, 0, 0)


def parse_blend_mode(name):
    return BLEND_MODES.get(name, skia.BlendMode.kSrcOver)


def parse_px_value(value, default=0.0):
    """'12px' -> 12.0. 단위가 없어도 숫자면 받는다."""
    if not value:
        return default
    value = value.strip()
    if value.endswith("px"):
        value = value[:-2]
    try:
        return float(value)
    except ValueError:
        return default


def parse_px(value):
    """'12px' -> 12.0, 'auto' 나 이상한 값 -> None."""
    if not value or value.strip().casefold() == "auto":
        return None
    value = value.strip()
    if value.endswith("px"):
        value = value[:-2]
    try:
        return float(value)
    except ValueError:
        return None


def parse_transform(value):
    """'translate(12px, 30px)' -> (12.0, 30.0). 아니면 None."""
    if not value:
        return None
    value = value.strip()
    if not value.casefold().startswith("translate(") or \
            not value.endswith(")"):
        return None
    parts = value[len("translate("):-1].split(",")
    if len(parts) != 2:
        return None
    return parse_px_value(parts[0]), parse_px_value(parts[1])


def parse_blur(filter_value):
    """'blur(4px)' -> 4.0. 다른 필터는 0."""
    if not filter_value:
        return 0.0
    value = filter_value.strip()
    if not value.casefold().startswith("blur(") or not value.endswith(")"):
        return 0.0
    return parse_px_value(value[len("blur("):-1])


def parse_outline(value):
    """'2px solid black' -> (2, 'black'). 아니면 (None, None)."""
    if not value:
        return None, None
    parts = value.split()
    if len(parts) != 3 or parts[1] != "solid":
        return None, None
    return int(parse_px_value(parts[0])), parts[2]


def parse_url_value(value):
    """'url(cat.png)' 또는 'url("cat.png")' -> 'cat.png'."""
    if not value:
        return None
    value = value.strip()
    if not value.casefold().startswith("url(") or not value.endswith(")"):
        return None
    inner = value[4:-1].strip()
    if len(inner) >= 2 and inner[0] == inner[-1] and inner[0] in "\"'":
        inner = inner[1:-1]
    return inner or None


def parse_zoom(value):
    """'150%' 또는 '1.5' -> 1.5."""
    if not value:
        return 1.0
    value = value.strip()
    try:
        if value.endswith("%"):
            return float(value[:-1]) / 100
        return float(value)
    except ValueError:
        return 1.0


def parse_aspect_ratio(value):
    """'16 / 9' 또는 '1.5' -> 비율. 없거나 이상하면 None."""
    if not value:
        return None
    value = value.strip()
    try:
        if "/" in value:
            a, _, b = value.partition("/")
            return float(a) / float(b)
        return float(value)
    except (ValueError, ZeroDivisionError):
        return None


def size_from_ratio(width, height, ratio, default_w, default_h):
    """한 축만 주어졌으면 비율로 나머지를 채운다."""
    if ratio is None or ratio <= 0:
        return (width if width is not None else default_w,
                height if height is not None else default_h)
    if width is not None and height is None:
        return width, width / ratio
    if height is not None and width is None:
        return height * ratio, height
    if width is None and height is None:
        return default_w, default_w / ratio
    return width, height


def expand_shorthand(prop, value):
    """단축 속성을 편다. 지금은 font 하나뿐.

    'font: italic bold 100% Times' -> 네 속성
    """
    if prop != "font":
        return {prop: value}
    parts = value.split()
    out = {}
    styles = {"normal", "italic", "oblique"}
    weights = {"normal", "bold", "bolder", "lighter"}
    i = 0
    while i < len(parts) and (parts[i].casefold() in styles | weights):
        p = parts[i].casefold()
        if p in styles and "font-style" not in out:
            out["font-style"] = p
        elif p in weights and "font-weight" not in out:
            out["font-weight"] = p
        i += 1
    if i < len(parts):
        out["font-size"] = parts[i]
        i += 1
    if i < len(parts):
        out["font-family"] = " ".join(parts[i:])
    return out
