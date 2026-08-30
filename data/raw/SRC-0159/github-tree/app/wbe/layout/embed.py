"""줄 안에 놓이는 상자들 — 입력란, 버튼, 이미지, 캔버스, iframe.

모두 `EmbedLayout` 을 이어받아 `intrinsic_size()` 만 채운다. 줄은 이들을
글자와 똑같이 `ascent()`/`descent()` 로만 다룬다.
"""

import skia

from wbe.css.values import (parse_aspect_ratio, parse_px_value,
                            size_from_ratio)
from wbe.dom.nodes import Element
from wbe.layout.boxes import BlockLayout, LayoutObject
from wbe.paint.commands import (DrawImage, DrawLine, DrawOutline, DrawRect,
                                DrawText)
from wbe.paint.effects import border_radius, paint_visual_effects
from wbe.paint.geometry import Rect

INPUT_WIDTH_PX = 200
CHECKBOX_SIZE = 16
BUTTON_PADDING = 4
BUTTON_MAX_WIDTH = 300
IFRAME_WIDTH_PX = 300
IFRAME_HEIGHT_PX = 150
IMAGE_PLACEHOLDER_COLOR = "#dddddd"
PASSWORD_CHAR = "*"


# ---------------------------------------------------------------------- #
# 입력 요소 읽기
# ---------------------------------------------------------------------- #

def input_type(node):
    return node.attributes.get("type", "text").casefold()


def is_hidden(node):
    return input_type(node) == "hidden"


def is_checkbox(node):
    return input_type(node) == "checkbox"


def is_checked(node):
    return "checked" in node.attributes


def display_value(node):
    """화면에 보일 글자. 암호는 별표로 가린다.

    폼에 실리는 값은 `attributes["value"]` 원본 그대로다. 둘을 섞으면
    암호가 별표로 전송된다.
    """
    value = node.attributes.get("value", "")
    if input_type(node) == "password":
        return PASSWORD_CHAR * len(value)
    return value


def is_lazy(node):
    return node.attributes.get("loading", "").casefold() == "lazy"


def has_alt(node):
    return bool(node.attributes.get("alt", "").strip())


def should_hide_broken(node):
    """`alt` 가 없는 깨진 이미지는 읽어 줄 것도 보여 줄 것도 없다."""
    return not has_alt(node)


def attr_px(node, name):
    value = node.attributes.get(name)
    return parse_px_value(value, None) if value else None


def placeholder_size(node):
    """아직 로드되지 않은 이미지가 잡아 둘 자리.

    크기를 알 수 있으면 그만큼 잡아 두어야 늦게 도착해도 페이지가 덜
    출렁인다. 모르면 0×0 이다.
    """
    width = attr_px(node, "width")
    height = attr_px(node, "height")
    ratio = parse_aspect_ratio(node.style.get("aspect-ratio"))
    if width is None and height is None and ratio is None:
        return 0, 0
    return size_from_ratio(width, height, ratio, 0, 0)


def object_fit_rect(box, image_w, image_h, fit="fill"):
    """상자 안에서 이미지가 실제로 차지할 사각형."""
    if fit == "fill" or not image_w or not image_h \
            or box.width <= 0 or box.height <= 0:
        return box
    scale_w = box.width / image_w
    scale_h = box.height / image_h
    if fit == "contain":
        scale = min(scale_w, scale_h)
    elif fit == "cover":
        scale = max(scale_w, scale_h)
    elif fit == "none":
        scale = 1.0
    elif fit == "scale-down":
        scale = min(1.0, min(scale_w, scale_h))
    else:
        return box
    w, h = image_w * scale, image_h * scale
    left = box.left + (box.width - w) / 2
    top = box.top + (box.height - h) / 2
    return Rect(left, top, left + w, top + h)


def decode_image(data):
    """바이트를 이미지로. 못 읽으면 None."""
    if not data:
        return None
    try:
        return skia.Image.MakeFromEncoded(skia.Data.MakeWithCopy(data))
    except Exception:
        return None


# ---------------------------------------------------------------------- #
# 배치 객체
# ---------------------------------------------------------------------- #

class EmbedLayout(LayoutObject):
    def __init__(self, node, parent, previous, frame=None, font=None):
        super().__init__(node, parent, previous, frame)
        self.font = font
        self.space = True
        self.superscript = False

    def intrinsic_size(self):
        return 0, 0

    def layout(self):
        self.width, self.height = self.intrinsic_size()
        if self.previous:
            space = self.previous.font.measure(" ") \
                if self.previous.space and self.previous.font else 0
            self.x = self.previous.x + space + self.previous.width
        else:
            self.x = self.parent.x

    def ascent(self):
        return self.height

    def descent(self):
        return 0

    def paint_effects(self, cmds):
        return paint_visual_effects(self.node, cmds, self.self_rect())


class InputLayout(EmbedLayout):
    def is_hidden(self):
        return is_hidden(self.node)

    def intrinsic_size(self):
        if self.is_hidden():
            return 0, 0          # 자리를 차지하지 않는다
        if is_checkbox(self.node):
            return CHECKBOX_SIZE, CHECKBOX_SIZE
        return INPUT_WIDTH_PX, self.font.metrics("linespace")

    def ascent(self):
        return 0 if self.is_hidden() else self.height

    def should_paint(self):
        return not self.is_hidden()

    def paint(self):
        node = self.node
        if is_checkbox(node):
            return [
                DrawRect(self.self_rect(),
                         "black" if is_checked(node) else "white", node),
                DrawOutline(self.self_rect(), "black", 1, node),
            ]
        cmds = []
        bg = node.style.get("background-color", "transparent")
        if bg != "transparent":
            cmds.append(DrawRect(self.self_rect(), bg, node))
        text = display_value(node)
        if node.is_focused:
            cx = self.x + self.font.measure(text)
            cmds.append(DrawLine(cx, self.y, cx, self.y + self.height,
                                 "black", 1, node))
        if text:
            cmds.append(DrawText(self.x, self.y, text, self.font,
                                 node.style["color"], node))
        return cmds

    def __repr__(self):
        return "InputLayout(%s)" % input_type(self.node)


class _Box:
    """버튼 안쪽 배치를 위한 가짜 부모."""

    def __init__(self, width):
        self.x, self.y, self.width = 0, 0, width

    def content_top(self):
        return self.y


class ButtonLayout(EmbedLayout):
    """버튼 안에 아무 요소나 담는다.

    줄 안에 놓이지만 안쪽은 제 나름의 블록 배치를 갖는다. 자식들은 버튼 폭
    안에서만 흐르므로 밖으로 새지 않는다.
    """

    def layout(self):
        avail = max(40, min(BUTTON_MAX_WIDTH, self.parent.width)
                    - 2 * BUTTON_PADDING)
        self.width = avail + 2 * BUTTON_PADDING
        if self.previous:
            space = self.previous.font.measure(" ") \
                if self.previous.space and self.previous.font else 0
            self.x = self.previous.x + space + self.previous.width
        else:
            self.x = self.parent.x
        self.inner = BlockLayout([self.node], _Box(avail), None, self.frame,
                                 skip_self=True)
        self.inner.layout()
        self.height = self.inner.height + 2 * BUTTON_PADDING

    def place(self, y):
        """줄이 정해 준 y 로 안쪽까지 옮긴다."""
        self.y = y
        dx = self.x + BUTTON_PADDING - self.inner.x
        dy = self.y + BUTTON_PADDING - self.inner.y
        from wbe.dom.nodes import tree_to_list
        for obj in _layout_tree(self.inner):
            if obj.x is not None:
                obj.x += dx
            if obj.y is not None:
                obj.y += dy

    def paint(self):
        from wbe.paint.commands import DrawRRect
        from wbe.paint.effects import paint_tree
        cmds = []
        bg = self.node.style.get("background-color", "transparent")
        radius = border_radius(self.node)
        if bg != "transparent":
            cmds.append(DrawRRect(self.self_rect(), radius, bg, self.node)
                        if radius > 0
                        else DrawRect(self.self_rect(), bg, self.node))
        cmds.append(DrawOutline(self.self_rect(), "black", 1, self.node))
        paint_tree(self.inner, cmds)
        return cmds

    def paint_effects(self, cmds):
        return cmds

    def __repr__(self):
        return "ButtonLayout(%gx%g)" % (self.width or 0, self.height or 0)


def _layout_tree(obj, out=None):
    out = [] if out is None else out
    out.append(obj)
    for child in obj.children:
        _layout_tree(child, out)
    if getattr(obj, "inner", None) is not None:
        _layout_tree(obj.inner, out)
    return out


class ImageLayout(EmbedLayout):
    def intrinsic_size(self):
        node = self.node
        image = node.image
        ratio = parse_aspect_ratio(node.style.get("aspect-ratio"))
        width = attr_px(node, "width")
        height = attr_px(node, "height")
        if image is None:
            if ratio is None and (width is not None or height is not None):
                return width or 0, height or 0
            return placeholder_size(node)
        if ratio is None:
            ratio = image.width() / image.height() if image.height() else None
        return size_from_ratio(width, height, ratio,
                               image.width(), image.height())

    def paint(self):
        node = self.node
        rect = self.self_rect()
        if node.image is None:
            if should_hide_broken(node):
                return []
            if self.width <= 0 or self.height <= 0:
                return []
            cmds = [DrawRect(rect, IMAGE_PLACEHOLDER_COLOR, node)]
            alt = node.attributes.get("alt", "")
            if alt and self.font is not None:
                cmds.append(DrawText(rect.left, rect.top, alt, self.font,
                                     "black", node))
            return cmds
        fit = node.style.get("object-fit", "fill")
        drawn = object_fit_rect(rect, node.image.width(), node.image.height(),
                                fit)
        return [DrawImage(node.image, drawn,
                          node.style.get("image-rendering", "auto"), node)]

    def __repr__(self):
        return "ImageLayout(%s)" % self.node.attributes.get("src", "")


class CanvasContext:
    """캔버스 2D 문맥.

    그리기 명령을 모아 두었다가 페인트 때 되돌려 준다.
    """

    def __init__(self, node):
        self.node = node
        self.commands = []
        self.fill_style = "black"

    def clear(self):
        self.commands = []

    def setFillStyle(self, color):
        self.fill_style = color

    def fillRect(self, x, y, w, h):
        self.commands.append(("rect", float(x), float(y), float(w), float(h),
                              self.fill_style))

    def fillText(self, text, x, y):
        self.commands.append(("text", str(text), float(x), float(y),
                              self.fill_style))

    def replay(self, rect, font):
        out = []
        for cmd in self.commands:
            if cmd[0] == "rect":
                _, x, y, w, h, color = cmd
                out.append(DrawRect(
                    Rect(rect.left + x, rect.top + y,
                         rect.left + x + w, rect.top + y + h),
                    color, self.node))
            elif font is not None:
                _, text, x, y, color = cmd
                out.append(DrawText(rect.left + x, rect.top + y, text, font,
                                    color, self.node))
        return out


class CanvasLayout(EmbedLayout):
    DEFAULT_WIDTH = 300
    DEFAULT_HEIGHT = 150

    def intrinsic_size(self):
        width = attr_px(self.node, "width")
        height = attr_px(self.node, "height")
        return (width if width is not None else self.DEFAULT_WIDTH,
                height if height is not None else self.DEFAULT_HEIGHT)

    def paint(self):
        rect = self.self_rect()
        cmds = [DrawRect(rect, "white", self.node)]
        context = self.node.canvas_context
        if context is not None:
            cmds.extend(context.replay(rect, self.font))
        return cmds

    def __repr__(self):
        return "CanvasLayout(%gx%g)" % (self.width or 0, self.height or 0)


class IframeLayout(EmbedLayout):
    def intrinsic_size(self):
        node = self.node
        ratio = parse_aspect_ratio(node.style.get("aspect-ratio"))
        return size_from_ratio(attr_px(node, "width"), attr_px(node, "height"),
                               ratio, IFRAME_WIDTH_PX, IFRAME_HEIGHT_PX)

    def layout(self):
        super().layout()
        frame = self.node.frame
        if frame is not None:
            frame.width = self.width
            frame.height = self.height
            frame.layout()

    def paint(self):
        from wbe.paint.commands import Transform
        cmds = [DrawRect(self.self_rect(), "white", self.node),
                DrawOutline(self.self_rect(), "black", 1, self.node)]
        frame = self.node.frame
        if frame is not None and frame.display_list:
            cmds.append(Transform((self.x, self.y - frame.scroll),
                                  list(frame.display_list), self.node))
        return cmds

    def __repr__(self):
        return "IframeLayout(%s)" % self.node.attributes.get("src", "")
