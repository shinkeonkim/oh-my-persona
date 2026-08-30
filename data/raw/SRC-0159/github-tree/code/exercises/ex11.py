"""11장 연습문제 구현 (11-1 ~ 11-5).

lab11.py 는 그대로 두고, 1~10장 연습문제를 이어받아 그 위에 11장 기능을 얹는다.

    python3 ex11.py http://localhost:8000/

11장은 그리기 바탕을 Tk 에서 Skia + SDL 로 갈아 끼운다. 배치 코드는 그대로 두고
**폰트와 그리기 명령만 바꿔 끼우는** 방식을 썼다(아래 `install_backend`).
그래서 3~10장에서 만든 배치 기능이 한 줄도 다시 쓰이지 않고 그대로 산다.

11장 본문 기능(opacity, mix-blend-mode, border-radius, overflow: clip)에 더해

    11-1 필터           filter: blur(Npx)
    11-2 히트 테스팅     둥근 모서리 밖은 클릭이 아니다
    11-3 관심 영역       페이지 전체가 아니라 화면 둘레만 래스터
    11-4 오버플로 스크롤  overflow: scroll 인 요소를 방향키로
    11-5 터치 입력       탭·두 손가락 스크롤
"""

import math
import os
import sys

import skia

import ex10
from ex3 import SUP_SCALE
from ex4 import Text, Element
from ex5 import (LINKS_BAR_COLOR, TOC_COLOR, TOC_LABEL, BULLET_SIZE,
                 LIST_INDENT)
from ex6 import tree_to_list, group_children, parse_px
from ex7 import Rect, HOME_URL
from ex8 import (CHECKBOX_SIZE, INPUT_WIDTH_PX, BUTTON_PADDING, _Box,
                 TextLayout as TextLayout8, LineLayout as LineLayout8,
                 ButtonLayout as ButtonLayout8)

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100
AOI_HEIGHT = 4 * HEIGHT              # 연습문제 11-3

FONTS = {}

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


def parse_blend_mode(name):
    return BLEND_MODES.get(name, skia.BlendMode.kSrcOver)


def parse_px_value(value, default=0.0):
    if not value:
        return default
    value = value.strip()
    if value.endswith("px"):
        value = value[:-2]
    try:
        return float(value)
    except ValueError:
        return default


def parse_blur(filter_value):
    """연습문제 11-1: 'blur(4px)' -> 4.0. 아니면 0."""
    if not filter_value:
        return 0.0
    value = filter_value.strip()
    if not value.casefold().startswith("blur(") or not value.endswith(")"):
        return 0.0
    return parse_px_value(value[len("blur("):-1])


# ---------------------------------------------------------------------- #
# 폰트 — Tk 폰트와 같은 얼굴을 하고 있어서 배치 코드가 눈치채지 못한다
# ---------------------------------------------------------------------- #

class Font:
    """skia.Font 를 감싸 measure()/metrics() 를 준다."""

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


DEFAULT_FAMILY = "Arial"
MONO_FAMILY = "Courier New"


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
        typeface = skia.Typeface(family, info)
        FONTS[key] = Font(skia.Font(typeface, size), family, weight, style,
                          size)
    return FONTS[key]


def skia_rect(rect):
    return skia.Rect.MakeLTRB(rect.left, rect.top, rect.right, rect.bottom)


# ---------------------------------------------------------------------- #
# 그리기 명령 — 생성자 모양은 7~10장과 똑같이 두었다
# ---------------------------------------------------------------------- #

class DrawCommand:
    def __init__(self, rect, node=None):
        self.rect = rect
        self.node = node
        self.children = []

    @property
    def top(self):
        return self.rect.top

    @property
    def left(self):
        return self.rect.left

    @property
    def bottom(self):
        return self.rect.bottom

    @property
    def right(self):
        return self.rect.right


class DrawText(DrawCommand):
    def __init__(self, x1, y1, text, font, color="black", node=None):
        super().__init__(
            Rect(x1, y1, x1 + font.measure(text),
                 y1 + font.metrics("linespace")), node)
        self.text, self.font, self.color = text, font, color

    def execute(self, canvas):
        paint = skia.Paint(AntiAlias=True, Color=parse_color(self.color))
        baseline = self.rect.top + self.font.metrics("ascent")
        canvas.drawString(self.text, float(self.rect.left), float(baseline),
                          self.font.skia_font, paint)

    def __repr__(self):
        return "DrawText(%r)" % self.text


class DrawRect(DrawCommand):
    def __init__(self, rect, color, node=None):
        super().__init__(rect, node)
        self.color = color

    def execute(self, canvas):
        canvas.drawRect(skia_rect(self.rect),
                        skia.Paint(Color=parse_color(self.color)))

    def __repr__(self):
        return "DrawRect(%s)" % self.color


class DrawRRect(DrawCommand):
    def __init__(self, rect, radius, color, node=None):
        super().__init__(rect, node)
        self.radius = radius
        self.color = color

    def execute(self, canvas):
        rrect = skia.RRect.MakeRectXY(skia_rect(self.rect), self.radius,
                                      self.radius)
        canvas.drawRRect(rrect, skia.Paint(Color=parse_color(self.color)))

    def __repr__(self):
        return "DrawRRect(r=%g, %s)" % (self.radius, self.color)


class DrawOutline(DrawCommand):
    def __init__(self, rect, color, thickness, node=None):
        super().__init__(rect, node)
        self.color, self.thickness = color, thickness

    def execute(self, canvas):
        canvas.drawRect(skia_rect(self.rect),
                        skia.Paint(Color=parse_color(self.color),
                                   Style=skia.Paint.kStroke_Style,
                                   StrokeWidth=self.thickness))


class DrawLine(DrawCommand):
    def __init__(self, x1, y1, x2, y2, color, thickness, node=None):
        super().__init__(Rect(x1, y1, x2, y2), node)
        self.color, self.thickness = color, thickness

    def execute(self, canvas):
        path = skia.Path().moveTo(self.rect.left, self.rect.top) \
            .lineTo(self.rect.right, self.rect.bottom)
        canvas.drawPath(path, skia.Paint(Color=parse_color(self.color),
                                         Style=skia.Paint.kStroke_Style,
                                         StrokeWidth=self.thickness))


def union(children):
    if not children:
        return Rect(0, 0, 0, 0)
    left = min(c.rect.left for c in children)
    top = min(c.rect.top for c in children)
    right = max(c.rect.right for c in children)
    bottom = max(c.rect.bottom for c in children)
    return Rect(left, top, right, bottom)


class Blend(DrawCommand):
    """투명도·블렌드 모드·블러를 한 겹 씌운다."""

    def __init__(self, opacity, blend_mode, children, node=None, blur=0.0):
        super().__init__(union(children), node)
        self.opacity = opacity
        self.blend_mode = blend_mode
        self.blur = blur                       # 연습문제 11-1
        self.children = children
        self.should_save = bool(blend_mode) or opacity < 1 or blur > 0

    def paint(self):
        paint = skia.Paint(Alphaf=self.opacity,
                           BlendMode=parse_blend_mode(self.blend_mode))
        if self.blur > 0:
            # 블러는 투명도·블렌딩보다 **안쪽**에서 일어난다. 즉 자식들을 흐리게
            # 만든 뒤 그 결과에 알파와 블렌드 모드를 적용한다.
            paint.setImageFilter(skia.ImageFilters.Blur(
                sigmaX=self.blur / 2, sigmaY=self.blur / 2))
        return paint

    def execute(self, canvas):
        if self.should_save:
            canvas.saveLayer(None, self.paint())
        for cmd in self.children:
            cmd.execute(canvas)
        if self.should_save:
            canvas.restore()

    def __repr__(self):
        return "Blend(op=%g, mode=%s, blur=%g)" % (
            self.opacity, self.blend_mode, self.blur)


class Translate(DrawCommand):
    """연습문제 11-4: 안쪽 내용을 스크롤한 만큼 민다."""

    def __init__(self, dx, dy, children, node=None):
        rect = union(children)
        super().__init__(Rect(rect.left + dx, rect.top + dy,
                              rect.right + dx, rect.bottom + dy), node)
        self.dx, self.dy = dx, dy
        self.children = children

    def execute(self, canvas):
        canvas.save()
        canvas.translate(self.dx, self.dy)
        for cmd in self.children:
            cmd.execute(canvas)
        canvas.restore()

    def __repr__(self):
        return "Translate(%g, %g)" % (self.dx, self.dy)


# ---------------------------------------------------------------------- #
# 시각 효과
# ---------------------------------------------------------------------- #

def border_radius(node):
    return parse_px_value(node.style.get("border-radius", "0px"))


def is_scrollable(node):
    """연습문제 11-4: overflow: scroll 이고 높이가 정해진 요소."""
    return node.style.get("overflow", "visible") == "scroll" \
        and parse_px_value(node.style.get("height", ""), 0) > 0


def paint_visual_effects(node, cmds, rect):
    opacity = float(node.style.get("opacity", "1.0"))
    blend_mode = node.style.get("mix-blend-mode")
    blur = parse_blur(node.style.get("filter"))          # 연습문제 11-1
    overflow = node.style.get("overflow", "visible")
    radius = border_radius(node)

    if is_scrollable(node):                              # 연습문제 11-4
        cmds = [Translate(0, -getattr(node, "scroll_offset", 0), cmds, node)]

    if overflow in ("clip", "scroll"):
        if not blend_mode:
            blend_mode = "source-over"
        cmds = cmds + [Blend(1.0, "destination-in",
                             [DrawRRect(rect, radius, "white", node)], node)]

    return [Blend(opacity, blend_mode, cmds, node, blur)]


def paint_tree(layout_object, display_list):
    cmds = []
    if layout_object.should_paint():
        cmds = layout_object.paint()
    for child in layout_object.children:
        paint_tree(child, cmds)
    if layout_object.should_paint():
        cmds = layout_object.paint_effects(cmds)
    display_list.extend(cmds)


def flatten(cmds, out=None):
    """중첩된 그리기 명령을 모두 훑는다 (히트 테스팅용)."""
    out = [] if out is None else out
    for cmd in cmds:
        out.append(cmd)
        flatten(getattr(cmd, "children", []), out)
    return out


# ---------------------------------------------------------------------- #
# 배치 코드가 쓰는 이름을 11장 것으로 바꿔 끼운다
# ---------------------------------------------------------------------- #

def install_backend():
    """3~10장 모듈의 get_font 와 그리기 명령을 Skia 판으로 교체한다.

    배치 코드는 자기 모듈의 전역에서 이 이름들을 찾으므로, 여기만 바꿔 두면
    지금까지 만든 모든 배치 기능이 그대로 Skia 위에서 돈다.
    """
    import ex3, ex5, ex7, ex8, ex9
    for mod in (ex3, ex5, ex7, ex8, ex9, ex10):
        if hasattr(mod, "get_font"):
            mod.get_font = get_font
        for name in ("DrawText", "DrawRect", "DrawLine", "DrawOutline"):
            if hasattr(mod, name):
                setattr(mod, name, globals()[name])
    ex7.paint_tree = paint_tree
    ex8.paint_tree = paint_tree
    ex10.paint_tree = paint_tree


install_backend()


# ---------------------------------------------------------------------- #
# 레이아웃 — 그리기와 효과만 11장 것으로
# ---------------------------------------------------------------------- #

class TextLayout(TextLayout8):
    def should_paint(self):
        return True

    def paint(self):
        return [DrawText(self.x, self.y, self.word, self.font,
                         self.color, self.node)]

    def paint_effects(self, cmds):
        return cmds


class LineLayout(LineLayout8):
    def should_paint(self):
        return True

    def paint(self):
        return []

    def paint_effects(self, cmds):
        return cmds


class InputLayout(ex10.InputLayout):
    def should_paint(self):
        return not self.is_hidden()

    def paint_effects(self, cmds):
        return paint_visual_effects(self.node, cmds, self.self_rect())


class ButtonLayout(ButtonLayout8):
    def layout(self):
        """안쪽도 11장 BlockLayout 으로. 그래야 효과와 그리기가 이어진다."""
        avail = max(40, min(self.MAX_WIDTH, self.parent.width) -
                    2 * BUTTON_PADDING)
        self.width = avail + 2 * BUTTON_PADDING
        if self.previous:
            space = self.previous.font.measure(" ") if self.previous.space else 0
            self.x = self.previous.x + space + self.previous.width
        else:
            self.x = self.parent.x
        self.inner = BlockLayout([self.node], _Box(self, avail), None,
                                 skip_self=True)
        self.inner.layout()
        self.height = self.inner.height + 2 * BUTTON_PADDING

    def should_paint(self):
        return True

    def paint(self):
        cmds = []
        bg = self.node.style.get("background-color", "transparent")
        if bg != "transparent":
            radius = border_radius(self.node)
            if radius > 0:
                cmds.append(DrawRRect(self.self_rect(), radius, bg, self.node))
            else:
                cmds.append(DrawRect(self.self_rect(), bg, self.node))
        cmds.append(DrawOutline(self.self_rect(), "black", 1, self.node))
        paint_tree(self.inner, cmds)
        return cmds

    def paint_effects(self, cmds):
        return cmds


class BlockLayout(ex10.BlockLayout):
    # -- 폰트: 11장의 get_font 를 쓴다 --------------------------------- #

    def font_for(self, node, scale=1.0, weight=None):
        s = node.style
        style_ = s["font-style"]
        style_ = "roman" if style_ == "normal" else style_
        size = int(float(s["font-size"][:-2]) * 0.75)
        if self.superscript:
            size = max(6, int(size * SUP_SCALE))
        if scale != 1.0:
            size = max(6, int(size * scale))
        return get_font(size, weight or s["font-weight"], style_,
                        s.get("font-family") or None)

    def toc_label_height(self):
        el = self.element("nav")
        if el is not None and el.attributes.get("id") == "toc":
            return get_font(12, "bold", "roman").metrics("linespace")
        return 0

    # -- 자식 만들기: 11장 클래스로 ------------------------------------ #

    def layout(self):
        indent = self.list_indent()
        self.x = self.parent.x + indent
        css_width = parse_px(self.style_of("width", "auto"))
        self.width = css_width if css_width is not None \
            else self.parent.width - indent
        self.y = (self.previous.y + self.previous.height
                  if self.previous else self.parent.content_top())

        mode = self.layout_mode()
        if mode == "block":
            previous = None
            for group in group_children(self.node):
                child = BlockLayout(group, self, previous)
                self.children.append(child)
                previous = child
            for child in self.children:
                child.layout()
        else:
            self.centered = self.superscript = False
            self.smallcaps = self.pre = False
            self.new_line()
            for node in self.nodes:
                if self.skip_self and node is self.node \
                        and isinstance(node, Element):
                    for child in node.children:
                        self.recurse(child)
                else:
                    self.recurse(node)
            for line in self.children:
                line.layout()

        css_height = parse_px(self.style_of("height", "auto"))
        if css_height is not None:
            self.height = css_height
        else:
            self.height = self.toc_label_height() + \
                sum(c.height for c in self.children)

    def new_line(self):
        last = self.children[-1] if self.children else None
        self.children.append(
            LineLayout(self.node, self, last, centered=self.centered))
        self.cursor_x = 0

    def place(self, node, text, font, color, space=True):
        line = self.children[-1]
        previous = line.children[-1] if line.children else None
        word = TextLayout(node, text, line, previous, font, color,
                          self.superscript, space)
        line.children.append(word)
        self.cursor_x += font.measure(text) + (font.measure(" ") if space else 0)

    def input(self, node):
        font = self.font_for(node)
        if ex10.is_hidden(node):
            line = self.children[-1]
            previous = line.children[-1] if line.children else None
            line.children.append(InputLayout(node, line, previous, font))
            return
        width = CHECKBOX_SIZE \
            if ex10.input_type(node) == "checkbox" \
            else INPUT_WIDTH_PX
        if self.cursor_x + width > self.width:
            self.new_line()
        line = self.children[-1]
        previous = line.children[-1] if line.children else None
        line.children.append(InputLayout(node, line, previous, font))
        self.cursor_x += width + font.measure(" ")

    def button(self, node):
        font = self.font_for(node)
        if self.cursor_x > 0:
            self.new_line()
        line = self.children[-1]
        line.children.append(ButtonLayout(node, line, None, font))
        self.new_line()

    # -- 그리기 -------------------------------------------------------- #

    def should_paint(self):
        el = self.element()
        return el is None or el.tag not in ("input", "button")

    def paint(self):
        cmds = []
        el = self.element()
        if el is None:
            return cmds
        bg = el.style.get("background-color", "transparent")
        radius = border_radius(el)
        if bg != "transparent":
            if radius > 0:
                cmds.append(DrawRRect(self.self_rect(), radius, bg, el))
            else:
                cmds.append(DrawRect(self.self_rect(), bg, el))
        if el.tag == "nav" and el.attributes.get("class") == "links":
            cmds.append(DrawRect(self.self_rect(),
                                 LINKS_BAR_COLOR, el))
        if el.tag == "nav" and el.attributes.get("id") == "toc":
            font = get_font(12, "bold", "roman")
            h = font.metrics("linespace")
            cmds.append(DrawRect(
                Rect(self.x, self.y, self.x + self.width, self.y + h),
                TOC_COLOR, el))
            cmds.append(DrawText(self.x, self.y, TOC_LABEL,
                                 font, "black", el))
        if el.tag == "li":
            size = BULLET_SIZE
            indent = LIST_INDENT
            top = self.y + (VSTEP - size) // 2
            left = self.x - indent // 2
            cmds.append(DrawRect(Rect(left, top, left + size, top + size),
                                 "black", el))
        return cmds

    def paint_effects(self, cmds):
        el = self.element()
        if el is None:
            return cmds
        return paint_visual_effects(el, cmds, self.self_rect())


class DocumentLayout(ex10.DocumentLayout):
    def layout(self):
        self.width = WIDTH - 2 * HSTEP
        self.x, self.y = HSTEP, VSTEP
        child = BlockLayout([self.node], self, None)
        self.children.append(child)
        child.layout()
        self.height = child.height

    def should_paint(self):
        return True

    def paint(self):
        return []

    def paint_effects(self, cmds):
        return cmds


# ---------------------------------------------------------------------- #
# 히트 테스팅 (연습문제 11-2)
# ---------------------------------------------------------------------- #

def inside_rounded(rect, radius, x, y):
    """둥근 모서리 밖이면 False."""
    if not rect.contains_point(x, y):
        return False
    if radius <= 0:
        return True
    r = min(radius, (rect.right - rect.left) / 2, (rect.bottom - rect.top) / 2)
    for cx, cy in ((rect.left + r, rect.top + r),
                   (rect.right - r, rect.top + r),
                   (rect.left + r, rect.bottom - r),
                   (rect.right - r, rect.bottom - r)):
        # 그 모서리 구역 안쪽인가?
        in_x = (x < cx) if cx == rect.left + r else (x > cx)
        in_y = (y < cy) if cy == rect.top + r else (y > cy)
        if in_x and in_y:
            return math.hypot(x - cx, y - cy) <= r
    return True


def hit(cmd, x, y):
    """이 그리기 명령이 그 점을 실제로 덮는가."""
    node = cmd.node
    radius = 0.0
    if isinstance(cmd, DrawRRect):
        radius = cmd.radius
    elif node is not None and hasattr(node, "style"):
        radius = border_radius(node)
    return inside_rounded(cmd.rect, radius, x, y)


# ---------------------------------------------------------------------- #
# 탭
# ---------------------------------------------------------------------- #

class Tab(ex10.Tab):
    def __init__(self, tab_height):
        super().__init__(tab_height)
        self.scrollable_focus = None      # 연습문제 11-4

    def render(self):
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)
        self.flat_display_list = flatten(self.display_list)

    # -- 연습문제 11-3 -------------------------------------------------- #

    def raster(self, canvas, aoi_top=0):
        canvas.clear(skia.ColorWHITE)
        canvas.save()
        canvas.translate(0, -aoi_top)
        for cmd in self.display_list:
            if cmd.rect.top > aoi_top + AOI_HEIGHT:
                continue
            if cmd.rect.bottom < aoi_top:
                continue
            cmd.execute(canvas)
        canvas.restore()

    def draw(self, canvas, offset):        # 옛 이름은 쓰지 않는다
        self.raster(canvas)

    # -- 히트 테스팅 --------------------------------------------------- #

    def node_at(self, x, y):
        y += self.scroll
        for cmd in reversed(self.flat_display_list):
            if cmd.node is None:
                continue
            if isinstance(cmd, (Blend, Translate)):
                continue
            if hit(cmd, x, y):             # 연습문제 11-2
                return cmd.node
        return None

    def click(self, x, y):
        node = self.node_at(x, y)
        self.scrollable_focus = None
        walk = node
        while walk is not None:            # 연습문제 11-4
            if isinstance(walk, Element) and is_scrollable(walk):
                self.scrollable_focus = walk
                break
            walk = walk.parent
        return super().click(x, y)

    # -- 스크롤 -------------------------------------------------------- #

    def scroll_by(self, delta):
        """연습문제 11-4: 포커스된 스크롤 상자가 있으면 그것부터."""
        node = self.scrollable_focus
        if node is not None:
            height = parse_px_value(node.style.get("height", ""), 0)
            inner = content_height(self.document, node)
            top = getattr(node, "scroll_offset", 0)
            node.scroll_offset = max(0, min(top + delta, max(0, inner - height)))
            self.render()
            return True
        self.scroll = max(0, min(self.scroll + delta, self.max_scroll()))
        return False

    def scrolldown(self):
        self.scroll_by(SCROLL_STEP)

    def scrollup(self):
        self.scroll_by(-SCROLL_STEP)

    def max_scroll(self):
        return max(self.document.height + 2 * VSTEP - self.tab_height, 0)


def content_height(document, node):
    """그 요소 안쪽 내용의 실제 높이."""
    for obj in tree_to_list(document, []):
        if getattr(obj, "node", None) is node and isinstance(obj, BlockLayout):
            return sum(c.height for c in obj.children)
    return 0


def main(argv):
    from ex11_sdl import run
    run(argv[0] if argv else HOME_URL)


if __name__ == "__main__":
    main(sys.argv[1:])
