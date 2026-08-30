"""6장 연습문제 구현 (6-1 ~ 6-10).

lab6.py 는 그대로 두고, 1~5장 연습문제를 이어받아 그 위에 6장 연습문제를 얹는다.

    python3 ex6.py https://browser.engineering/

구현한 연습문제
    6-1  폰트            font-family 를 상속 속성으로, <code> 는 고정폭
    6-2  너비/높이        width / height 를 픽셀 또는 auto 로
    6-3  클래스 선택자     .main — 태그 선택자보다 우선
    6-4  display         layout_mode 를 display 속성으로, 블록 목록을 CSS 로
    6-5  단축 속성        font: italic bold 100% Times
    6-6  인라인 스타일시트  <style> 태그
    6-7  빠른 자손 선택자   O(nd) -> O(n+d)
    6-8  선택자 시퀀스     span.announce, 우선순위는 합
    6-9  !important      우선순위 +10000
    6-10 :has 선택자      자손의 존재로 조상을 고른다 (요소당 상각 O(1))
"""

import sys
import tkinter

from ex2 import (URL, parse_url, WIDTH, HEIGHT, HSTEP, VSTEP, SCROLL_STEP,
                 SCROLLBAR_COLOR)
from ex3 import get_font, SOFT_HYPHEN, SUP_SCALE, SMALLCAPS_SCALE
from ex4 import HTMLParser, SourceParser, Text, Element
from ex5 import (DrawText as _DrawText, DrawRect, paint_tree, is_skipped,
                 LINKS_BAR_COLOR, TOC_COLOR, TOC_LABEL,
                 BULLET_SIZE, LIST_INDENT)

IMPORTANT_BONUS = 10000          # 연습문제 6-9


class DrawText(_DrawText):
    """6장부터 글자에 색이 붙는다."""

    def __init__(self, x1, y1, text, font, color="black"):
        super().__init__(x1, y1, text, font)
        self.color = color

    def execute(self, scroll, canvas):
        canvas.create_text(self.left, self.top - scroll, text=self.text,
                           font=self.font, fill=self.color, anchor="nw")

# 연습문제 6-1: font-family 도 상속된다
INHERITED_PROPERTIES = {
    "font-size": "16px",
    "font-style": "normal",
    "font-weight": "normal",
    "font-family": "",
    "color": "black",
}

# 연습문제 6-4: 하드코딩하던 블록 목록을 브라우저 기본 스타일시트로 옮긴다
BLOCK_TAGS = [
    "html", "body", "article", "section", "nav", "aside",
    "h1", "h2", "h3", "h4", "h5", "h6", "hgroup", "header",
    "footer", "address", "p", "hr", "pre", "blockquote",
    "ol", "ul", "menu", "li", "dl", "dt", "dd", "figure",
    "figcaption", "main", "div", "table", "form", "fieldset",
    "legend", "details", "summary",
]

BROWSER_CSS = """
%s { display: block; }

pre { background-color: gray; font-family: monospace; }
code { font-family: monospace; }

a { color: blue; }
i { font-style: italic; }
b { font-weight: bold; }
small { font-size: 90%%; }
big { font-size: 110%%; }
""" % ", ".join(BLOCK_TAGS)


def tree_to_list(tree, out):
    out.append(tree)
    for child in tree.children:
        tree_to_list(child, out)
    return out


# ---------------------------------------------------------------------- #
# 선택자
# ---------------------------------------------------------------------- #

class TagSelector:
    def __init__(self, tag):
        self.tag = tag
        self.priority = 1

    def matches(self, node):
        return isinstance(node, Element) and self.tag == node.tag

    def __repr__(self):
        return self.tag


class ClassSelector:
    """연습문제 6-3: .main — 태그보다 우선하도록 우선순위를 크게 준다."""

    def __init__(self, cls):
        self.cls = cls
        self.priority = 10

    def matches(self, node):
        if not isinstance(node, Element):
            return False
        return self.cls in node.attributes.get("class", "").split()

    def __repr__(self):
        return "." + self.cls


class SelectorSequence:
    """연습문제 6-8: span.announce 처럼 붙여 쓴 것들. 우선순위는 합."""

    def __init__(self, selectors):
        self.selectors = selectors
        self.priority = sum(s.priority for s in selectors)

    def matches(self, node):
        return all(s.matches(node) for s in self.selectors)

    def __repr__(self):
        return "".join(repr(s) for s in self.selectors)


class DescendantSelector:
    """연습문제 6-7: 조상들을 목록으로 들고 한 번만 거슬러 올라간다.

    안쪽부터 맞춰 보면서 조상을 한 칸씩 올라가므로 O(n + d) 다.
    """

    def __init__(self, selectors):
        self.selectors = selectors                  # 바깥 -> 안쪽 순서
        self.priority = sum(s.priority for s in selectors)

    def matches(self, node):
        if not self.selectors[-1].matches(node):
            return False
        i = len(self.selectors) - 2
        ancestor = node.parent
        while i >= 0 and ancestor:
            if self.selectors[i].matches(ancestor):
                i -= 1
            ancestor = ancestor.parent
        return i < 0

    def __repr__(self):
        return " ".join(repr(s) for s in self.selectors)


class HasSelector:
    """연습문제 6-10: a:has(b) — 자손 b 가 있는 a.

    매칭 때마다 서브트리를 뒤지면 느리므로, 스타일 적용 전에 트리를 한 번만
    훑어서 '조건을 만족하는 조상' 집합을 만들어 둔다. 전체 O(n), 요소당 상각 O(1).
    """

    def __init__(self, base, inner):
        self.base = base
        self.inner = inner
        self.priority = base.priority + inner.priority
        self.satisfied = None      # prepare() 가 채운다

    def prepare(self, root):
        self.satisfied = set()
        for node in tree_to_list(root, []):
            if not self.inner.matches(node):
                continue
            ancestor = node.parent
            while ancestor is not None:
                if id(ancestor) in self.satisfied:
                    break          # 위쪽은 이미 표시돼 있다
                self.satisfied.add(id(ancestor))
                ancestor = ancestor.parent

    def matches(self, node):
        if self.satisfied is None:
            return False
        return self.base.matches(node) and id(node) in self.satisfied

    def __repr__(self):
        return "%r:has(%r)" % (self.base, self.inner)


class ImportantSelector:
    """연습문제 6-9: 같은 선언을 우선순위만 올려 한 번 더 적용한다."""

    def __init__(self, base):
        self.base = base
        self.priority = base.priority + IMPORTANT_BONUS

    def matches(self, node):
        return self.base.matches(node)

    def prepare(self, root):
        if hasattr(self.base, "prepare"):
            self.base.prepare(root)

    def __repr__(self):
        return "%r!important" % self.base


# ---------------------------------------------------------------------- #
# CSS 파서
# ---------------------------------------------------------------------- #

class CSSParser:
    def __init__(self, s):
        self.s = s
        self.i = 0

    def whitespace(self):
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1

    def literal(self, literal):
        if not (self.i < len(self.s) and self.s[self.i] == literal):
            raise Exception("파싱 실패: %r 를 기대했습니다" % literal)
        self.i += 1

    def word(self):
        start = self.i
        while self.i < len(self.s):
            if self.s[self.i].isalnum():
                self.i += 1
            elif self.s[self.i] in "#-.%_/":
                self.i += 1
            else:
                break
        if not (self.i > start):
            raise Exception("파싱 실패: 낱말을 기대했습니다")
        return self.s[start:self.i]

    def ident(self):
        """선택자에 쓰는 이름. word() 와 달리 '.' 을 삼키지 않는다."""
        start = self.i
        while self.i < len(self.s):
            if self.s[self.i].isalnum() or self.s[self.i] in "#-_":
                self.i += 1
            else:
                break
        if self.i == start:
            raise Exception("파싱 실패: 이름을 기대했습니다")
        return self.s[start:self.i]

    def value(self):
        """연습문제 6-5: 값이 여러 낱말일 수 있다 (font: italic bold 100% Times)."""
        start = self.i
        while self.i < len(self.s) and self.s[self.i] not in ";}":
            self.i += 1
        return self.s[start:self.i].strip()

    def pair(self):
        prop = self.word()
        self.whitespace()
        self.literal(":")
        self.whitespace()
        val = self.value()
        return prop.casefold(), val

    def ignore_until(self, chars):
        while self.i < len(self.s):
            if self.s[self.i] in chars:
                return self.s[self.i]
            self.i += 1
        return None

    def body(self):
        """(보통 선언, !important 선언) 두 벌을 돌려준다 (연습문제 6-9)."""
        normal, important = {}, {}
        while self.i < len(self.s) and self.s[self.i] != "}":
            try:
                prop, val = self.pair()
                target = normal
                if val.casefold().endswith("!important"):
                    val = val[:-len("!important")].strip()
                    target = important
                for k, v in expand_shorthand(prop, val).items():
                    target[k] = v
                self.whitespace()
                if self.i < len(self.s) and self.s[self.i] == ";":
                    self.literal(";")
                    self.whitespace()
            except Exception:
                why = self.ignore_until([";", "}"])
                if why == ";":
                    self.literal(";")
                    self.whitespace()
                else:
                    break
        return normal, important

    # -- 선택자 --------------------------------------------------------- #

    def simple_selector(self):
        """태그·클래스와 그것들을 붙여 쓴 것, 그리고 :has() 를 읽는다."""
        parts = []
        if self.i < len(self.s) and self.s[self.i] == ".":
            self.literal(".")
            parts.append(ClassSelector(self.ident().casefold()))
        else:
            parts.append(TagSelector(self.ident().casefold()))
        while self.i < len(self.s) and self.s[self.i] == ".":     # 6-8
            self.literal(".")
            parts.append(ClassSelector(self.ident().casefold()))

        base = parts[0] if len(parts) == 1 else SelectorSequence(parts)

        if self.s.startswith(":has(", self.i):                    # 6-10
            self.i += len(":has(")
            self.whitespace()
            inner = self.simple_selector()
            self.whitespace()
            self.literal(")")
            base = HasSelector(base, inner)
        return base

    def selector(self):
        out = [self.simple_selector()]
        self.whitespace()
        while self.i < len(self.s) and self.s[self.i] not in "{,":
            out.append(self.simple_selector())
            self.whitespace()
        return out[0] if len(out) == 1 else DescendantSelector(out)

    def selector_list(self):
        """쉼표로 나열된 선택자들."""
        out = [self.selector()]
        self.whitespace()
        while self.i < len(self.s) and self.s[self.i] == ",":
            self.literal(",")
            self.whitespace()
            out.append(self.selector())
            self.whitespace()
        return out

    def parse(self):
        rules = []
        while self.i < len(self.s):
            try:
                self.whitespace()
                if self.i >= len(self.s):
                    break
                selectors = self.selector_list()
                self.literal("{")
                self.whitespace()
                normal, important = self.body()
                self.literal("}")
                for sel in selectors:
                    if normal:
                        rules.append((sel, normal))
                    if important:
                        rules.append((ImportantSelector(sel), important))
            except Exception:
                why = self.ignore_until(["}"])
                if why == "}":
                    self.literal("}")
                    self.whitespace()
                else:
                    break
        return rules


def expand_shorthand(prop, value):
    """연습문제 6-5: font 한 줄을 네 속성으로 편다."""
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


def cascade_priority(rule):
    selector, body = rule
    return selector.priority


# ---------------------------------------------------------------------- #
# 스타일 적용
# ---------------------------------------------------------------------- #

def style(node, rules, root=None):
    if root is None:
        root = node
        for selector, _ in rules:                 # 6-10 준비 단계 (전체 O(n))
            if hasattr(selector, "prepare"):
                selector.prepare(root)

    node.style = {}
    for prop, default in INHERITED_PROPERTIES.items():
        node.style[prop] = node.parent.style[prop] if node.parent else default

    for selector, body in rules:
        if not selector.matches(node):
            continue
        for prop, value in body.items():
            node.style[prop] = value

    if isinstance(node, Element) and "style" in node.attributes:
        normal, important = CSSParser(node.attributes["style"]).body()
        for prop, value in {**normal, **important}.items():
            node.style[prop] = value

    if node.style["font-size"].endswith("%"):
        parent_size = (node.parent.style["font-size"] if node.parent
                       else INHERITED_PROPERTIES["font-size"])
        pct = float(node.style["font-size"][:-1]) / 100
        node.style["font-size"] = str(pct * float(parent_size[:-2])) + "px"

    for child in node.children:
        style(child, rules, root)


# ---------------------------------------------------------------------- #
# 레이아웃
# ---------------------------------------------------------------------- #

def is_block(node):
    """연습문제 6-4: 하드코딩 목록 대신 display 속성을 본다."""
    if isinstance(node, Text):
        return False
    return node.style.get("display", "inline") == "block"


def group_children(node):
    """5-2 / 5-5 / 5-6 을 display 기반 is_block 으로 다시 쓴 것."""
    groups, run, pending = [], [], []

    def flush_run():
        if run:
            groups.append(run[:])
            run.clear()

    for child in node.children:
        if is_skipped(child):
            continue
        if isinstance(child, Element) and child.tag == "h6":
            flush_run()
            pending.append(child)
            continue
        if is_block(child):
            flush_run()
            groups.append(pending + [child])
            pending = []
        else:
            if pending:
                run.extend(pending)
                pending = []
            run.append(child)
    flush_run()
    if pending:
        groups.append(pending)
    return groups


def parse_px(value):
    """'12px' -> 12.0, 'auto'/이상한 값 -> None (연습문제 6-2)."""
    if not value or value.casefold() == "auto":
        return None
    value = value.strip()
    if value.endswith("px"):
        value = value[:-2]
    try:
        return float(value)
    except ValueError:
        return None


class BlockLayout:
    def __init__(self, nodes, parent, previous):
        self.nodes = nodes if isinstance(nodes, list) else [nodes]
        self.node = self.nodes[0]
        self.parent = parent
        self.previous = previous
        self.children = []
        self.x = self.y = self.width = self.height = None
        self.display_list = []

    @property
    def anonymous(self):
        return len(self.nodes) > 1 or isinstance(self.node, Text)

    def element(self, tag=None):
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
        return "inline" if self.node.children else "block"

    def toc_label_height(self):
        el = self.element("nav")
        if el is not None and el.attributes.get("id") == "toc":
            return get_font(12, "bold", "roman").metrics("linespace")
        return 0

    def list_indent(self):
        return LIST_INDENT if self.element("li") else 0

    def content_top(self):
        return self.y + self.toc_label_height()

    def style_of(self, prop, default=""):
        return self.node.style.get(prop, default) if hasattr(self.node, "style") \
            else default

    def layout(self):
        indent = self.list_indent()
        self.x = self.parent.x + indent

        # 연습문제 6-2
        css_width = parse_px(self.style_of("width", "auto"))
        self.width = css_width if css_width is not None \
            else self.parent.width - indent

        self.y = (self.previous.y + self.previous.height
                  if self.previous else self.parent.content_top())
        label = self.toc_label_height()

        mode = self.layout_mode()
        if mode == "block":
            previous = None
            for group in group_children(self.node):
                child = BlockLayout(group, self, previous)
                self.children.append(child)
                previous = child
        else:
            self.cursor_x = 0
            self.cursor_y = label
            self.line = []
            self.centered = self.superscript = self.smallcaps = self.pre = False
            for node in self.nodes:
                self.recurse(node)
            self.flush()

        for child in self.children:
            child.layout()

        css_height = parse_px(self.style_of("height", "auto"))     # 6-2
        if css_height is not None:
            self.height = css_height
        elif mode == "block":
            self.height = label + sum(c.height for c in self.children)
        else:
            self.height = self.cursor_y

    # -- 글자 --------------------------------------------------------- #

    def font_for(self, node):
        """연습문제 6-1: font-family 를 스타일에서 가져온다."""
        s = node.style
        weight = s["font-weight"]
        style_ = s["font-style"]
        if style_ == "normal":
            style_ = "roman"
        size = int(float(s["font-size"][:-2]) * 0.75)
        if self.superscript:
            size = max(6, int(size * SUP_SCALE))
        family = s.get("font-family") or None
        return get_font(size, weight, style_, family)

    def recurse(self, node):
        if isinstance(node, Text):
            if self.pre:
                self.pre_text(node)
            else:
                for word in node.text.split():
                    self.word(node, word)
        else:
            self.open_tag(node)
            for child in node.children:
                self.recurse(child)
            self.close_tag(node)

    def open_tag(self, node):
        tag = node.tag
        if tag == "br":
            self.flush()
        elif tag == "sup":
            self.superscript = True
        elif tag == "abbr":
            self.smallcaps = True
        elif tag == "pre":
            self.flush()
            self.pre = True
        elif tag == "h1" and node.attributes.get("class") == "title":
            self.flush()
            self.centered = True

    def close_tag(self, node):
        tag = node.tag
        if tag == "p":
            if is_block(node):          # display:inline 이면 줄을 끊지 않는다
                self.flush()
                self.cursor_y += VSTEP
        elif tag == "sup":
            self.superscript = False
        elif tag == "abbr":
            self.smallcaps = False
        elif tag == "pre":
            self.flush()
            self.pre = False
        elif tag == "h1" and node.attributes.get("class") == "title":
            self.flush()
            self.centered = False

    def place(self, text, font, color, space=True):
        self.line.append((self.cursor_x, text, font, color, self.superscript))
        self.cursor_x += font.measure(text)
        if space:
            self.cursor_x += font.measure(" ")

    def fits(self, text, font):
        return self.cursor_x + font.measure(text) <= self.width

    def word(self, node, word):
        color = node.style["color"]
        if self.smallcaps:
            self.smallcaps_word(node, word, color)
            return
        font = self.font_for(node)
        plain = word.replace(SOFT_HYPHEN, "")
        if not self.fits(plain, font):
            if SOFT_HYPHEN in word and self.hyphenate(node, word, font, color):
                return
            self.flush()
        self.place(plain, font, color)

    def hyphenate(self, node, word, font, color):
        parts = word.split(SOFT_HYPHEN)
        for i in range(len(parts) - 1, 0, -1):
            head = "".join(parts[:i]) + "-"
            if self.fits(head, font):
                self.place(head, font, color, space=False)
                self.flush()
                self.word(node, SOFT_HYPHEN.join(parts[i:]))
                return True
        return False

    def smallcaps_word(self, node, word, color):
        s = node.style
        size = int(float(s["font-size"][:-2]) * 0.75)
        family = s.get("font-family") or None
        style_ = s["font-style"]
        style_ = "roman" if style_ == "normal" else style_
        big = get_font(size, s["font-weight"], style_, family)
        small = get_font(max(6, int(size * SMALLCAPS_SCALE)), "bold",
                         style_, family)
        if not self.fits(word.replace(SOFT_HYPHEN, ""), big):
            self.flush()
        runs, cur, cur_lower = [], "", None
        for c in word.replace(SOFT_HYPHEN, ""):
            lower = c.islower()
            if cur and lower != cur_lower:
                runs.append((cur, cur_lower))
                cur = ""
            cur, cur_lower = cur + c, lower
        if cur:
            runs.append((cur, cur_lower))
        for i, (run, lower) in enumerate(runs):
            last = (i == len(runs) - 1)
            self.place(run.upper() if lower else run,
                       small if lower else big, color, space=last)

    def pre_text(self, node):
        color = node.style["color"]
        for i, seg in enumerate(node.text.split("\n")):
            if i:
                self.flush()
            if seg:
                self.place(seg, self.font_for(node), color, space=False)

    def line_width(self):
        if not self.line:
            return 0
        first_x = self.line[0][0]
        last_x, last_text, last_font = self.line[-1][0], self.line[-1][1], \
            self.line[-1][2]
        return last_x + last_font.measure(last_text) - first_x

    def flush(self):
        if not self.line:
            self.cursor_x = 0
            return
        metrics = [f.metrics() for _, _, f, _, _ in self.line]
        max_ascent = max(m["ascent"] for m in metrics)
        max_descent = max(m["descent"] for m in metrics)
        baseline = self.cursor_y + 1.25 * max_ascent
        offset = ((self.width - self.line_width()) / 2 - self.line[0][0]
                  if self.centered else 0)
        for rel_x, text, font, color, is_sup in self.line:
            y = (baseline - max_ascent) if is_sup \
                else (baseline - font.metrics("ascent"))
            self.display_list.append(
                (self.x + rel_x + offset, self.y + y, text, font, color))
        self.cursor_x = 0
        self.cursor_y = baseline + 1.25 * max_descent
        self.line = []

    # -- 그리기 -------------------------------------------------------- #

    def paint(self):
        cmds = []
        el = self.element()
        if el is not None:
            bg = el.style.get("background-color", "transparent")
            if bg != "transparent":
                cmds.append(DrawRect(self.x, self.y, self.x + self.width,
                                     self.y + self.height, bg))
            if el.tag == "nav" and el.attributes.get("class") == "links":
                cmds.append(DrawRect(self.x, self.y, self.x + self.width,
                                     self.y + self.height, LINKS_BAR_COLOR))
            if el.tag == "nav" and el.attributes.get("id") == "toc":
                font = get_font(12, "bold", "roman")
                h = font.metrics("linespace")
                cmds.append(DrawRect(self.x, self.y, self.x + self.width,
                                     self.y + h, TOC_COLOR))
                cmds.append(DrawText(self.x, self.y, TOC_LABEL, font))
            if el.tag == "li":
                top = self.y + (VSTEP - BULLET_SIZE) // 2
                left = self.x - LIST_INDENT // 2
                cmds.append(DrawRect(left, top, left + BULLET_SIZE,
                                     top + BULLET_SIZE, "black"))
        if self.layout_mode() == "inline":
            for x, y, word, font, color in self.display_list:
                cmds.append(DrawText(x, y, word, font, color))
        return cmds

    def __repr__(self):
        what = "익명" if self.anonymous else self.node
        return "BlockLayout[%s](%s)" % (self.layout_mode(), what)


class DocumentLayout:
    def __init__(self, node):
        self.node = node
        self.parent = self.previous = None
        self.children = []
        self.x = self.y = self.width = self.height = None

    def content_top(self):
        return self.y

    def layout(self):
        self.width = WIDTH - 2 * HSTEP
        self.x, self.y = HSTEP, VSTEP
        child = BlockLayout([self.node], self, None)
        self.children.append(child)
        child.layout()
        self.height = child.height

    def paint(self):
        return []


# ---------------------------------------------------------------------- #
# 브라우저
# ---------------------------------------------------------------------- #

DEFAULT_STYLE_SHEET = CSSParser(BROWSER_CSS).parse()


class Browser:
    def __init__(self):
        self.scroll = 0
        self.display_list = []
        self.document = None
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.canvas.pack(fill="both", expand=True)
        self.window.bind("<Down>", lambda e: self.scroll_by(SCROLL_STEP))
        self.window.bind("<Up>", lambda e: self.scroll_by(-SCROLL_STEP))

    def load(self, url):
        body = url.request()
        parser = SourceParser(body) if url.view_source else HTMLParser(body)
        self.nodes = parser.parse()
        rules = DEFAULT_STYLE_SHEET.copy()

        nodes = tree_to_list(self.nodes, [])
        # <link rel=stylesheet>
        links = [n.attributes["href"] for n in nodes
                 if isinstance(n, Element) and n.tag == "link"
                 and n.attributes.get("rel") == "stylesheet"
                 and "href" in n.attributes]
        for link in links:
            try:
                rules.extend(CSSParser(url.resolve(link).request()).parse())
            except Exception:
                continue
        # 연습문제 6-6: <style> 태그
        for n in nodes:
            if isinstance(n, Element) and n.tag == "style":
                text = "".join(c.text for c in n.children
                               if isinstance(c, Text))
                rules.extend(CSSParser(text).parse())

        style(self.nodes, sorted(rules, key=cascade_priority))
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)
        self.draw()

    def scroll_by(self, delta):
        bottom = max(0, self.document.height + 2 * VSTEP - HEIGHT)
        scroll = max(0, min(self.scroll + delta, bottom))
        if scroll != self.scroll:
            self.scroll = scroll
            self.draw()

    def draw(self):
        self.canvas.delete("all")
        for cmd in self.display_list:
            if cmd.top > self.scroll + HEIGHT or cmd.bottom < self.scroll:
                continue
            cmd.execute(self.scroll, self.canvas)


def main(argv):
    url = parse_url(argv[0]) if argv else URL("about:blank")
    Browser().load(url)
    tkinter.mainloop()


if __name__ == "__main__":
    main(sys.argv[1:])
