"""브라우저 크롬.

크롬도 페이지와 똑같이 HTML + CSS 로 적고 같은 엔진으로 배치한다. 버튼은
`<button>`, 주소창은 `<input>`, 탭 이름은 `<a>` 다. 클릭도 페이지와 같은
방식(그리기 명령 → 노드)으로 처리한다.
"""

from wbe.css.parser import CSSParser
from wbe.css.selectors import cascade_priority, prepare_selectors
from wbe.css.style import style
from wbe.dom.nodes import Element, tree_to_list
from wbe.dom.parser import HTMLParser
from wbe.dom.serialize import escape_attr
from wbe.layout.boxes import DocumentLayout
from wbe.paint.commands import DrawLine, DrawRect, Transform, flatten
from wbe.paint.effects import paint_tree
from wbe.paint.geometry import VSTEP, WIDTH, Rect
from wbe.paint.hittest import hit
from wbe.stylesheets import BROWSER_CSS, CHROME_CSS
from wbe.tab import HOME_URL, AddressBar, address_to_url, is_bookmarked, \
    toggle_bookmark
from wbe.net.url import URL

LOCK = "\N{lock}"


class Chrome:
    def __init__(self, browser):
        self.browser = browser
        self.focus = None
        self.address = AddressBar()
        self.rules = CSSParser(BROWSER_CSS + CHROME_CSS).parse()
        self.rules.sort(key=cascade_priority)
        self.bottom = 0
        self.document = None
        self.display_list = []
        self.flat_display_list = []
        self.nodes = None
        self.render()

    # ------------------------------------------------------------------ #
    # HTML 만들기
    # ------------------------------------------------------------------ #

    def html(self):
        tab = self.browser.active_tab
        tabs = "".join(
            '<a href="wbe:tab:{0}" class="{1}">Tab {0}</a> '.format(
                i, "current" if t is tab else "")
            for i, t in enumerate(self.browser.tabs))
        frame = tab.focused_frame if tab else None
        history = frame.history if frame else None
        back_cls = "" if history and history.can_back() else "disabled"
        fwd_cls = "" if history and history.can_forward() else "disabled"
        marked = "*" if tab and is_bookmarked(tab.url) else "-"

        if self.focus == "address bar":
            value = self.address.text
        else:
            value = str(tab.url) if tab else ""

        lock = ""
        if tab is not None and tab.url is not None:
            if tab.url.is_secure() and not (frame and frame.insecure):
                lock = '<span id="lock">%s</span> ' % LOCK
            elif frame and frame.insecure:
                lock = '<span id="lock">!</span> '

        return (
            "<html><body>"
            '<nav id="tabbar">'
            '<button id="newtab">+</button> ' + tabs +
            "</nav>"
            '<nav id="urlbar">'
            '<button id="back" class="{back}">&lt;</button> '
            '<button id="forward" class="{fwd}">&gt;</button> '
            + lock +
            '<input id="address" value="{value}"> '
            '<button id="bookmark">{mark}</button>'
            "</nav>"
            "</body></html>"
        ).format(back=back_cls, fwd=fwd_cls, value=escape_attr(value),
                 mark=marked)

    # ------------------------------------------------------------------ #
    # 배치와 그리기
    # ------------------------------------------------------------------ #

    def render(self):
        self.nodes = HTMLParser(self.html()).parse()
        for node in tree_to_list(self.nodes):
            if isinstance(node, Element):
                node.is_focused = (self.focus == "address bar"
                                   and node.attributes.get("id") == "address")
        prepare_selectors(self.rules, self.nodes)
        style(self.nodes, self.rules)
        self.document = DocumentLayout(self.nodes)
        self.document.layout(self.browser.width
                             if self.browser is not None else WIDTH)
        self.display_list = []
        paint_tree(self.document, self.display_list)
        self.flat_display_list = flatten(self.display_list)
        self.bottom = self.document.height + 2 * VSTEP

    def paint(self):
        width = self.browser.width if self.browser is not None else WIDTH
        return ([DrawRect(Rect(0, 0, width, self.bottom), "white")]
                + self.display_list
                + [DrawLine(0, self.bottom, width, self.bottom, "black", 1)])

    def raster(self, canvas):
        for cmd in self.paint():
            cmd.execute(canvas)

    # ------------------------------------------------------------------ #
    # 입력
    # ------------------------------------------------------------------ #

    def node_at(self, x, y):
        for cmd in reversed(self.flat_display_list):
            if cmd.node is None or isinstance(cmd, Transform):
                continue
            if hasattr(cmd, "children") and cmd.children:
                continue
            if hit(cmd, x, y):
                return cmd.node
        return None

    def click(self, x, y):
        self.focus = None
        node = self.node_at(x, y)
        while node is not None:
            if not isinstance(node, Element):
                node = node.parent
                continue
            name = node.attributes.get("id")
            href = node.attributes.get("href", "")
            if node.tag == "button" and name == "newtab":
                self.browser.new_tab(URL(HOME_URL))
                break
            if node.tag == "button" and name == "back":
                self.browser.go_back()
                break
            if node.tag == "button" and name == "forward":
                self.browser.go_forward()
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
        if self.focus is not None:
            self.focus = None
            self.render()

    def keypress(self, char):
        if self.focus == "address bar":
            self.address.insert(char)
            self.render()
            return True
        return False

    def backspace(self):
        if self.focus == "address bar":
            self.address.backspace()
            self.render()
            return True
        return False

    def left(self):
        if self.focus == "address bar":
            self.address.left()
            self.render()

    def right(self):
        if self.focus == "address bar":
            self.address.right()
            self.render()

    def enter(self):
        if self.focus != "address bar":
            return False
        url = address_to_url(self.address.text)
        self.focus = None
        self.render()
        self.browser.load_in_active_tab(url)
        return True
