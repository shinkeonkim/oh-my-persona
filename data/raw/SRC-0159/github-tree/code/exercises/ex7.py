"""7장 연습문제 구현 (7-1 ~ 7-11).

lab7.py 는 그대로 두고, 1~6장 연습문제를 이어받아 그 위에 7장 기능을 얹는다.

    python3 ex7.py https://browser.engineering/

7장에서 줄과 글자가 각각 레이아웃 객체(LineLayout / TextLayout)가 되므로,
3~6장에서 만든 배치 기능(가운데 정렬·위 첨자·소프트 하이픈·스몰 캡·<pre>·
익명 상자·런인 제목·width/height)도 그 구조로 옮겨 담았다.

구현한 연습문제
    7-1  백스페이스        주소창에서 한 글자 지우기
    7-2  가운데 클릭        Button-2 로 링크를 새 탭에서 열기
    7-3  창 제목           <title> 을 창 제목으로
    7-4  앞으로 가기        되돌리기 + 갈 곳 없으면 회색
    7-5  프래그먼트        #id 로 스크롤, 같은 페이지면 다시 안 읽음
    7-6  검색             URL 이 아니면 검색 엔진으로
    7-7  방문한 링크        방문한 곳은 보라색
    7-8  북마크           about:bookmarks 와 토글 버튼
    7-9  커서             좌우 방향키로 글자 사이를 오감
    7-10 여러 창           Ctrl+N 으로 새 창
    7-11 디스플레이 리스트를 통한 클릭
"""

import sys
import tkinter
import urllib.parse

import ex6
from ex1 import URL as BaseURL
from ex2 import URL as AboutURL, WIDTH, HEIGHT, HSTEP, VSTEP, SCROLL_STEP
from ex3 import get_font, SOFT_HYPHEN, SUP_SCALE, SMALLCAPS_SCALE
from ex4 import HTMLParser, Text, Element
from ex5 import (is_skipped, LINKS_BAR_COLOR, TOC_COLOR, TOC_LABEL,
                 BULLET_SIZE, LIST_INDENT)
from ex6 import (CSSParser, style, cascade_priority, is_block, group_children,
                 tree_to_list, parse_px, BROWSER_CSS)

SEARCH_URL = "https://google.com/search?q={}"      # 연습문제 7-6
VISITED_COLOR = "purple"                           # 연습문제 7-7
BOOKMARK_ON = "#ffcc00"                            # 연습문제 7-8
BOOKMARK_OFF = "white"
DISABLED_COLOR = "#999999"                         # 연습문제 7-4
HOME_URL = "https://browser.engineering/"

VISITED = set()          # 연습문제 7-7
BOOKMARKS = []           # 연습문제 7-8

EXTRA_CSS = """
a.visited { color: %s; }
""" % VISITED_COLOR

DEFAULT_STYLE_SHEET = CSSParser(BROWSER_CSS + EXTRA_CSS).parse()


# ---------------------------------------------------------------------- #
# URL — 프래그먼트(7-5), about:bookmarks(7-8)
# ---------------------------------------------------------------------- #

class URL(AboutURL):
    """#프래그먼트를 떼어서 따로 들고 다닌다 (연습문제 7-5)."""

    def __init__(self, url):
        self.fragment = None
        if "#" in url:
            url, self.fragment = url.split("#", 1)
            self.fragment = self.fragment or None
        super().__init__(url)

    def request(self, *args, **kwargs):
        if self.scheme == "about" and self.path == "bookmarks":
            return bookmarks_page()          # 연습문제 7-8
        if self.scheme == "data":
            # data: URL 의 내용은 퍼센트 인코딩돼 있다 (RFC 2397)
            return urllib.parse.unquote(self.data)
        return super().request(*args, **kwargs)

    def resolve(self, url):
        """상대 URL 을 절대 URL 로. '#id' 는 같은 페이지의 다른 곳이다."""
        if url.startswith("#"):
            out = URL(str(self))
            out.fragment = url[1:] or None
            return out
        if "://" in url or url.startswith(("about:", "data:", "view-source:")):
            return URL(url)
        if getattr(self, "scheme", None) in ("about", "data"):
            return URL(url)
        if not url.startswith("/"):
            dir_, _, _ = self.path.rpartition("/")
            while url.startswith("../"):
                url = url[3:]
                if "/" in dir_:
                    dir_, _, _ = dir_.rpartition("/")
            url = dir_ + "/" + url
        return URL("{}://{}:{}{}".format(self.scheme, self.host, self.port, url))

    def same_page(self, other):
        """프래그먼트만 다른가? (연습문제 7-5)"""
        return base_str(self) == base_str(other)

    def __str__(self):
        out = super().__repr__()
        return out + ("#" + self.fragment if self.fragment else "")

    __repr__ = __str__


def base_str(url):
    return AboutURL.__repr__(url) if url.scheme == "about" \
        else BaseURL.__repr__(url)


def bookmarks_page():
    """연습문제 7-8: 북마크 목록을 HTML 로 만들어 준다."""
    items = "".join('<li><a href="{0}">{0}</a></li>'.format(b)
                    for b in BOOKMARKS)
    return ("<html><head><title>Bookmarks</title></head><body>"
            "<h1>Bookmarks</h1><ul>" + (items or "<li>(비어 있음)</li>")
            + "</ul></body></html>")


def looks_like_url(text):
    """연습문제 7-6: 주소인가 검색어인가."""
    text = text.strip()
    if not text or " " in text:
        return False
    if "://" in text:
        return True
    if text.startswith(("about:", "data:", "file:", "view-source:")):
        return True
    head = text.split("/", 1)[0]
    return "." in head and not head.endswith(".")


def address_to_url(text):
    """연습문제 7-6: 주소창 글자를 URL 로."""
    text = text.strip()
    if not looks_like_url(text):
        return URL(SEARCH_URL.format(text.replace(" ", "+")))
    if "://" not in text and not text.startswith(
            ("about:", "data:", "file:", "view-source:")):
        text = "https://" + text
    try:
        return URL(text)
    except Exception:
        return URL("about:blank")


# ---------------------------------------------------------------------- #
# 그리기 명령 — 모두 Rect 를 쓰고, 자기를 만든 노드를 기억한다 (7-11)
# ---------------------------------------------------------------------- #

class Rect:
    def __init__(self, left, top, right, bottom):
        self.left, self.top = left, top
        self.right, self.bottom = right, bottom

    def contains_point(self, x, y):
        return self.left <= x < self.right and self.top <= y < self.bottom

    def __repr__(self):
        return "Rect(%g, %g, %g, %g)" % (self.left, self.top,
                                         self.right, self.bottom)


class DrawCommand:
    def __init__(self, rect, node=None):
        self.rect = rect
        self.node = node          # 연습문제 7-11


class DrawText(DrawCommand):
    def __init__(self, x1, y1, text, font, color="black", node=None):
        super().__init__(
            Rect(x1, y1, x1 + font.measure(text),
                 y1 + font.metrics("linespace")), node)
        self.text, self.font, self.color = text, font, color
        self.top, self.left = y1, x1
        self.bottom = self.rect.bottom

    def execute(self, scroll, canvas):
        canvas.create_text(self.rect.left, self.rect.top - scroll,
                           text=self.text, font=self.font,
                           fill=self.color, anchor="nw")

    def __repr__(self):
        return "DrawText(%r)" % self.text


class DrawRect(DrawCommand):
    def __init__(self, rect, color, node=None):
        super().__init__(rect, node)
        self.color = color

    def execute(self, scroll, canvas):
        canvas.create_rectangle(self.rect.left, self.rect.top - scroll,
                                self.rect.right, self.rect.bottom - scroll,
                                width=0, fill=self.color)

    def __repr__(self):
        return "DrawRect(%s, %s)" % (self.rect, self.color)


class DrawOutline(DrawCommand):
    def __init__(self, rect, color, thickness, node=None):
        super().__init__(rect, node)
        self.color, self.thickness = color, thickness

    def execute(self, scroll, canvas):
        canvas.create_rectangle(self.rect.left, self.rect.top - scroll,
                                self.rect.right, self.rect.bottom - scroll,
                                width=self.thickness, outline=self.color)


class DrawLine(DrawCommand):
    def __init__(self, x1, y1, x2, y2, color, thickness, node=None):
        super().__init__(Rect(x1, y1, x2, y2), node)
        self.color, self.thickness = color, thickness

    def execute(self, scroll, canvas):
        canvas.create_line(self.rect.left, self.rect.top - scroll,
                           self.rect.right, self.rect.bottom - scroll,
                           fill=self.color, width=self.thickness)


def paint_tree(layout_object, display_list):
    display_list.extend(layout_object.paint())
    for child in layout_object.children:
        paint_tree(child, display_list)


# ---------------------------------------------------------------------- #
# 레이아웃
# ---------------------------------------------------------------------- #

class TextLayout:
    """낱말 하나. 폰트·색·위 첨자 여부를 스스로 안다."""

    def __init__(self, node, word, parent, previous,
                 font=None, color=None, superscript=False, space=True):
        self.node = node
        self.word = word
        self.parent = parent
        self.previous = previous
        self.children = []
        self.font = font
        self.color = color if color is not None else "black"
        self.superscript = superscript
        self.space = space
        self.x = self.y = self.width = self.height = None

    def layout(self):
        self.width = self.font.measure(self.word)
        self.height = self.font.metrics("linespace")
        if self.previous:
            space = self.previous.font.measure(" ") if self.previous.space else 0
            self.x = self.previous.x + space + self.previous.width
        else:
            self.x = self.parent.x

    def paint(self):
        return [DrawText(self.x, self.y, self.word, self.font,
                         self.color, self.node)]

    def __repr__(self):
        return "TextLayout(%r)" % self.word


class LineLayout:
    def __init__(self, node, parent, previous, centered=False):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []
        self.centered = centered
        self.x = self.y = self.width = self.height = None

    def layout(self):
        self.width = self.parent.width
        self.x = self.parent.x
        self.y = (self.previous.y + self.previous.height
                  if self.previous else self.parent.content_top())

        for word in self.children:
            word.layout()

        if not self.children:
            self.height = 0
            return

        if self.centered:                       # 3장 연습문제: 가운데 정렬
            last = self.children[-1]
            used = last.x + last.width - self.children[0].x
            offset = (self.width - used) / 2
            for word in self.children:
                word.x += offset

        max_ascent = max(w.font.metrics("ascent") for w in self.children)
        baseline = self.y + 1.25 * max_ascent
        for word in self.children:
            # 위 첨자는 윗줄을 맞춘다 (3장 연습문제)
            word.y = (baseline - max_ascent) if word.superscript \
                else (baseline - word.font.metrics("ascent"))
        max_descent = max(w.font.metrics("descent") for w in self.children)
        self.height = 1.25 * (max_ascent + max_descent)

    def paint(self):
        return []

    def __repr__(self):
        return "LineLayout(%d words)" % len(self.children)


class BlockLayout:
    def __init__(self, nodes, parent, previous):
        self.nodes = nodes if isinstance(nodes, list) else [nodes]
        self.node = self.nodes[0]
        self.parent = parent
        self.previous = previous
        self.children = []
        self.x = self.y = self.width = self.height = None

    # -- 5장 연습문제에서 온 것들 -------------------------------------- #

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
        return getattr(self.node, "style", {}).get(prop, default)

    # -- 배치 ---------------------------------------------------------- #

    def layout(self):
        indent = self.list_indent()
        self.x = self.parent.x + indent

        css_width = parse_px(self.style_of("width", "auto"))        # 6-2
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
                self.recurse(node)
            for line in self.children:
                line.layout()

        css_height = parse_px(self.style_of("height", "auto"))      # 6-2
        if css_height is not None:
            self.height = css_height
        else:
            label = self.toc_label_height()
            self.height = label + sum(c.height for c in self.children)

    def new_line(self):
        last = self.children[-1] if self.children else None
        self.children.append(
            LineLayout(self.node, self, last, centered=self.centered))
        self.cursor_x = 0

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

    def color_for(self, node):
        return node.style["color"]

    def fits(self, text, font):
        return self.cursor_x + font.measure(text) <= self.width

    def place(self, node, text, font, color, space=True):
        line = self.children[-1]
        previous = line.children[-1] if line.children else None
        word = TextLayout(node, text, line, previous, font, color,
                          self.superscript, space)
        line.children.append(word)
        self.cursor_x += font.measure(text) + (font.measure(" ") if space else 0)

    def word(self, node, word):
        if self.smallcaps:
            self.smallcaps_word(node, word)
            return
        font = self.font_for(node)
        color = self.color_for(node)
        plain = word.replace(SOFT_HYPHEN, "")
        if not self.fits(plain, font):
            if SOFT_HYPHEN in word and self.hyphenate(node, word, font, color):
                return
            self.new_line()
        self.place(node, plain, font, color)

    def hyphenate(self, node, word, font, color):
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
        big = self.font_for(node)
        small = self.font_for(node, SMALLCAPS_SCALE, "bold")
        color = self.color_for(node)
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
        font = self.font_for(node)
        color = self.color_for(node)
        for i, seg in enumerate(node.text.split("\n")):
            if i:
                self.new_line()
            if seg:
                self.place(node, seg, font, color, space=False)

    # -- 그리기 -------------------------------------------------------- #

    def self_rect(self):
        return Rect(self.x, self.y, self.x + self.width, self.y + self.height)

    def paint(self):
        cmds = []
        el = self.element()
        if el is None:
            return cmds
        bg = el.style.get("background-color", "transparent")
        if bg != "transparent":
            cmds.append(DrawRect(self.self_rect(), bg, el))
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
# 브라우저 크롬을 이루는 작은 부품들
# ---------------------------------------------------------------------- #

class History:
    """연습문제 7-4: 뒤로/앞으로."""

    def __init__(self):
        self.past = []
        self.future = []

    def visit(self, url):
        self.past.append(url)
        self.future.clear()          # 새로 이동하면 앞으로 갈 곳은 사라진다

    def can_back(self):
        return len(self.past) > 1

    def can_forward(self):
        return len(self.future) > 0

    def back(self):
        if not self.can_back():
            return None
        self.future.append(self.past.pop())
        return self.past[-1]

    def forward(self):
        if not self.can_forward():
            return None
        url = self.future.pop()
        self.past.append(url)
        return url

    def current(self):
        return self.past[-1] if self.past else None


class AddressBar:
    """연습문제 7-1(백스페이스)·7-9(커서)."""

    def __init__(self, text=""):
        self.text = text
        self.cursor = len(text)

    def set_text(self, text):
        self.text = text
        self.cursor = len(text)

    def insert(self, char):
        self.text = self.text[:self.cursor] + char + self.text[self.cursor:]
        self.cursor += 1

    def backspace(self):
        if self.cursor == 0:
            return
        self.text = self.text[:self.cursor - 1] + self.text[self.cursor:]
        self.cursor -= 1

    def delete(self):
        if self.cursor >= len(self.text):
            return
        self.text = self.text[:self.cursor] + self.text[self.cursor + 1:]

    def left(self):
        self.cursor = max(0, self.cursor - 1)

    def right(self):
        self.cursor = min(len(self.text), self.cursor + 1)

    def home(self):
        self.cursor = 0

    def end(self):
        self.cursor = len(self.text)

    def before_cursor(self):
        return self.text[:self.cursor]

    def __repr__(self):
        return "AddressBar(%r, cursor=%d)" % (self.text, self.cursor)


def toggle_bookmark(url):
    """연습문제 7-8. 켜졌으면 True."""
    key = str(url)
    if key in BOOKMARKS:
        BOOKMARKS.remove(key)
        return False
    BOOKMARKS.append(key)
    return True


def is_bookmarked(url):
    return str(url) in BOOKMARKS


# ---------------------------------------------------------------------- #
# 탭
# ---------------------------------------------------------------------- #

class Tab:
    def __init__(self, tab_height):
        self.url = None
        self.tab_height = tab_height
        self.history = History()
        self.scroll = 0
        self.nodes = None
        self.document = None
        self.display_list = []

    # -- 읽기 ---------------------------------------------------------- #

    def load(self, url, record=True):
        body = url.request()
        self.url = url
        if record:
            self.history.visit(url)
        VISITED.add(base_str(url))                     # 연습문제 7-7
        self.nodes = HTMLParser(body).parse()

        rules = DEFAULT_STYLE_SHEET.copy()
        for node in tree_to_list(self.nodes, []):
            if not isinstance(node, Element):
                continue
            if node.tag == "link" and node.attributes.get("rel") == "stylesheet" \
                    and "href" in node.attributes:
                try:
                    rules.extend(CSSParser(
                        url.resolve(node.attributes["href"]).request()).parse())
                except Exception:
                    continue
            elif node.tag == "style":                  # 연습문제 6-6
                text = "".join(c.text for c in node.children
                               if isinstance(c, Text))
                rules.extend(CSSParser(text).parse())

        self.mark_visited_links()                      # 연습문제 7-7
        style(self.nodes, sorted(rules, key=cascade_priority))
        self.render()

        self.scroll = 0
        if url.fragment:                               # 연습문제 7-5
            self.scroll_to(url.fragment)

    def render(self):
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)

    def mark_visited_links(self):
        """방문한 링크에 visited 클래스를 붙인다 (연습문제 7-7).

        6-3 의 클래스 선택자를 그대로 재활용하므로 스타일 쪽은 손댈 게 없다.
        """
        for node in tree_to_list(self.nodes, []):
            if not isinstance(node, Element) or node.tag != "a":
                continue
            href = node.attributes.get("href")
            if not href:
                continue
            try:
                target = self.url.resolve(href)
            except Exception:
                continue
            if base_str(target) not in VISITED:
                continue
            classes = node.attributes.get("class", "").split()
            if "visited" not in classes:
                classes.append("visited")
            node.attributes["class"] = " ".join(classes)

    # -- 제목 ---------------------------------------------------------- #

    def title(self):
        """연습문제 7-3: <title> 안의 글자, 없으면 URL."""
        if self.nodes is not None:
            for node in tree_to_list(self.nodes, []):
                if isinstance(node, Element) and node.tag == "title":
                    text = "".join(c.text for c in node.children
                                   if isinstance(c, Text)).strip()
                    if text:
                        return text
        return str(self.url) if self.url else "새 탭"

    # -- 스크롤 -------------------------------------------------------- #

    def max_scroll(self):
        return max(self.document.height + 2 * VSTEP - self.tab_height, 0)

    def scrolldown(self):
        self.scroll = min(self.scroll + SCROLL_STEP, self.max_scroll())

    def scrollup(self):
        self.scroll = max(self.scroll - SCROLL_STEP, 0)

    def scroll_to(self, fragment):
        """연습문제 7-5: 그 id 를 가진 요소를 화면 맨 위로."""
        for obj in tree_to_list(self.document, []):
            node = getattr(obj, "node", None)
            if isinstance(node, Element) \
                    and node.attributes.get("id") == fragment:
                self.scroll = max(0, min(obj.y - VSTEP, self.max_scroll()))
                return True
        return False

    # -- 클릭 ---------------------------------------------------------- #

    def link_at(self, x, y):
        """연습문제 7-11: 좌표 -> 그리기 명령 -> 그 명령을 만든 노드 -> <a>."""
        y += self.scroll
        for cmd in reversed(self.display_list):
            if cmd.node is None or not cmd.rect.contains_point(x, y):
                continue
            node = cmd.node
            while node is not None:
                if isinstance(node, Element) and node.tag == "a" \
                        and "href" in node.attributes:
                    return self.url.resolve(node.attributes["href"])
                node = node.parent
        return None

    def click(self, x, y):
        url = self.link_at(x, y)
        if url is None:
            return None
        if self.url is not None and url.same_page(self.url) and url.fragment:
            self.history.visit(url)          # 같은 페이지면 다시 안 읽는다 (7-5)
            self.url = url
            self.scroll_to(url.fragment)
            return url
        self.load(url)
        return url

    # -- 방문 기록 ----------------------------------------------------- #

    def go_back(self):
        url = self.history.back()
        if url is not None:
            self.load(url, record=False)
        return url

    def go_forward(self):
        url = self.history.forward()
        if url is not None:
            self.load(url, record=False)
        return url

    def draw(self, canvas, offset):
        for cmd in self.display_list:
            if cmd.rect.top > self.scroll + self.tab_height:
                continue
            if cmd.rect.bottom < self.scroll:
                continue
            cmd.execute(self.scroll - offset, canvas)

    def __repr__(self):
        return "Tab(%s)" % self.url


# ---------------------------------------------------------------------- #
# 크롬
# ---------------------------------------------------------------------- #

class Chrome:
    def __init__(self, browser):
        self.browser = browser
        self.focus = None
        self.address = AddressBar()

        self.font = get_font(20, "normal", "roman")
        self.font_height = self.font.metrics("linespace")
        self.padding = 5

        self.tabbar_top = 0
        self.tabbar_bottom = self.font_height + 2 * self.padding
        plus_width = self.font.measure("+") + 2 * self.padding
        self.newtab_rect = Rect(self.padding, self.padding,
                                self.padding + plus_width,
                                self.padding + self.font_height)

        self.urlbar_top = self.tabbar_bottom
        self.urlbar_bottom = self.urlbar_top + self.font_height + 2 * self.padding

        def button(left, label):
            w = self.font.measure(label) + 2 * self.padding
            return Rect(left, self.urlbar_top + self.padding,
                        left + w, self.urlbar_bottom - self.padding), left + w

        self.back_rect, right = button(self.padding, "<")
        self.forward_rect, right = button(right + self.padding, ">")
        star_w = self.font.measure("*") + 2 * self.padding
        self.bookmark_rect = Rect(WIDTH - self.padding - star_w,
                                  self.urlbar_top + self.padding,
                                  WIDTH - self.padding,
                                  self.urlbar_bottom - self.padding)
        self.address_rect = Rect(right + self.padding,
                                 self.urlbar_top + self.padding,
                                 self.bookmark_rect.left - self.padding,
                                 self.urlbar_bottom - self.padding)
        self.bottom = self.urlbar_bottom

    def tab_rect(self, i):
        start = self.newtab_rect.right + self.padding
        w = self.font.measure("Tab X") + 2 * self.padding
        return Rect(start + w * i, self.tabbar_top,
                    start + w * (i + 1), self.tabbar_bottom)

    # -- 그리기 -------------------------------------------------------- #

    def paint(self):
        cmds = [DrawRect(Rect(0, 0, WIDTH, self.bottom), "white"),
                DrawLine(0, self.bottom, WIDTH, self.bottom, "black", 1)]
        cmds.append(DrawOutline(self.newtab_rect, "black", 1))
        cmds.append(DrawText(self.newtab_rect.left + self.padding,
                             self.newtab_rect.top, "+", self.font))

        for i, tab in enumerate(self.browser.tabs):
            bounds = self.tab_rect(i)
            cmds.append(DrawLine(bounds.left, 0, bounds.left, bounds.bottom,
                                 "black", 1))
            cmds.append(DrawLine(bounds.right, 0, bounds.right, bounds.bottom,
                                 "black", 1))
            cmds.append(DrawText(bounds.left + self.padding, bounds.top +
                                 self.padding, "Tab %d" % i, self.font))
            if tab is self.browser.active_tab:
                cmds.append(DrawLine(0, bounds.bottom, bounds.left,
                                     bounds.bottom, "black", 1))
                cmds.append(DrawLine(bounds.right, bounds.bottom, WIDTH,
                                     bounds.bottom, "black", 1))

        tab = self.browser.active_tab
        # 연습문제 7-4: 갈 곳이 없으면 회색
        back_color = "black" if tab and tab.history.can_back() \
            else DISABLED_COLOR
        fwd_color = "black" if tab and tab.history.can_forward() \
            else DISABLED_COLOR
        cmds.append(DrawOutline(self.back_rect, back_color, 1))
        cmds.append(DrawText(self.back_rect.left + self.padding,
                             self.back_rect.top, "<", self.font, back_color))
        cmds.append(DrawOutline(self.forward_rect, fwd_color, 1))
        cmds.append(DrawText(self.forward_rect.left + self.padding,
                             self.forward_rect.top, ">", self.font, fwd_color))

        # 연습문제 7-8: 북마크된 페이지면 노란 버튼
        marked = tab is not None and is_bookmarked(tab.url)
        cmds.append(DrawRect(self.bookmark_rect,
                             BOOKMARK_ON if marked else BOOKMARK_OFF))
        cmds.append(DrawOutline(self.bookmark_rect, "black", 1))
        cmds.append(DrawText(self.bookmark_rect.left + self.padding,
                             self.bookmark_rect.top, "*", self.font))

        cmds.append(DrawOutline(self.address_rect, "black", 1))
        left = self.address_rect.left + self.padding
        if self.focus == "address bar":
            cmds.append(DrawText(left, self.address_rect.top,
                                 self.address.text, self.font))
            # 연습문제 7-9: 커서는 글자 사이 어디에나 설 수 있다
            cx = left + self.font.measure(self.address.before_cursor())
            cmds.append(DrawLine(cx, self.address_rect.top,
                                 cx, self.address_rect.bottom, "red", 1))
        elif tab is not None:
            cmds.append(DrawText(left, self.address_rect.top,
                                 str(tab.url), self.font))
        return cmds

    # -- 입력 ---------------------------------------------------------- #

    def click(self, x, y):
        self.focus = None
        if self.newtab_rect.contains_point(x, y):
            self.browser.new_tab(URL(HOME_URL))
        elif self.back_rect.contains_point(x, y):
            self.browser.active_tab.go_back()
        elif self.forward_rect.contains_point(x, y):        # 7-4
            self.browser.active_tab.go_forward()
        elif self.bookmark_rect.contains_point(x, y):       # 7-8
            toggle_bookmark(self.browser.active_tab.url)
        elif self.address_rect.contains_point(x, y):
            self.focus = "address bar"
            self.address.set_text("")
        else:
            for i, tab in enumerate(self.browser.tabs):
                if self.tab_rect(i).contains_point(x, y):
                    self.browser.active_tab = tab
                    break

    def keypress(self, char):
        if self.focus == "address bar":
            self.address.insert(char)

    def backspace(self):                                    # 7-1
        if self.focus == "address bar":
            self.address.backspace()

    def left(self):                                         # 7-9
        if self.focus == "address bar":
            self.address.left()

    def right(self):                                        # 7-9
        if self.focus == "address bar":
            self.address.right()

    def enter(self):
        if self.focus == "address bar":
            self.browser.active_tab.load(address_to_url(self.address.text))
            self.focus = None


# ---------------------------------------------------------------------- #
# 창 (연습문제 7-10)
# ---------------------------------------------------------------------- #

WINDOWS = []


class Browser:
    """창 하나. 탭들은 자기가 속한 창이 들고 있다."""

    def __init__(self, root=None):
        self.window = tkinter.Toplevel(root) if root is not None \
            else tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT,
                                     bg="white")
        self.canvas.pack()
        self.tabs = []
        self.active_tab = None
        self.chrome = Chrome(self)
        WINDOWS.append(self)

        self.window.bind("<Down>", self.handle_down)
        self.window.bind("<Up>", self.handle_up)
        self.window.bind("<Button-1>", self.handle_click)
        self.window.bind("<Button-2>", self.handle_middle_click)   # 7-2
        self.window.bind("<Key>", self.handle_key)
        self.window.bind("<Return>", self.handle_enter)
        self.window.bind("<BackSpace>", self.handle_backspace)     # 7-1
        self.window.bind("<Left>", self.handle_left)               # 7-9
        self.window.bind("<Right>", self.handle_right)             # 7-9
        self.window.bind("<Control-n>", self.handle_new_window)    # 7-10
        self.window.protocol("WM_DELETE_WINDOW", self.close)

    # -- 탭 ------------------------------------------------------------ #

    def new_tab(self, url, background=False):
        tab = Tab(HEIGHT - self.chrome.bottom)
        tab.load(url)
        self.tabs.append(tab)
        if not background:
            self.active_tab = tab
        elif self.active_tab is None:
            self.active_tab = tab
        self.draw()
        return tab

    def set_title(self):
        """연습문제 7-3."""
        if self.active_tab is not None:
            self.window.title(self.active_tab.title())

    # -- 이벤트 -------------------------------------------------------- #

    def handle_down(self, e):
        self.active_tab.scrolldown()
        self.draw()

    def handle_up(self, e):
        self.active_tab.scrollup()
        self.draw()

    def handle_click(self, e):
        if e.y < self.chrome.bottom:
            self.chrome.click(e.x, e.y)
        else:
            self.active_tab.click(e.x, e.y - self.chrome.bottom)
        self.draw()

    def handle_middle_click(self, e):
        """연습문제 7-2: 가운데 클릭은 새 탭에서 연다."""
        if e.y < self.chrome.bottom:
            return
        url = self.active_tab.link_at(e.x, e.y - self.chrome.bottom)
        if url is not None:
            self.new_tab(url, background=True)
        self.draw()

    def handle_key(self, e):
        if len(e.char) == 0:
            return
        if not (0x20 <= ord(e.char) < 0x7f):
            return
        self.chrome.keypress(e.char)
        self.draw()

    def handle_backspace(self, e):
        self.chrome.backspace()
        self.draw()

    def handle_left(self, e):
        self.chrome.left()
        self.draw()

    def handle_right(self, e):
        self.chrome.right()
        self.draw()

    def handle_enter(self, e):
        self.chrome.enter()
        self.draw()

    def handle_new_window(self, e):
        """연습문제 7-10."""
        other = Browser(root=self.window)
        other.new_tab(URL(HOME_URL))
        return other

    def close(self):
        if self in WINDOWS:
            WINDOWS.remove(self)
        self.window.destroy()

    def draw(self):
        self.canvas.delete("all")
        if self.active_tab is not None:
            self.active_tab.draw(self.canvas, self.chrome.bottom)
        for cmd in self.chrome.paint():
            cmd.execute(0, self.canvas)
        self.set_title()


def main(argv):
    browser = Browser()
    browser.new_tab(URL(argv[0]) if argv else URL(HOME_URL))
    tkinter.mainloop()


if __name__ == "__main__":
    main(sys.argv[1:])
