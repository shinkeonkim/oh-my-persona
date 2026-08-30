"""8장 연습문제 구현 (8-1 ~ 8-9).

lab8.py 는 그대로 두고, 1~7장 연습문제를 이어받아 그 위에 8장 기능을 얹는다.

    python3 ex8.py http://localhost:8000/

브라우저 쪽 연습문제
    8-1  Enter 키       입력란에서 Enter 로 폼 제출
    8-2  GET 폼         물음표 뒤에 붙여 보내기
    8-3  블러           포커스는 한 번에 한 곳만
    8-4  체크박스        type=checkbox, 체크된 것만 제출
    8-5  요청 재전송      POST 로 갔던 곳으로 뒤로 갈 때 물어보기
    8-8  풍부한 버튼      버튼 안에 아무 요소나
    8-9  HTML 크롬       크롬을 우리 레이아웃 엔진으로

서버 쪽 연습문제(8-6 게시판, 8-7 영속성)는 server8ex.py 에 있다.
"""

import sys
import tkinter

import ex7
from ex1 import MAX_REDIRECTS
from ex2 import WIDTH, HEIGHT, HSTEP, VSTEP
from ex3 import get_font
from ex4 import HTMLParser, Text, Element
from ex6 import (CSSParser, style, cascade_priority, is_block, group_children,
                 tree_to_list, parse_px, BROWSER_CSS)
from ex7 import (Rect, DrawText, DrawRect, DrawLine, DrawOutline, paint_tree)
from ex7 import (History as _History7, AddressBar, Tab as _Tab7,
                 Browser as _Browser7, VISITED, BOOKMARKS, base_str,
                 address_to_url, is_bookmarked, toggle_bookmark,
                 DISABLED_COLOR, BOOKMARK_ON, BOOKMARK_OFF, HOME_URL)

INPUT_WIDTH_PX = 200
CHECKBOX_SIZE = 16
BUTTON_PADDING = 4

EXTRA_CSS = """
input { font-weight: normal; font-style: normal; background-color: lightblue; }
button { font-weight: normal; font-style: normal; background-color: orange; }
a.visited { color: purple; }
"""

DEFAULT_STYLE_SHEET = CSSParser(BROWSER_CSS + EXTRA_CSS).parse()


# ---------------------------------------------------------------------- #
# URL — POST 와 질의 문자열
# ---------------------------------------------------------------------- #

def percent_encode(text):
    out = []
    for byte in text.encode("utf8"):
        c = chr(byte)
        # ASCII 범위만 안전하다. 0x80 이상은 chr() 이 라틴-1 글자를 주는데
        # 그것도 isalnum() 을 통과하므로 여기서 걸러야 이중 인코딩을 막는다.
        if (byte < 128 and c.isalnum()) or c in "-_.~":
            out.append(c)
        elif c == " ":
            out.append("+")
        else:
            out.append("%%%02X" % byte)
    return "".join(out)


def form_encode(pairs):
    return "&".join("%s=%s" % (percent_encode(k), percent_encode(v))
                    for k, v in pairs)


class URL(ex7.URL):
    """payload 가 있으면 POST 로 보낸다."""

    def request(self, payload=None, redirects_left=MAX_REDIRECTS):
        if payload is None:
            return super().request(redirects_left)
        s = self._connect()
        s.send(self._post_bytes(payload))
        response = s.makefile("rb", newline="\r\n")
        _, status, _ = self._read_status(response)
        headers = self._read_headers(response)
        if 300 <= status < 400 and "location" in headers:
            self._finish(s, headers, body=b"")
            if redirects_left <= 0:
                raise Exception("리다이렉트가 너무 많이 이어집니다")
            # POST 뒤의 리다이렉트는 GET 으로 따라간다
            return self.resolve(headers["location"]).request(
                None, redirects_left - 1)
        body = self._read_body(response, headers)
        self._finish(s, headers, body)
        return body.decode("utf8", "replace")

    def _post_bytes(self, payload):
        data = payload.encode("utf8")
        headers = {
            "Host": self.host,
            "Connection": "keep-alive",
            "User-Agent": "wbe-ko/1.0",
            "Content-Length": str(len(data)),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        lines = ["POST {} HTTP/1.1".format(self.path)]
        lines += ["{}: {}".format(k, v) for k, v in headers.items()]
        return ("\r\n".join(lines) + "\r\n\r\n").encode("utf8") + data

    def resolve(self, url):
        """상위의 resolve 가 만든 URL 을 8장 URL 로 다시 감싼다."""
        out = super().resolve(url)
        return out if isinstance(out, URL) else URL(str(out))

    def with_query(self, query):
        """연습문제 8-2: 경로 뒤에 ?질의 를 붙인 새 URL."""
        path = self.path.split("?", 1)[0]
        return URL("{}://{}:{}{}?{}".format(self.scheme, self.host, self.port,
                                            path, query))


# ---------------------------------------------------------------------- #
# 레이아웃 — 줄 안에 글자만이 아니라 입력란과 버튼도 놓인다
# ---------------------------------------------------------------------- #

class TextLayout(ex7.TextLayout):
    def ascent(self):
        return self.font.metrics("ascent")

    def descent(self):
        return self.font.metrics("descent")


class InputLayout:
    """연습문제 8-4 를 포함한 <input>. 체크박스면 네모를 그린다."""

    def __init__(self, node, parent, previous, font=None):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []
        self.font = font
        self.space = True
        self.superscript = False
        self.x = self.y = self.width = self.height = None

    def is_checkbox(self):
        return self.node.attributes.get("type", "text").casefold() == "checkbox"

    def checked(self):
        return "checked" in self.node.attributes

    def layout(self):
        if self.is_checkbox():
            self.width = self.height = CHECKBOX_SIZE
        else:
            self.width = INPUT_WIDTH_PX
            self.height = self.font.metrics("linespace")
        if self.previous:
            space = self.previous.font.measure(" ") if self.previous.space else 0
            self.x = self.previous.x + space + self.previous.width
        else:
            self.x = self.parent.x

    def ascent(self):
        return self.height

    def descent(self):
        return 0

    def self_rect(self):
        return Rect(self.x, self.y, self.x + self.width, self.y + self.height)

    def paint(self):
        cmds = []
        bg = self.node.style.get("background-color", "transparent")
        if self.is_checkbox():
            cmds.append(DrawRect(self.self_rect(),
                                 "black" if self.checked() else "white",
                                 self.node))
            cmds.append(DrawOutline(self.self_rect(), "black", 1, self.node))
            return cmds
        if bg != "transparent":
            cmds.append(DrawRect(self.self_rect(), bg, self.node))
        text = self.node.attributes.get("value", "")
        if self.node.is_focused:
            cx = self.x + self.font.measure(text)
            cmds.append(DrawLine(cx, self.y, cx, self.y + self.height,
                                 "black", 1, self.node))
        if text:
            cmds.append(DrawText(self.x, self.y, text, self.font,
                                 self.node.style["color"], self.node))
        return cmds

    def __repr__(self):
        return "InputLayout(%s)" % self.node.attributes.get("type", "text")


class ButtonLayout:
    """연습문제 8-8: 버튼 안에 아무 요소나 담는다.

    버튼은 줄 안에 놓이지만, 안쪽은 제 나름의 블록 배치를 갖는다.
    자식들은 버튼 폭 안에서만 흐르므로 밖으로 새지 않는다.
    """

    MAX_WIDTH = 300

    def __init__(self, node, parent, previous, font=None):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []
        self.font = font
        self.space = True
        self.superscript = False
        self.x = self.y = self.width = self.height = None

    def layout(self):
        avail = max(40, min(self.MAX_WIDTH, self.parent.width) -
                    2 * BUTTON_PADDING)
        self.width = avail + 2 * BUTTON_PADDING
        if self.previous:
            space = self.previous.font.measure(" ") if self.previous.space else 0
            self.x = self.previous.x + space + self.previous.width
        else:
            self.x = self.parent.x
        # 안쪽은 그냥 블록 하나. 자식이 무엇이든 우리 배치기가 처리한다.
        inner = BlockLayout([self.node], _Box(self, avail), None,
                            skip_self=True)
        self.inner = inner
        inner.layout()
        self.height = inner.height + 2 * BUTTON_PADDING

    def place(self, y):
        """줄이 정해 준 y 로 안쪽까지 옮긴다."""
        self.y = y
        dx = self.x + BUTTON_PADDING - self.inner.x
        dy = self.y + BUTTON_PADDING - self.inner.y
        for obj in tree_to_list(self.inner, [self.inner]):
            if obj.x is not None:
                obj.x += dx
            if obj.y is not None:
                obj.y += dy

    def ascent(self):
        return self.height

    def descent(self):
        return 0

    def self_rect(self):
        return Rect(self.x, self.y, self.x + self.width, self.y + self.height)

    def paint(self):
        bg = self.node.style.get("background-color", "transparent")
        cmds = []
        if bg != "transparent":
            cmds.append(DrawRect(self.self_rect(), bg, self.node))
        cmds.append(DrawOutline(self.self_rect(), "black", 1, self.node))
        paint_tree(self.inner, cmds)
        return cmds

    def __repr__(self):
        return "ButtonLayout(%dx%d)" % (self.width or 0, self.height or 0)


class _Box:
    """ButtonLayout 안쪽 배치를 위한 가짜 부모."""

    def __init__(self, owner, width):
        self.x, self.y, self.width = 0, 0, width
        self.owner = owner

    def content_top(self):
        return self.y


class LineLayout(ex7.LineLayout):
    """자식이 글자든 입력란이든 버튼이든 ascent/descent 로만 다룬다."""

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
                if isinstance(child, ButtonLayout):
                    pass

        max_ascent = max(c.ascent() for c in self.children)
        baseline = self.y + 1.25 * max_ascent
        for child in self.children:
            y = (baseline - max_ascent) if getattr(child, "superscript", False) \
                else (baseline - child.ascent())
            if isinstance(child, ButtonLayout):
                child.place(y)
            else:
                child.y = y
        max_descent = max(c.descent() for c in self.children)
        self.height = 1.25 * (max_ascent + max_descent)

    def should_paint(self):
        return True


class BlockLayout(ex7.BlockLayout):
    def __init__(self, nodes, parent, previous, skip_self=False):
        super().__init__(nodes, parent, previous)
        # ButtonLayout 안쪽은 버튼 자신을 다시 상자로 만들지 않고 내용만 흘린다
        self.skip_self = skip_self

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

    def layout_mode(self):
        if any(isinstance(n, Text) for n in self.nodes):
            return "inline"
        if len(self.nodes) > 1:
            return "inline"
        if any(is_block(c) for c in self.node.children):
            return "block"
        if self.node.tag in ("input", "button"):
            return "inline"
        return "inline" if self.node.children else "block"

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
        else:
            self.open_tag(node)
            for child in node.children:
                self.recurse(child)
            self.close_tag(node)

    def input(self, node):
        font = self.font_for(node)
        width = CHECKBOX_SIZE if \
            node.attributes.get("type", "text").casefold() == "checkbox" \
            else INPUT_WIDTH_PX
        if self.cursor_x + width > self.width:
            self.new_line()
        line = self.children[-1]
        previous = line.children[-1] if line.children else None
        obj = InputLayout(node, line, previous, font)
        line.children.append(obj)
        self.cursor_x += width + font.measure(" ")

    def button(self, node):
        """연습문제 8-8."""
        font = self.font_for(node)
        if self.cursor_x > 0:
            self.new_line()
        line = self.children[-1]
        obj = ButtonLayout(node, line, None, font)
        line.children.append(obj)
        self.new_line()

    def paint(self):
        el = self.element()
        if el is not None and el.tag in ("input", "button"):
            return []       # 입력란과 버튼은 자기 레이아웃 객체가 그린다
        return super().paint()


class DocumentLayout(ex7.DocumentLayout):
    def layout(self):
        self.width = WIDTH - 2 * HSTEP
        self.x, self.y = HSTEP, VSTEP
        child = BlockLayout([self.node], self, None)
        self.children.append(child)
        child.layout()
        self.height = child.height


# ---------------------------------------------------------------------- #
# 방문 기록 — 어떤 메서드로 갔는지 기억한다 (연습문제 8-5)
# ---------------------------------------------------------------------- #

class HistoryEntry:
    def __init__(self, url, method="GET", body=None):
        self.url = url
        self.method = method
        self.body = body

    def is_post(self):
        return self.method == "POST"

    def __repr__(self):
        return "%s %s" % (self.method, self.url)


class History(_History7):
    def visit(self, url, method="GET", body=None):
        super().visit(HistoryEntry(url, method, body))


# ---------------------------------------------------------------------- #
# 탭
# ---------------------------------------------------------------------- #

def always_resubmit(entry):
    return True


def never_resubmit(entry):
    return False


class Tab(_Tab7):
    def __init__(self, tab_height):
        super().__init__(tab_height)
        self.history = History()
        self.focus = None
        # 연습문제 8-5: POST 를 다시 보낼지 물어보는 자리
        self.confirm_resubmit = never_resubmit

    # -- 읽기 ---------------------------------------------------------- #

    def load(self, url, payload=None, record=True):
        body = url.request(payload)
        self.url = url
        self.focus = None
        if record:
            self.history.visit(url, "POST" if payload is not None else "GET",
                               payload)
        VISITED.add(base_str(url))
        self.nodes = HTMLParser(body).parse()
        for node in tree_to_list(self.nodes, []):
            if isinstance(node, Element):
                node.is_focused = False

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
            elif node.tag == "style":
                text = "".join(c.text for c in node.children
                               if isinstance(c, Text))
                rules.extend(CSSParser(text).parse())

        self.mark_visited_links()
        style(self.nodes, sorted(rules, key=cascade_priority))
        self.render()
        self.scroll = 0
        if url.fragment:
            self.scroll_to(url.fragment)

    def render(self):
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)

    # -- 포커스 (연습문제 8-3) ------------------------------------------ #

    def blur(self):
        if self.focus is not None:
            self.focus.is_focused = False
            self.focus = None

    def focus_on(self, node):
        self.blur()
        self.focus = node
        node.is_focused = True

    # -- 클릭 ---------------------------------------------------------- #

    def node_at(self, x, y):
        y += self.scroll
        for cmd in reversed(self.display_list):
            if cmd.node is not None and cmd.rect.contains_point(x, y):
                return cmd.node
        return None

    def click(self, x, y):
        self.blur()
        node = self.node_at(x, y)
        while node is not None:
            if isinstance(node, Text):
                pass
            elif node.tag == "a" and "href" in node.attributes:
                return self.follow(self.url.resolve(node.attributes["href"]))
            elif node.tag == "input":
                type_ = node.attributes.get("type", "text").casefold()
                if type_ == "checkbox":                    # 연습문제 8-4
                    if "checked" in node.attributes:
                        del node.attributes["checked"]
                    else:
                        node.attributes["checked"] = ""
                else:
                    self.focus_on(node)
                    node.attributes["value"] = ""
                self.render()
                return None
            elif node.tag == "button":
                return self.submit_form(node)
            node = node.parent
        return None

    def follow(self, url):
        if self.url is not None and url.same_page(self.url) and url.fragment:
            self.history.visit(url)
            self.url = url
            self.scroll_to(url.fragment)
            return url
        self.load(url)
        return url

    # -- 폼 ------------------------------------------------------------ #

    def form_for(self, node):
        while node is not None:
            if isinstance(node, Element) and node.tag == "form" \
                    and "action" in node.attributes:
                return node
            node = node.parent
        return None

    def form_pairs(self, form):
        pairs = []
        for node in tree_to_list(form, []):
            if not isinstance(node, Element) or node.tag != "input":
                continue
            if "name" not in node.attributes:
                continue
            type_ = node.attributes.get("type", "text").casefold()
            if type_ in ("submit", "button"):
                continue
            if type_ == "checkbox":                       # 연습문제 8-4
                if "checked" not in node.attributes:
                    continue
                value = node.attributes.get("value", "on")
            else:
                value = node.attributes.get("value", "")
            pairs.append((node.attributes["name"], value))
        return pairs

    def submit_form(self, node):
        form = self.form_for(node)
        if form is None:
            return None
        body = form_encode(self.form_pairs(form))
        url = self.url.resolve(form.attributes["action"])
        method = form.attributes.get("method", "post").casefold()
        if method == "get":                                # 연습문제 8-2
            target = url.with_query(body)
            self.load(target)
            return target
        self.load(url, payload=body)
        return url

    # -- 키 입력 ------------------------------------------------------- #

    def keypress(self, char):
        if self.focus is not None:
            self.focus.attributes["value"] = \
                self.focus.attributes.get("value", "") + char
            self.render()
            return True
        return False

    def backspace(self):
        if self.focus is not None:
            value = self.focus.attributes.get("value", "")
            self.focus.attributes["value"] = value[:-1]
            self.render()
            return True
        return False

    def enter(self):
        """연습문제 8-1: 입력란 안에서 Enter 는 폼을 낸다."""
        if self.focus is None:
            return None
        return self.submit_form(self.focus)

    # -- 방문 기록 (연습문제 8-5) --------------------------------------- #

    def go_back(self):
        if not self.history.can_back():
            return None
        entry = self.history.back()
        if entry.is_post() and not self.confirm_resubmit(entry):
            self.history.forward()          # 되돌린다
            return None
        self.load(entry.url, entry.body if entry.is_post() else None,
                  record=False)
        return entry.url

    def go_forward(self):
        if not self.history.can_forward():
            return None
        entry = self.history.forward()
        if entry.is_post() and not self.confirm_resubmit(entry):
            self.history.back()
            return None
        self.load(entry.url, entry.body if entry.is_post() else None,
                  record=False)
        return entry.url


# ---------------------------------------------------------------------- #
# 연습문제 8-9: HTML 로 만든 브라우저 크롬
# ---------------------------------------------------------------------- #

CHROME_CSS = """
body { background-color: white; }
nav { display: block; }
button { background-color: #eeeeee; }
input { background-color: white; }
a { color: black; }
a.current { font-weight: bold; }
button.disabled { color: #999999; }
"""


def escape(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


class HTMLChrome:
    """크롬을 HTML + CSS 로 적고, 페이지와 같은 엔진으로 배치한다.

    버튼은 <button>, 주소창은 <input>, 탭 이름은 <a> 다. 클릭 처리도
    페이지와 같은 방식(그리기 명령 -> 노드)으로 한다.
    """

    def __init__(self, browser):
        self.browser = browser
        self.focus = None
        self.address = AddressBar()
        self.rules = sorted(CSSParser(BROWSER_CSS + EXTRA_CSS
                                      + CHROME_CSS).parse(),
                            key=cascade_priority)
        self.bottom = 0
        self.document = None
        self.display_list = []
        self.render()

    # -- HTML 만들기 --------------------------------------------------- #

    def html(self):
        tab = self.browser.active_tab
        tabs = "".join(
            '<a href="wbe:tab:{0}" class="{1}">Tab {0}</a> '.format(
                i, "current" if t is self.browser.active_tab else "")
            for i, t in enumerate(self.browser.tabs))
        back_cls = "" if tab and tab.history.can_back() else "disabled"
        fwd_cls = "" if tab and tab.history.can_forward() else "disabled"
        marked = "*" if tab and is_bookmarked(tab.url) else "-"
        if self.focus == "address bar":
            value = self.address.text
        else:
            value = str(tab.url) if tab else ""
        return (
            "<html><body>"
            '<nav id="tabbar">'
            '<button id="newtab">+</button> ' + tabs +
            "</nav>"
            '<nav id="urlbar">'
            '<button id="back" class="{back}">&lt;</button> '
            '<button id="forward" class="{fwd}">&gt;</button> '
            '<input id="address" value="{value}"> '
            '<button id="bookmark">{mark}</button>'
            "</nav>"
            "</body></html>"
        ).format(back=back_cls, fwd=fwd_cls, value=escape(value), mark=marked)

    def render(self):
        self.nodes = HTMLParser(self.html()).parse()
        for node in tree_to_list(self.nodes, []):
            if isinstance(node, Element):
                node.is_focused = (self.focus == "address bar"
                                   and node.attributes.get("id") == "address")
        style(self.nodes, self.rules)
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)
        self.bottom = self.document.height + 2 * VSTEP

    def paint(self):
        cmds = [DrawRect(Rect(0, 0, WIDTH, self.bottom), "white")]
        cmds.extend(self.display_list)
        cmds.append(DrawLine(0, self.bottom, WIDTH, self.bottom, "black", 1))
        return cmds

    # -- 입력 ---------------------------------------------------------- #

    def node_at(self, x, y):
        for cmd in reversed(self.display_list):
            if cmd.node is not None and cmd.rect.contains_point(x, y):
                return cmd.node
        return None

    def click(self, x, y):
        self.focus = None
        node = self.node_at(x, y)
        while node is not None:
            if isinstance(node, Text):
                node = node.parent
                continue
            name = node.attributes.get("id")
            href = node.attributes.get("href", "")
            if node.tag == "button" and name == "newtab":
                self.browser.new_tab(URL(HOME_URL))
                break
            if node.tag == "button" and name == "back":
                self.browser.active_tab.go_back()
                break
            if node.tag == "button" and name == "forward":
                self.browser.active_tab.go_forward()
                break
            if node.tag == "button" and name == "bookmark":
                toggle_bookmark(self.browser.active_tab.url)
                break
            if node.tag == "input" and name == "address":
                self.focus = "address bar"
                self.address.set_text("")
                break
            if node.tag == "a" and href.startswith("wbe:tab:"):
                i = int(href[len("wbe:tab:"):])
                if 0 <= i < len(self.browser.tabs):
                    self.browser.active_tab = self.browser.tabs[i]
                break
            node = node.parent
        self.render()
        return self.focus

    def blur(self):
        self.focus = None
        self.render()

    def keypress(self, char):
        if self.focus == "address bar":
            self.address.insert(char)
            self.render()

    def backspace(self):
        if self.focus == "address bar":
            self.address.backspace()
            self.render()

    def left(self):
        if self.focus == "address bar":
            self.address.left()
            self.render()

    def right(self):
        if self.focus == "address bar":
            self.address.right()
            self.render()

    def enter(self):
        if self.focus == "address bar":
            self.browser.active_tab.load(address_to_url(self.address.text))
            self.focus = None
            self.render()
            return True
        return False


# ---------------------------------------------------------------------- #
# 브라우저
# ---------------------------------------------------------------------- #

class Browser(_Browser7):
    def __init__(self, root=None):
        super().__init__(root)
        self.chrome = HTMLChrome(self)        # 연습문제 8-9

    def new_tab(self, url, background=False):
        tab = Tab(HEIGHT - self.chrome.bottom)
        tab.load(url)
        self.tabs.append(tab)
        if not background or self.active_tab is None:
            self.active_tab = tab
        self.chrome.render()
        self.draw()
        return tab

    # -- 포커스 조정 (연습문제 8-3) ------------------------------------- #

    def handle_click(self, e):
        if e.y < self.chrome.bottom:
            if self.active_tab is not None:
                self.active_tab.blur()        # 커서가 둘이 되지 않게
            self.chrome.click(e.x, e.y)
        else:
            self.chrome.blur()
            self.active_tab.click(e.x, e.y - self.chrome.bottom)
        self.draw()

    def handle_key(self, e):
        if len(e.char) == 0:
            return
        if not (0x20 <= ord(e.char) < 0x7f):
            return
        if self.chrome.focus:
            self.chrome.keypress(e.char)
        elif self.active_tab is not None:
            self.active_tab.keypress(e.char)
        self.draw()

    def handle_backspace(self, e):
        if self.chrome.focus:
            self.chrome.backspace()
        elif self.active_tab is not None:
            self.active_tab.backspace()
        self.draw()

    def handle_enter(self, e):
        if not self.chrome.enter():
            if self.active_tab is not None:
                self.active_tab.enter()       # 연습문제 8-1
        self.chrome.render()
        self.draw()

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
