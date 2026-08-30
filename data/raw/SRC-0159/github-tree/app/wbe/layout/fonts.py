"""폰트.

`Font` 는 `skia.Font` 를 감싸 `measure()` 와 `metrics()` 를 준다. 배치 코드는
이 두 메서드만 쓰므로 자기가 무엇 위에서 도는지 알 필요가 없다.
"""

import skia

DEFAULT_FAMILY = "Arial"
MONO_FAMILY = "Courier New"

# 위 첨자와 스몰 캡의 크기 비율
SUP_SCALE = 0.5
SMALLCAPS_SCALE = 0.75

SOFT_HYPHEN = "\N{soft hyphen}"

FONTS = {}


class Font:
    def __init__(self, skia_font, family, weight, style, size):
        self.skia_font = skia_font
        self.family = family
        self.weight = weight
        self.style = style
        self.size = size
        m = skia_font.getMetrics()
        self._ascent = -m.fAscent
        self._descent = m.fDescent

    def measure(self, text):
        return self.skia_font.measureText(text)

    def metrics(self, name=None):
        out = {"ascent": self._ascent, "descent": self._descent,
               "linespace": self._ascent + self._descent}
        return out[name] if name else out

    def cget(self, name):
        return {"family": self.family, "weight": self.weight,
                "slant": self.style, "size": self.size}[name]

    def __repr__(self):
        return "Font(%s %s %s %d)" % (self.family, self.weight, self.style,
                                      self.size)


def get_font(size, weight="normal", style="roman", family=None):
    family = family or DEFAULT_FAMILY
    if family.casefold() == "monospace":
        family = MONO_FAMILY
    size = int(size)
    key = (family, weight, style, size)
    if key not in FONTS:
        skia_weight = skia.FontStyle.kBold_Weight if weight == "bold" \
            else skia.FontStyle.kNormal_Weight
        skia_style = skia.FontStyle.kItalic_Slant if style == "italic" \
            else skia.FontStyle.kUpright_Slant
        info = skia.FontStyle(skia_weight, skia.FontStyle.kNormal_Width,
                              skia_style)
        FONTS[key] = Font(skia.Font(skia.Typeface(family, info), size),
                          family, weight, style, size)
    return FONTS[key]


def font_for_style(style, zoom=1.0, superscript=False, scale=1.0,
                   weight=None):
    """계산된 스타일에서 폰트를 고른다."""
    css_style = style["font-style"]
    css_style = "roman" if css_style == "normal" else css_style
    size = int(float(style["font-size"][:-2]) * 0.75 * zoom)
    if superscript:
        size = max(6, int(size * SUP_SCALE))
    if scale != 1.0:
        size = max(6, int(size * scale))
    return get_font(max(1, size), weight or style["font-weight"], css_style,
                    style.get("font-family") or None)
