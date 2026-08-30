"""15장 연습문제 구현 (15-1 ~ 15-12).

lab15.py 는 그대로 두고, 1~14장 연습문제를 이어받아 그 위에 15장 기능을 얹는다.
자바스크립트 쪽은 runtime15ex.js, 창은 ex15_sdl.py 에 있다.

15장 본문 기능(이미지, iframe, 프레임, postMessage)에 더해

    15-1  canvas 요소
    15-2  배경 이미지            background-image: url(...)
    15-3  object-fit           contain / cover / fill
    15-4  지연 로딩             loading=lazy
    15-5  iframe 종횡비         aspect-ratio
    15-6  이미지 자리 표시자
    15-7  미디어 쿼리           width, iframe 안에서도
    15-8  postMessage 의 대상 출처
    15-9  다중 프레임 포커스
    15-10 iframe 방문 기록
    15-11 스크립트가 추가하거나 제거한 iframe
    15-12 X-Frame-Options
"""

import base64
import os
import sys
import urllib.parse

import skia

import ex10
import ex11
import ex12
import ex13
import ex14
from ex4 import Text, Element
from ex8 import History
from ex9 import HTMLParser
import ex6
from ex6 import tree_to_list
from ex11 import (Rect, DrawText, DrawRect, DrawRRect, DrawOutline, DrawLine,
                  parse_px_value, WIDTH, HEIGHT, HSTEP, VSTEP)
from ex13 import Transform, Blend
from ex14 import (CSSParser, BROWSER_CSS_14, is_focusable, focusable_nodes,
                  get_tabindex, media_matches, effective_zoom, dpx,
                  RecordingSpeaker, PrintSpeaker)

HERE = os.path.dirname(os.path.abspath(__file__))

IFRAME_WIDTH_PX = 300
IFRAME_HEIGHT_PX = 150
IMAGE_PLACEHOLDER_COLOR = "#dddddd"      # 연습문제 15-6
NAV_SERIAL = 0                           # 연습문제 15-10: 이동 순서

BROWSER_CSS_15 = BROWSER_CSS_14 + """
iframe { display: block; }
img { display: inline; }
canvas { display: inline; }
"""


# ---------------------------------------------------------------------- #
# 이미지
# ---------------------------------------------------------------------- #

def parse_image_rendering(quality):
    if quality == "crisp-edges":
        return skia.FilterMode.kNearest
    return skia.FilterMode.kLinear


def decode_image(data):
    """바이트를 skia.Image 로. 못 읽으면 None."""
    if not data:
        return None
    try:
        return skia.Image.MakeFromEncoded(skia.Data.MakeWithCopy(data))
    except Exception:
        return None


def request_bytes(url):
    """이미지처럼 글자가 아닌 것을 받아 온다."""
    if url.scheme == "data":
        mediatype, _, _ = str(url).partition(",")
        raw = url.data
        if mediatype.casefold().endswith(";base64"):
            return base64.b64decode(raw)
        return urllib.parse.unquote_to_bytes(raw)
    if url.scheme == "file":
        with open(url.path, "rb") as f:
            return f.read()
    text = url.request(referrer=None)
    return text.encode("utf8", "surrogateescape")


class DrawImage:
    def __init__(self, image, rect, quality="auto", node=None):
        self.image = image
        self.rect = rect
        self.quality = parse_image_rendering(quality)
        self.node = node
        self.children = []

    def execute(self, canvas):
        if self.image is None:
            return
        canvas.drawImageRect(
            self.image,
            skia.Rect.MakeWH(self.image.width(), self.image.height()),
            ex11.skia_rect(self.rect),
            skia.SamplingOptions(self.quality))

    def __repr__(self):
        return "DrawImage(%s)" % (self.rect,)


# ---------------------------------------------------------------------- #
# 연습문제 15-3: object-fit
# ---------------------------------------------------------------------- #

def object_fit_rect(box, image_w, image_h, fit="fill"):
    """상자 안에서 이미지가 실제로 차지할 사각형."""
    box_w = box.right - box.left
    box_h = box.bottom - box.top
    if fit == "fill" or not image_w or not image_h or box_w <= 0 or box_h <= 0:
        return box
    scale_w = box_w / image_w
    scale_h = box_h / image_h
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
    left = box.left + (box_w - w) / 2
    top = box.top + (box_h - h) / 2
    return Rect(left, top, left + w, top + h)


# ---------------------------------------------------------------------- #
# 연습문제 15-2: background-image
# ---------------------------------------------------------------------- #

class CSSParser15(CSSParser):
    """괄호 안의 세미콜론을 값의 끝으로 보지 않는다.

    15-2 의 background-image: url(data:image/png;base64,...) 가 그 예다.
    CSS 는 url(...) 을 토큰 하나로 보므로 괄호 깊이를 세야 한다.
    """

    def value(self):
        start, depth = self.i, 0
        while self.i < len(self.s):
            c = self.s[self.i]
            if c == "(":
                depth += 1
            elif c == ")":
                depth = max(0, depth - 1)
            elif c in ";}" and depth == 0:
                break
            self.i += 1
        return self.s[start:self.i].strip()


def resolve(base, href):
    """상대 주소를 푼다.

    8장의 resolve 는 결과를 str() 로 한 번 거치는데, data: URL 의 __repr__ 는
    내용을 '...' 로 줄여 버린다. 지금까지는 data: 를 상대 주소로 풀 일이
    없어 드러나지 않았지만, 이미지와 iframe 이 들어오는 15장에서는 곧바로
    문제가 된다. 절대 주소는 원문 그대로 새로 만든다.
    """
    if href.startswith(("data:", "about:", "view-source:")) or "://" in href:
        return ex10.URL(href)
    return base.resolve(href)


def install_css():
    """인라인 style="..." 도 괄호를 아는 파서로 읽게 한다."""
    ex6.CSSParser.value = CSSParser15.value


install_css()


def origin_of(url):
    """data:/about: 처럼 호스트가 없는 URL 은 불투명 출처다."""
    if url is None:
        return None
    if getattr(url, "host", None) is None:
        return "null"
    return url.origin()


def parse_url_value(value):
    """'url(cat.png)' 또는 'url("cat.png")' -> 'cat.png'"""
    if not value:
        return None
    value = value.strip()
    if not value.casefold().startswith("url(") or not value.endswith(")"):
        return None
    inner = value[4:-1].strip()
    if len(inner) >= 2 and inner[0] == inner[-1] and inner[0] in "\"'":
        inner = inner[1:-1]
    return inner or None


# ---------------------------------------------------------------------- #
# 연습문제 15-5: aspect-ratio
# ---------------------------------------------------------------------- #

def parse_aspect_ratio(value):
    """'16 / 9' 또는 '1.5' -> 비율. 없으면 None."""
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
    """하나만 주어졌으면 비율로 나머지를 채운다."""
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


# ---------------------------------------------------------------------- #
# 연습문제 15-4 / 15-6: 지연 로딩과 자리 표시자
# ---------------------------------------------------------------------- #

def is_lazy(node):
    return node.attributes.get("loading", "").casefold() == "lazy"


def has_alt(node):
    return bool(node.attributes.get("alt", "").strip())


def placeholder_size(node):
    """아직 로드되지 않은 이미지의 크기 (연습문제 15-6)."""
    width = parse_px_value(node.attributes.get("width", ""), None) \
        if node.attributes.get("width") else None
    height = parse_px_value(node.attributes.get("height", ""), None) \
        if node.attributes.get("height") else None
    ratio = parse_aspect_ratio(node.style.get("aspect-ratio"))
    if width is None and height is None and ratio is None:
        return 0, 0            # 크기를 모르면 자리를 차지하지 않는다
    return size_from_ratio(width, height, ratio, 0, 0)


def should_hide_broken(node):
    """alt 가 없으면 깨진 이미지를 숨긴다 (연습문제 15-6)."""
    return not has_alt(node)


# ---------------------------------------------------------------------- #
# 연습문제 15-12: X-Frame-Options
# ---------------------------------------------------------------------- #

def frame_allowed(headers, parent_origin, target_origin):
    """이 응답을 iframe 안에 넣어도 되는가."""
    value = (headers or {}).get("x-frame-options", "").strip().casefold()
    if not value:
        return True
    if value == "deny":
        return False
    if value == "sameorigin":
        return parent_origin == target_origin
    return True


# ---------------------------------------------------------------------- #
# 배치 — 끼워 넣는 것들
# ---------------------------------------------------------------------- #

class EmbedLayout:
    """줄 안에 놓이는 상자 하나. 이미지·iframe·canvas 의 공통 뼈대."""

    def __init__(self, node, parent, previous, frame=None, font=None):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.frame = frame
        self.children = []
        self.font = font
        self.space = True
        self.superscript = False
        self.x = self.y = self.width = self.height = None

    def layout(self):
        self.width, self.height = self.intrinsic_size()
        if self.previous:
            space = self.previous.font.measure(" ") \
                if self.previous.space and self.previous.font else 0
            self.x = self.previous.x + space + self.previous.width
        else:
            self.x = self.parent.x

    def intrinsic_size(self):
        return 0, 0

    def ascent(self):
        return self.height

    def descent(self):
        return 0

    def should_paint(self):
        return True

    def self_rect(self):
        return Rect(self.x, self.y, self.x + self.width, self.y + self.height)

    def paint(self):
        return []

    def paint_effects(self, cmds):
        return ex13.paint_visual_effects(self.node, cmds, self.self_rect())


class ImageLayout(EmbedLayout):
    def intrinsic_size(self):
        node = self.node
        image = getattr(node, "image", None)
        ratio = parse_aspect_ratio(node.style.get("aspect-ratio"))
        width = parse_px_value(node.attributes.get("width", ""), None) \
            if node.attributes.get("width") else None
        height = parse_px_value(node.attributes.get("height", ""), None) \
            if node.attributes.get("height") else None
        if image is None:
            if ratio is None and (width is not None or height is not None):
                return size_from_ratio(width, height, None, width or 0,
                                       height or 0)
            return placeholder_size(node)      # 15-4 / 15-6
        if ratio is None:
            ratio = image.width() / image.height() if image.height() else None
        return size_from_ratio(width, height, ratio,
                               image.width(), image.height())

    def paint(self):
        node = self.node
        image = getattr(node, "image", None)
        rect = self.self_rect()
        if image is None:
            if should_hide_broken(node):       # 15-6
                return []
            if self.width <= 0 or self.height <= 0:
                return []
            cmds = [DrawRect(rect, IMAGE_PLACEHOLDER_COLOR, node)]
            alt = node.attributes.get("alt", "")
            if alt and self.font is not None:
                cmds.append(DrawText(rect.left, rect.top, alt, self.font,
                                     "black", node))
            return cmds
        fit = node.style.get("object-fit", "fill")          # 15-3
        drawn = object_fit_rect(rect, image.width(), image.height(), fit)
        return [DrawImage(image, drawn,
                          node.style.get("image-rendering", "auto"), node)]

    def __repr__(self):
        return "ImageLayout(%s)" % self.node.attributes.get("src", "")


class CanvasLayout(EmbedLayout):
    """연습문제 15-1."""

    DEFAULT_WIDTH = 300
    DEFAULT_HEIGHT = 150

    def intrinsic_size(self):
        node = self.node
        width = parse_px_value(node.attributes.get("width", ""),
                               self.DEFAULT_WIDTH) \
            if node.attributes.get("width") else self.DEFAULT_WIDTH
        height = parse_px_value(node.attributes.get("height", ""),
                                self.DEFAULT_HEIGHT) \
            if node.attributes.get("height") else self.DEFAULT_HEIGHT
        return width, height

    def paint(self):
        context = getattr(self.node, "canvas_context", None)
        rect = self.self_rect()
        cmds = [DrawRect(rect, "white", self.node)]
        if context is not None:
            cmds.extend(context.replay(rect, self.font))
        return cmds

    def __repr__(self):
        return "CanvasLayout(%gx%g)" % (self.width or 0, self.height or 0)


class IframeLayout(EmbedLayout):
    def intrinsic_size(self):
        node = self.node
        ratio = parse_aspect_ratio(node.style.get("aspect-ratio"))    # 15-5
        width = parse_px_value(node.attributes.get("width", ""), None) \
            if node.attributes.get("width") else None
        height = parse_px_value(node.attributes.get("height", ""), None) \
            if node.attributes.get("height") else None
        return size_from_ratio(width, height, ratio,
                               IFRAME_WIDTH_PX, IFRAME_HEIGHT_PX)

    def layout(self):
        super().layout()
        frame = getattr(self.node, "frame", None)
        if frame is not None:
            frame.width = self.width
            frame.height = self.height
            frame.layout()

    def paint(self):
        cmds = [DrawRect(self.self_rect(), "white", self.node),
                DrawOutline(self.self_rect(), "black", 1, self.node)]
        frame = getattr(self.node, "frame", None)
        if frame is not None and frame.display_list:
            cmds.append(Transform((self.x, self.y - frame.scroll),
                                  list(frame.display_list), self.node))
        return cmds

    def __repr__(self):
        return "IframeLayout(%s)" % self.node.attributes.get("src", "")


# ---------------------------------------------------------------------- #
# 배치 트리에 끼워 넣기
# ---------------------------------------------------------------------- #

class BlockLayout(ex11.BlockLayout):
    def __init__(self, nodes, parent, previous, skip_self=False, frame=None):
        super().__init__(nodes, parent, previous, skip_self)
        self.frame = frame

    def layout(self):
        indent = self.list_indent()
        self.x = self.parent.x + indent
        css_width = ex11.parse_px(self.style_of("width", "auto"))
        self.width = css_width if css_width is not None \
            else self.parent.width - indent
        self.y = (self.previous.y + self.previous.height
                  if self.previous else self.parent.content_top())

        mode = self.layout_mode()
        if mode == "block":
            previous = None
            for group in ex11.group_children(self.node):
                child = BlockLayout(group, self, previous, frame=self.frame)
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

        css_height = ex11.parse_px(self.style_of("height", "auto"))
        if css_height is not None:
            self.height = css_height
        else:
            self.height = self.toc_label_height() + \
                sum(c.height for c in self.children)

    def layout_mode(self):
        if any(isinstance(n, Text) for n in self.nodes):
            return "inline"
        if len(self.nodes) > 1:
            return "inline"
        if any(ex6.is_block(c) for c in self.node.children):
            return "block"
        if self.node.tag in ("input", "button", "img", "canvas", "iframe"):
            return "inline"
        return "inline" if self.node.children else "block"

    def recurse(self, node):
        if isinstance(node, Text):
            if self.pre:
                self.pre_text(node)
            else:
                for word in node.text.split():
                    self.word(node, word)
        elif node.tag == "input":
            self.input(node)
        elif node.tag == "button":
            self.button(node)
        elif node.tag == "img":
            self.embed(node, ImageLayout)
        elif node.tag == "canvas":
            self.embed(node, CanvasLayout)
        elif node.tag == "iframe":
            self.embed(node, IframeLayout)
        else:
            self.open_tag(node)
            for child in node.children:
                self.recurse(child)
            self.close_tag(node)

    def embed(self, node, cls):
        font = self.font_for(node)
        obj = cls(node, None, None, self.frame, font)
        probe_width, _ = obj.intrinsic_size()
        if probe_width and self.cursor_x + probe_width > self.width:
            self.new_line()
        line = self.children[-1]
        previous = line.children[-1] if line.children else None
        obj.parent = line
        obj.previous = previous
        line.children.append(obj)
        self.cursor_x += probe_width + font.measure(" ")

    def paint(self):
        cmds = super().paint()
        el = self.element()
        if el is None:
            return cmds
        # 연습문제 15-2: 배경 이미지는 배경색 위에
        image = getattr(el, "background_image", None)
        if image is not None:
            cmds.insert(0, DrawImage(image, self.self_rect(),
                                     el.style.get("image-rendering", "auto"),
                                     el))
        return cmds

    def should_paint(self):
        el = self.element()
        return el is None or el.tag not in ("input", "button", "img",
                                            "canvas", "iframe")


class DocumentLayout(ex11.DocumentLayout):
    def __init__(self, node, frame=None):
        super().__init__(node)
        self.frame = frame

    def layout(self, width=None):
        self.width = (width if width is not None else WIDTH) - 2 * HSTEP
        self.x, self.y = HSTEP, VSTEP
        child = BlockLayout([self.node], self, None, frame=self.frame)
        self.children = [child]
        child.layout()
        self.height = child.height


# ---------------------------------------------------------------------- #
# 연습문제 15-1: 캔버스 2D 문맥
# ---------------------------------------------------------------------- #

class CanvasContext:
    """그리기 명령을 모아 두었다가 페인트 때 되돌려 준다."""

    def __init__(self, node):
        self.node = node
        self.commands = []
        self.fill_style = "black"

    def clear(self):
        self.commands = []

    def fillRect(self, x, y, w, h):
        self.commands.append(("rect", float(x), float(y), float(w), float(h),
                              self.fill_style))

    def fillText(self, text, x, y):
        self.commands.append(("text", str(text), float(x), float(y),
                              self.fill_style))

    def setFillStyle(self, color):
        self.fill_style = color

    def replay(self, rect, font):
        out = []
        for cmd in self.commands:
            if cmd[0] == "rect":
                _, x, y, w, h, color = cmd
                out.append(DrawRect(
                    Rect(rect.left + x, rect.top + y,
                         rect.left + x + w, rect.top + y + h),
                    color, self.node))
            else:
                _, text, x, y, color = cmd
                if font is not None:
                    out.append(DrawText(rect.left + x, rect.top + y, text,
                                        font, color, self.node))
        return out


# ---------------------------------------------------------------------- #
# 프레임
# ---------------------------------------------------------------------- #

class Frame:
    """문서 하나. 최상위 문서도, iframe 안의 문서도 이것이다."""

    def __init__(self, tab, parent_frame=None, frame_element=None):
        self.tab = tab
        self.parent_frame = parent_frame
        self.frame_element = frame_element
        self.url = None
        self.nodes = None
        self.js = None
        self.document = None
        self.display_list = []
        self.scroll = 0
        self.focus = None
        self.tab_focus = None
        self.width = WIDTH
        self.height = HEIGHT
        self.base_rules = []
        self.link_rules = {}
        self.link_bodies = {}
        self.keyframes = {}
        self.history = History()                    # 연습문제 15-10
        self.children = []
        self.blocked = False                        # 연습문제 15-12

    # -- 읽기 ---------------------------------------------------------- #

    def origin(self):
        return origin_of(self.url)

    def load(self, url, payload=None, record=True):
        parent_origin = self.parent_frame.origin() if self.parent_frame \
            else None
        body = url.request(referrer=self.url, payload=payload)
        headers = getattr(url, "response_headers", {}) or {}
        if self.parent_frame is not None and \
                not frame_allowed(headers, parent_origin, origin_of(url)):
            self.blocked = True                     # 연습문제 15-12
            body = "<html><body><p>이 페이지는 프레임 안에 넣을 수 없습니다</p>" \
                   "</body></html>"
        else:
            self.blocked = False

        self.url = url
        if record:
            self.history.visit(url)
            global NAV_SERIAL
            NAV_SERIAL += 1
            self.nav_serial = NAV_SERIAL
        self.nodes = HTMLParser(body).parse()
        for node in tree_to_list(self.nodes, []):
            if isinstance(node, Element):
                node.is_focused = node.is_hovered = node.focus_visible = False

        self.keyframes = {}
        for node in tree_to_list(self.nodes, []):
            if isinstance(node, Element) and node.tag == "style":
                text = "".join(c.text for c in node.children
                               if isinstance(c, Text))
                self.keyframes.update(ex13.parse_keyframes(text))

        self.js = self.tab.make_js(self)
        self.load_embeds()
        self.rebuild_rules()
        self.restyle()
        self.js.update_id_globals()
        for node in tree_to_list(self.nodes, []):
            if isinstance(node, Element) and node.tag == "script":
                self.run_script(node)
        self.layout()

    def run_script(self, node):
        code = "".join(c.text for c in node.children if isinstance(c, Text))
        src = node.attributes.get("src")
        if src:
            try:
                code = ex15_request_text(resolve(self.url, src))
            except Exception:
                return
        if code.strip():
            self.js.run(src or "인라인 스크립트", code)

    # -- 자원 ---------------------------------------------------------- #

    def load_embeds(self):
        for node in tree_to_list(self.nodes, []):
            if not isinstance(node, Element):
                continue
            if node.tag == "img":
                self.load_image(node)
            elif node.tag == "canvas":
                node.canvas_context = CanvasContext(node)
            elif node.tag == "iframe":
                self.load_iframe(node)

    def load_image(self, node, force=False):
        node.image = None
        if is_lazy(node) and not force:          # 연습문제 15-4
            node.image_pending = True
            return
        node.image_pending = False
        src = node.attributes.get("src")
        if not src:
            return
        try:
            node.image = decode_image(request_bytes(resolve(self.url, src)))
        except Exception:
            node.image = None

    def load_background(self, node):
        """연습문제 15-2."""
        node.background_image = None
        src = parse_url_value(node.style.get("background-image"))
        if not src:
            return
        try:
            node.background_image = decode_image(
                request_bytes(resolve(self.url, src)))
        except Exception:
            node.background_image = None

    def load_iframe(self, node):
        src = node.attributes.get("src")
        if not src:
            node.frame = None
            return
        child = Frame(self.tab, self, node)
        node.frame = child
        self.children.append(child)
        try:
            child.load(resolve(self.url, src))
        except Exception:
            node.frame = None
            if child in self.children:
                self.children.remove(child)

    def unload_iframe(self, node):
        """연습문제 15-11."""
        child = getattr(node, "frame", None)
        if child is None:
            return
        if child in self.children:
            self.children.remove(child)
        if child.js is not None:
            child.js.discarded = True
        node.frame = None

    # -- 스타일과 배치 -------------------------------------------------- #

    def media(self):
        return {
            "prefers-color-scheme":
                "dark" if self.tab and self.tab.dark_mode else "light",
            "forced-colors": bool(self.tab and self.tab.forced_colors),
            "width": self.width / (self.tab.zoom if self.tab else 1.0),
        }

    def sheet_texts(self):
        texts = [BROWSER_CSS_15]
        for node in tree_to_list(self.nodes, []):
            if isinstance(node, Element) and node.tag == "style":
                texts.append("".join(c.text for c in node.children
                                     if isinstance(c, Text)))
        return texts

    def rebuild_rules(self):
        media = self.media()
        self.base_rules = []
        for text in self.sheet_texts():
            self.base_rules.extend(CSSParser15(text, media).parse())
        for node, body in self.link_bodies.items():
            self.link_rules[node] = CSSParser15(body, media).parse()

    def all_rules(self):
        rules = list(self.base_rules)
        for extra in self.link_rules.values():
            rules.extend(extra)
        return sorted(rules, key=ex10.cascade_priority)

    def restyle(self):
        self.rebuild_rules()
        ex13.style(self.nodes, self.all_rules(), self.tab, self.keyframes)
        if self.tab is not None and self.tab.forced_colors:
            ex14.force_colors(tree_to_list(self.nodes, []))
        for node in tree_to_list(self.nodes, []):       # 15-2
            if isinstance(node, Element) \
                    and node.style.get("background-image"):
                self.load_background(node)

    def layout(self):
        if self.nodes is None:
            return
        if getattr(self, "styled_width", None) != self.width:
            self.restyle()                 # 너비가 바뀌면 미디어 쿼리도 바뀐다
            self.styled_width = self.width
        self.document = DocumentLayout(self.nodes, self)
        self.document.layout(self.width)
        self.display_list = []
        ex13.paint_tree(self.document, self.display_list)

    def all_frames(self, out=None):
        out = [] if out is None else out
        out.append(self)
        for child in self.children:
            child.all_frames(out)
        return out

    # -- 포커스 (연습문제 15-9) ----------------------------------------- #

    def focusable(self):
        return focusable_nodes(tree_to_list(self.nodes, []))

    def __repr__(self):
        return "Frame(%s)" % self.url


def ex15_request_text(url):
    return url.request(referrer=None)


# ---------------------------------------------------------------------- #
# 자바스크립트 — 캔버스, postMessage, iframe 붙이고 떼기
# ---------------------------------------------------------------------- #

RUNTIME_JS = open(os.path.join(HERE, "runtime15ex.js"), encoding="utf8").read()


class JSContext(ex14.JSContext):
    """프레임 하나에 하나씩."""

    RUNTIME = RUNTIME_JS

    def __init__(self, frame):
        self.frame = frame
        super().__init__(frame.tab)
        self.tab = frame.tab
        for name in ("canvas_fill_rect", "canvas_fill_text",
                     "canvas_fill_style", "canvas_clear", "post_message"):
            self.interp.export_function(name, getattr(self, name))

    # 이 문맥이 다루는 트리는 프레임의 것이다
    @property
    def nodes(self):
        return self.frame.nodes

    def querySelectorAll(self, selector_text):
        selector = ex14.CSSParser(selector_text).selector()
        if hasattr(selector, "prepare"):
            selector.prepare(self.frame.nodes)
        return [self.get_handle(node)
                for node in tree_to_list(self.frame.nodes, [])
                if selector.matches(node)]

    def update_id_globals(self):
        current = {}
        for node in tree_to_list(self.frame.nodes, []):
            if not isinstance(node, Element):
                continue
            name = node.attributes.get("id")
            if name and self.usable_id(name) and name not in current:
                current[name] = self.get_handle(node)
        for name in list(self.id_globals):
            if name not in current:
                self.interp.evaljs("delete this[dukpy.name];", name=name)
                del self.id_globals[name]
        for name, handle in current.items():
            if self.id_globals.get(name) != handle:
                self.interp.evaljs(
                    "this[dukpy.name] = new Node(dukpy.handle);",
                    name=name, handle=handle)
                self.id_globals[name] = handle

    def changed(self):
        self.update_id_globals()
        self.frame.restyle()
        self.frame.layout()
        if self.tab is not None:
            self.tab.set_needs_paint()

    # -- 연습문제 15-1 -------------------------------------------------- #

    def context_of(self, handle):
        node = self.node(handle)
        if not hasattr(node, "canvas_context") or node.canvas_context is None:
            node.canvas_context = CanvasContext(node)
        return node.canvas_context

    def canvas_fill_style(self, handle, color):
        self.context_of(handle).setFillStyle(color)
        return color

    def canvas_fill_rect(self, handle, x, y, w, h):
        self.context_of(handle).fillRect(x, y, w, h)
        self.changed()
        return None

    def canvas_fill_text(self, handle, text, x, y):
        self.context_of(handle).fillText(text, x, y)
        self.changed()
        return None

    def canvas_clear(self, handle):
        self.context_of(handle).clear()
        self.changed()
        return None

    # -- 15장 본문 + 연습문제 15-8 -------------------------------------- #

    def post_message(self, message, target_origin="*"):
        parent = self.frame.parent_frame
        if parent is None or parent.js is None:
            return 0
        if not origin_matches(target_origin, parent.origin()):
            return 0                       # 연습문제 15-8
        return parent.js.deliver_message(message, self.frame.origin())

    def deliver_message(self, message, origin):
        return self.interp.evaljs(
            "__runWindowMessage(dukpy.data, dukpy.origin)",
            data=message, origin=origin or "")

    # -- 연습문제 15-11 ------------------------------------------------- #

    def attach_resources(self, subtree):
        for node in tree_to_list(subtree, []):
            if not isinstance(node, Element):
                continue
            if node.tag == "script":
                self.frame.run_script(node)
            elif node.tag == "link" and "href" in node.attributes \
                    and node.attributes.get("rel") == "stylesheet":
                pass
            elif node.tag == "iframe":
                self.frame.load_iframe(node)
            elif node.tag == "img":
                self.frame.load_image(node)
            elif node.tag == "canvas":
                node.canvas_context = CanvasContext(node)

    def detach_resources(self, subtree):
        for node in tree_to_list(subtree, []):
            if isinstance(node, Element) and node.tag == "iframe":
                self.frame.unload_iframe(node)


# ---------------------------------------------------------------------- #
# 탭
# ---------------------------------------------------------------------- #

class Tab(ex14.Tab):
    def __init__(self, browser, tab_height, **kwargs):
        super().__init__(browser, tab_height, **kwargs)
        self.root_frame = None
        self.focused_frame = None
        self.tab_order_focus = None

    def make_js(self, frame):
        return JSContext(frame)

    def load(self, url, payload=None, record=True):
        self.root_frame = Frame(self, None, None)
        self.root_frame.width = ex11.WIDTH
        self.root_frame.height = self.tab_height
        self.root_frame.load(url, payload, record)
        self.url = url
        self.focused_frame = self.root_frame
        self.js = self.root_frame.js
        self.nodes = self.root_frame.nodes
        self.render()

    def render(self):
        if self.root_frame is None:
            return False
        self.root_frame.layout()
        self.document = self.root_frame.document
        self.display_list = list(self.root_frame.display_list)
        self.flat_display_list = ex11.flatten(self.display_list)
        self.needs_render = self.needs_layout = self.needs_paint = False
        return True

    def force_render(self):
        return self.render()

    def frames(self):
        return self.root_frame.all_frames() if self.root_frame else []

    # -- 연습문제 15-9 -------------------------------------------------- #

    def advance_tab(self):
        order = frame_tab_order(self.root_frame)
        nxt = next_focus(order, self.tab_order_focus)
        if nxt is None:
            return None
        self.tab_order_focus = nxt
        frame, node = nxt
        for other in self.frames():
            if other.tab_focus is not None and other is not frame:
                other.tab_focus.is_focused = False
                other.tab_focus.focus_visible = False
                other.tab_focus = None
        frame.tab_focus = node
        node.is_focused = True
        node.focus_visible = True
        self.focused_frame = frame
        self.tab_focus = node
        frame.restyle()
        self.render()
        return node

    # -- 연습문제 15-10 ------------------------------------------------- #

    def go_back(self):
        """가장 최근에 이동한 프레임에서 뒤로 간다."""
        frame = self.last_navigated_frame()
        if frame is None:
            return None
        entry = frame.history.back()
        if entry is None:
            return None
        frame.load(entry.url, record=False)     # 8-5 의 HistoryEntry
        self.render()
        return entry.url

    def last_navigated_frame(self):
        """방문 기록에 남은 이동 중 가장 나중 것을 가진 프레임."""
        best, best_time = None, -1
        for frame in self.frames():
            if not frame.history.can_back():
                continue
            stamp = getattr(frame, "nav_serial", 0)
            if stamp >= best_time:
                best, best_time = frame, stamp
        return best


# ---------------------------------------------------------------------- #
# 연습문제 15-9: 프레임을 넘나드는 탭 순서
# ---------------------------------------------------------------------- #

def frame_tab_order(root):
    """모든 프레임의 포커스 대상을, 프레임 순서대로 이어 붙인 목록."""
    out = []
    for frame in root.all_frames():
        for node in frame.focusable():
            out.append((frame, node))
    return out


def next_focus(order, current):
    if not order:
        return None
    if current is None or current not in order:
        return order[0]
    return order[(order.index(current) + 1) % len(order)]


# ---------------------------------------------------------------------- #
# 연습문제 15-8: postMessage 의 대상 출처
# ---------------------------------------------------------------------- #

def origin_matches(target_origin, frame_origin):
    if target_origin in (None, "", "*"):
        return True
    return target_origin.rstrip("/") == (frame_origin or "").rstrip("/")


def main(argv):
    from ex15_sdl import run
    run(argv[0] if argv else ex11.HOME_URL)


if __name__ == "__main__":
    main(sys.argv[1:])
