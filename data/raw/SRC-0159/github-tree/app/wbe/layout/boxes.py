"""배치 트리.

    DocumentLayout   문서 하나
      BlockLayout    블록 상자 (또는 인라인 내용을 담은 익명 상자)
        LineLayout   줄 하나
          TextLayout 낱말 하나
          EmbedLayout 입력란·버튼·이미지·캔버스·iframe

`BlockLayout` 은 노드 하나가 아니라 **형제 목록**을 받는다. 익명 블록 상자와
런인 제목이 모두 "어떤 형제들을 한 상자에 담을까" 의 문제라, 그 판단을
`group_children` 한 곳에 모아 두었기 때문이다.
"""

from wbe.css.style import is_block, is_skipped
from wbe.css.values import parse_px
from wbe.dom.nodes import Element, Text
from wbe.layout.fonts import (SMALLCAPS_SCALE, SOFT_HYPHEN, font_for_style,
                              get_font)
from wbe.paint.commands import DrawImage, DrawRect, DrawText
from wbe.paint.effects import border_radius, paint_visual_effects
from wbe.paint.geometry import HSTEP, VSTEP, WIDTH, Rect

LINKS_BAR_COLOR = "#eeeeee"
TOC_COLOR = "#dddddd"
TOC_LABEL = "Table of Contents"
BULLET_SIZE = 4
LIST_INDENT = 2 * HSTEP


def group_children(node):
    """자식들을 상자 단위(형제 목록)로 묶는다.

    - `<head>`/`<script>`/`<style>` 은 건너뛴다
    - `<h6>` 은 자기 상자를 만들지 않고 다음 묶음의 첫머리로 들어간다
    - 이어지는 인라인 형제들은 하나의 익명 상자로 묶는다
    """
    groups, run, pending_runin = [], [], []

    def flush_run():
        if run:
            groups.append(run[:])
            run.clear()

    for child in node.children:
        if is_skipped(child):
            continue
        if isinstance(child, Element) and child.tag == "h6":
            flush_run()
            pending_runin.append(child)
            continue
        if is_block(child):
            flush_run()
            groups.append(pending_runin + [child])
            pending_runin = []
        else:
            if pending_runin:
                run.extend(pending_runin)
                pending_runin = []
            run.append(child)
    flush_run()
    if pending_runin:
        groups.append(pending_runin)
    return groups


class LayoutObject:
    """배치 객체의 공통 부분."""

    def __init__(self, node, parent, previous, frame=None):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.frame = frame
        self.children = []
        self.x = self.y = self.width = self.height = None
        # 그리기 캐시
        self.painted = None
        self.needs_paint = True
        self.has_dirty_paint_descendants = True

    def self_rect(self):
        return Rect(self.x, self.y, self.x + self.width, self.y + self.height)

    def should_paint(self):
        return True

    def paint(self):
        return []

    def paint_effects(self, cmds):
        return cmds


class TextLayout(LayoutObject):
    """낱말 하나. 폰트·색·위 첨자 여부를 스스로 안다."""

    def __init__(self, node, word, parent, previous, font=None, color=None,
                 superscript=False, space=True):
        super().__init__(node, parent, previous)
        self.word = word
        self.font = font
        self.color = color if color is not None else "black"
        self.superscript = superscript
        self.space = space

    def layout(self):
        self.width = self.font.measure(self.word)
        self.height = self.font.metrics("linespace")
        if self.previous:
            space = self.previous.font.measure(" ") \
                if self.previous.space and self.previous.font else 0
            self.x = self.previous.x + space + self.previous.width
        else:
            self.x = self.parent.x

    def ascent(self):
        return self.font.metrics("ascent")

    def descent(self):
        return self.font.metrics("descent")

    def paint(self):
        return [DrawText(self.x, self.y, self.word, self.font, self.color,
                         self.node)]

    def __repr__(self):
        return "TextLayout(%r)" % self.word


class LineLayout(LayoutObject):
    """줄 하나. 자식이 글자든 입력란이든 `ascent`/`descent` 로만 다룬다."""

    def __init__(self, node, parent, previous, centered=False):
        super().__init__(node, parent, previous)
        self.centered = centered

    def layout(self):
        self.width = self.parent.width
        self.x = self.parent.x
        self.y = (self.previous.y + self.previous.height
                  if self.previous else self.parent.content_top())

        for child in self.children:
            child.layout()

        if not self.children:
            self.height = 0
            return

        if self.centered:
            last = self.children[-1]
            used = last.x + last.width - self.children[0].x
            offset = (self.width - used) / 2
            for child in self.children:
                child.x += offset

        max_ascent = max(c.ascent() for c in self.children)
        baseline = self.y + 1.25 * max_ascent
        for child in self.children:
            # 위 첨자는 아랫줄이 아니라 윗줄을 맞춘다
            y = (baseline - max_ascent) \
                if getattr(child, "superscript", False) \
                else (baseline - child.ascent())
            child.place(y) if hasattr(child, "place") else setattr(child, "y", y)
        max_descent = max(c.descent() for c in self.children)
        self.height = 1.25 * (max_ascent + max_descent)

    def __repr__(self):
        return "LineLayout(%d개)" % len(self.children)


class BlockLayout(LayoutObject):
    def __init__(self, nodes, parent, previous, frame=None, skip_self=False):
        nodes = nodes if isinstance(nodes, list) else [nodes]
        super().__init__(nodes[0], parent, previous, frame)
        self.nodes = nodes
        # 버튼 안쪽은 버튼 자신을 다시 상자로 만들지 않고 내용만 흘린다
        self.skip_self = skip_self

    # -- 정체 ---------------------------------------------------------- #

    @property
    def anonymous(self):
        return len(self.nodes) > 1 or isinstance(self.node, Text)

    def element(self, tag=None):
        """익명 상자가 아니면 그 요소. 맞지 않으면 None."""
        if len(self.nodes) == 1 and isinstance(self.node, Element):
            if tag is None or self.node.tag == tag:
                return self.node
        return None

    def layout_mode(self):
        if any(isinstance(n, Text) for n in self.nodes):
            return "inline"
        if len(self.nodes) > 1:
            return "inline"
        if any(is_block(c) for c in self.node.children):
            return "block"
        if self.node.tag in ("input", "button", "img", "canvas", "iframe"):
            return "inline"
        return "inline" if self.node.children else "block"

    def style_of(self, prop, default=""):
        return getattr(self.node, "style", {}).get(prop, default)

    def zoom(self):
        return self.frame.zoom() if self.frame is not None else 1.0

    # -- 목차와 목록 --------------------------------------------------- #

    def toc_label_height(self):
        el = self.element("nav")
        if el is not None and el.attributes.get("id") == "toc":
            return get_font(12, "bold", "roman").metrics("linespace")
        return 0

    def list_indent(self):
        return LIST_INDENT if self.element("li") else 0

    def content_top(self):
        """자식이 시작할 y. 목차 제목만큼 아래로 민다."""
        return self.y + self.toc_label_height()

    # -- 배치 ---------------------------------------------------------- #

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
            self.children = []
            for group in group_children(self.node):
                child = BlockLayout(group, self, previous, self.frame)
                self.children.append(child)
                previous = child
            for child in self.children:
                child.layout()
        else:
            self.centered = self.superscript = False
            self.smallcaps = self.pre = False
            self.children = []
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

    # -- 인라인 내용 훑기 ----------------------------------------------- #

    def recurse(self, node):
        from wbe.layout.embed import (ButtonLayout, CanvasLayout, IframeLayout,
                                      ImageLayout, InputLayout)
        if isinstance(node, Text):
            if self.pre:
                self.pre_text(node)
            else:
                for word in node.text.split():
                    self.word(node, word)
        elif node.tag == "input":
            self.embed(node, InputLayout)
        elif node.tag == "button":
            self.button(node, ButtonLayout)
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

    def open_tag(self, node):
        tag = node.tag
        if tag == "br":
            self.new_line()
        elif tag == "sup":
            self.superscript = True
        elif tag == "abbr":
            self.smallcaps = True
        elif tag == "pre":
            self.pre = True
            self.new_line()
        elif tag == "h1" and node.attributes.get("class") == "title":
            self.centered = True
            self.new_line()

    def close_tag(self, node):
        tag = node.tag
        if tag == "p":
            # 문단의 줄바꿈은 태그 이름이 아니라 display 가 정한다
            if is_block(node):
                self.new_line()
        elif tag == "sup":
            self.superscript = False
        elif tag == "abbr":
            self.smallcaps = False
        elif tag == "pre":
            self.pre = False
            self.new_line()
        elif tag == "h1" and node.attributes.get("class") == "title":
            self.centered = False
            self.new_line()

    # -- 낱말 ---------------------------------------------------------- #

    def font_for(self, node, scale=1.0, weight=None):
        return font_for_style(node.style, self.zoom(), self.superscript,
                              scale, weight)

    def fits(self, text, font):
        return self.cursor_x + font.measure(text) <= self.width

    def place(self, node, text, font, color, space=True):
        line = self.children[-1]
        previous = line.children[-1] if line.children else None
        line.children.append(
            TextLayout(node, text, line, previous, font, color,
                       self.superscript, space))
        self.cursor_x += font.measure(text) + \
            (font.measure(" ") if space else 0)

    def word(self, node, word):
        if self.smallcaps:
            self.smallcaps_word(node, word)
            return
        font = self.font_for(node)
        color = node.style["color"]
        plain = word.replace(SOFT_HYPHEN, "")
        if not self.fits(plain, font):
            if SOFT_HYPHEN in word and self.hyphenate(node, word, font, color):
                return
            self.new_line()
        self.place(node, plain, font, color)

    def hyphenate(self, node, word, font, color):
        """소프트 하이픈이 있으면 거기서 끊어 본다."""
        parts = word.split(SOFT_HYPHEN)
        for i in range(len(parts) - 1, 0, -1):
            head = "".join(parts[:i]) + "-"
            if self.fits(head, font):
                self.place(node, head, font, color, space=False)
                self.new_line()
                self.word(node, SOFT_HYPHEN.join(parts[i:]))
                return True
        return False

    def smallcaps_word(self, node, word):
        """소문자만 작은 대문자로 바꿔 놓는다."""
        big = self.font_for(node)
        small = self.font_for(node, SMALLCAPS_SCALE, "bold")
        color = node.style["color"]
        plain = word.replace(SOFT_HYPHEN, "")
        if not self.fits(plain, big):
            self.new_line()
        runs, cur, cur_lower = [], "", None
        for c in plain:
            lower = c.islower()
            if cur and lower != cur_lower:
                runs.append((cur, cur_lower))
                cur = ""
            cur, cur_lower = cur + c, lower
        if cur:
            runs.append((cur, cur_lower))
        for i, (run, lower) in enumerate(runs):
            last = (i == len(runs) - 1)
            self.place(node, run.upper() if lower else run,
                       small if lower else big, color, space=last)

    def pre_text(self, node):
        """`<pre>` 안은 공백과 줄바꿈을 그대로 살린다."""
        font = self.font_for(node)
        color = node.style["color"]
        for i, seg in enumerate(node.text.split("\n")):
            if i:
                self.new_line()
            if seg:
                self.place(node, seg, font, color, space=False)

    # -- 끼워 넣는 것들 -------------------------------------------------- #

    def embed(self, node, cls):
        font = self.font_for(node)
        obj = cls(node, None, None, self.frame, font)
        probe_width, _ = obj.intrinsic_size()
        if probe_width and self.cursor_x + probe_width > self.width:
            self.new_line()
        line = self.children[-1]
        obj.parent = line
        obj.previous = line.children[-1] if line.children else None
        line.children.append(obj)
        self.cursor_x += probe_width + font.measure(" ")

    def button(self, node, cls):
        """버튼은 안쪽이 제 나름의 블록 배치를 갖는다. 줄을 혼자 쓴다."""
        font = self.font_for(node)
        if self.cursor_x > 0:
            self.new_line()
        line = self.children[-1]
        obj = cls(node, line, None, self.frame, font)
        line.children.append(obj)
        self.new_line()

    # -- 그리기 -------------------------------------------------------- #

    def should_paint(self):
        el = self.element()
        return el is None or el.tag not in ("input", "button", "img",
                                            "canvas", "iframe")

    def paint(self):
        cmds = []
        el = self.element()
        if el is None:
            return cmds

        bg = el.style.get("background-color", "transparent")
        radius = border_radius(el)
        if bg != "transparent":
            from wbe.paint.commands import DrawRRect
            cmds.append(DrawRRect(self.self_rect(), radius, bg, el)
                        if radius > 0
                        else DrawRect(self.self_rect(), bg, el))
        if getattr(el, "background_image", None) is not None:
            cmds.insert(0, DrawImage(el.background_image, self.self_rect(),
                                     el.style.get("image-rendering", "auto"),
                                     el))
        if el.tag == "nav" and el.attributes.get("class") == "links":
            cmds.append(DrawRect(self.self_rect(), LINKS_BAR_COLOR, el))
        if el.tag == "nav" and el.attributes.get("id") == "toc":
            font = get_font(12, "bold", "roman")
            h = font.metrics("linespace")
            cmds.append(DrawRect(
                Rect(self.x, self.y, self.x + self.width, self.y + h),
                TOC_COLOR, el))
            cmds.append(DrawText(self.x, self.y, TOC_LABEL, font, "black", el))
        if el.tag == "li":
            top = self.y + (VSTEP - BULLET_SIZE) // 2
            left = self.x - LIST_INDENT // 2
            cmds.append(DrawRect(
                Rect(left, top, left + BULLET_SIZE, top + BULLET_SIZE),
                "black", el))
        return cmds

    def paint_effects(self, cmds):
        el = self.element()
        if el is None:
            return cmds
        return paint_visual_effects(el, cmds, self.self_rect())

    def __repr__(self):
        what = "익명" if self.anonymous else self.node
        return "BlockLayout[%s](%s)" % (self.layout_mode(), what)


class DocumentLayout(LayoutObject):
    def __init__(self, node, frame=None):
        super().__init__(node, None, None, frame)

    def content_top(self):
        return self.y

    def layout(self, width=None):
        self.width = (width if width is not None else WIDTH) - 2 * HSTEP
        self.x, self.y = HSTEP, VSTEP
        child = BlockLayout([self.node], self, None, self.frame)
        self.children = [child]
        child.layout()
        self.height = child.height

    def __repr__(self):
        return "DocumentLayout(%s)" % (self.width,)
