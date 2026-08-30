"""14장 연습문제 구현 (14-1 ~ 14-11).

lab14.py 는 그대로 두고, 1~13장 연습문제를 이어받아 그 위에 14장 기능을 얹는다.
자바스크립트 쪽은 runtime14ex.js, 창은 ex14_sdl.py 에 있다.

14장 본문 기능(확대, 다크 모드, 포커스 링, tabindex, 접근성 트리, 낭독,
마우스 호버 강조)에 더해

    14-1  대비가 좋은 포커스 링   흰 굵은 선 + 검은 얇은 선
    14-2  focus 메서드와 이벤트
    14-3  읽는 동안 요소 강조하기
    14-4  너비 미디어 쿼리        max-width
    14-5  혼합 인라인            여러 줄에 걸친 포커스 링
    14-6  스레드화된 접근성       말하기를 따로
    14-7  고대비 모드            forced-colors
    14-8  focus-visible         탭이면 보이고 클릭이면 감춘다
    14-9  OS 통합               macOS 의 say
    14-10 zoom CSS 속성
    14-11 소리 내어 말하기        pyttsx3
"""

import os
import shutil
import subprocess
import sys
import threading

import ex10
import ex11
import ex12
import ex13
from ex4 import Text, Element
import ex6
import ex8
from ex6 import (TagSelector, ClassSelector, SelectorSequence, HasSelector,
                 ImportantSelector, tree_to_list)
from ex9 import IdSelector, CSSParser as CSSParser9
from ex11 import (Rect, DrawText, DrawRect, DrawRRect, DrawOutline, DrawLine,
                  parse_px_value, WIDTH, HEIGHT, HSTEP, VSTEP)
from ex13 import Transform, Blend, paint_tree

# 확대
ZOOM_STEP = 1.1
MIN_ZOOM, MAX_ZOOM = 0.5, 4.0

# 연습문제 14-1: 바깥은 흰 굵은 선, 안쪽은 검은 얇은 선
FOCUS_OUTER_COLOR = "white"
FOCUS_INNER_COLOR = "black"
FOCUS_OUTER_WIDTH = 4
FOCUS_INNER_WIDTH = 2

# 연습문제 14-3
READING_HIGHLIGHT = "#ffff88"

# 연습문제 14-7
FORCED_COLORS = {
    "color": "#ffffff",
    "background-color": "#000000",
    "link": "#00ffff",
    "outline": "#ffff00",
}


def dpx(css_px, zoom):
    """CSS 픽셀을 장치 픽셀로."""
    return css_px * zoom


# ---------------------------------------------------------------------- #
# 말하기 (연습문제 14-9, 14-11)
# ---------------------------------------------------------------------- #

class Speaker:
    """말하기 뒷단. 시험할 때는 갈아 끼운다."""

    def speak(self, text):
        raise NotImplementedError

    def stop(self):
        pass


class PrintSpeaker(Speaker):
    """소리 없이 화면에만. 아무 뒷단도 없을 때의 기본값."""

    def speak(self, text):
        print("말하기:", text)


class RecordingSpeaker(Speaker):
    """시험용. 무엇을 말했는지 모아 둔다."""

    def __init__(self):
        self.spoken = []

    def speak(self, text):
        self.spoken.append(text)


class MacSaySpeaker(Speaker):
    """연습문제 14-9: macOS 의 내장 음성 합성기를 그대로 쓴다."""

    def __init__(self):
        self.process = None

    def available(self):
        return shutil.which("say") is not None

    def speak(self, text):
        self.stop()
        self.process = subprocess.Popen(["say", text])

    def stop(self):
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
        self.process = None


class PyttsxSpeaker(Speaker):
    """연습문제 14-11: pyttsx3 로 소리 내어 읽는다."""

    def __init__(self):
        import pyttsx3
        self.engine = pyttsx3.init()

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()


def default_speaker():
    """쓸 수 있는 뒷단 중 가장 나은 것을 고른다."""
    mac = MacSaySpeaker()
    if mac.available():
        return mac
    try:
        return PyttsxSpeaker()
    except Exception:
        return PrintSpeaker()


class AccessibilityThread:
    """연습문제 14-6: 말하기가 브라우저 스레드를 막지 않게."""

    def __init__(self, speaker=None):
        self.speaker = speaker or PrintSpeaker()
        self.condition = threading.Condition()
        self.queue = []
        self.needs_quit = False
        self.idle = threading.Event()
        self.idle.set()
        self.thread = threading.Thread(target=self.run, name="접근성 스레드")
        self.thread.daemon = True

    def start_thread(self):
        self.thread.start()

    def speak(self, text):
        with self.condition:
            self.queue.append(text)
            self.idle.clear()
            self.condition.notify_all()

    def set_needs_quit(self):
        with self.condition:
            self.needs_quit = True
            self.condition.notify_all()

    def run_one(self):
        with self.condition:
            if not self.queue:
                self.idle.set()
                return False
            text = self.queue.pop(0)
        self.speaker.speak(text)
        with self.condition:
            if not self.queue:
                self.idle.set()
        return True

    def run(self):
        while True:
            with self.condition:
                if self.needs_quit:
                    return
                if not self.queue:
                    self.condition.wait(0.05)
            self.run_one()

    def wait(self, timeout=None):
        return self.idle.wait(timeout)


# ---------------------------------------------------------------------- #
# 선택자 — 의사 클래스와 미디어 쿼리
# ---------------------------------------------------------------------- #

class PseudoclassSelector:
    def __init__(self, pseudoclass, base):
        self.pseudoclass = pseudoclass
        self.base = base
        self.priority = base.priority

    def matches(self, node):
        if not self.base.matches(node):
            return False
        if self.pseudoclass == "focus":
            return getattr(node, "is_focused", False)
        if self.pseudoclass == "focus-visible":            # 14-8
            return getattr(node, "is_focused", False) \
                and getattr(node, "focus_visible", False)
        if self.pseudoclass == "hover":
            return getattr(node, "is_hovered", False)
        return False

    def __repr__(self):
        return "%r:%s" % (self.base, self.pseudoclass)


PSEUDOCLASSES = {"focus", "focus-visible", "hover"}


class CSSParser(CSSParser9):
    """의사 클래스와 미디어 쿼리를 알아듣는다."""

    def __init__(self, s, media=None):
        super().__init__(s)
        self.media = media or {}

    def simple_selector(self):
        base = super().simple_selector()
        while self.i < len(self.s) and self.s[self.i] == ":":
            save = self.i
            self.literal(":")
            try:
                name = self.ident().casefold()
            except Exception:
                self.i = save
                break
            if name not in PSEUDOCLASSES:
                self.i = save
                break
            base = PseudoclassSelector(name, base)
        return base

    def media_query(self):
        """(prefers-color-scheme: dark) / (max-width: 400px) / (forced-colors: active)"""
        self.literal("(")
        self.whitespace()
        prop = self.ident().casefold()
        self.whitespace()
        self.literal(":")
        self.whitespace()
        value = ""
        while self.i < len(self.s) and self.s[self.i] != ")":
            value += self.s[self.i]
            self.i += 1
        self.literal(")")
        return prop, value.strip()

    def parse(self):
        rules = []
        media_stack = []
        while self.i < len(self.s):
            self.whitespace()
            if self.i >= len(self.s):
                break
            if self.s[self.i] == "@" and self.s.startswith("@media", self.i):
                self.i += len("@media")
                self.whitespace()
                prop, value = self.media_query()
                self.whitespace()
                self.literal("{")
                media_stack.append(media_matches(prop, value, self.media))
                continue
            if self.s[self.i] == "}":
                self.literal("}")
                if media_stack:
                    media_stack.pop()
                continue
            if self.s.startswith("@keyframes", self.i):
                # @keyframes 는 ex13.parse_keyframes 가 따로 읽는다
                depth = 0
                while self.i < len(self.s):
                    if self.s[self.i] == "{":
                        depth += 1
                    elif self.s[self.i] == "}":
                        depth -= 1
                        if depth == 0:
                            self.i += 1
                            break
                    self.i += 1
                continue
            try:
                selectors = self.selector_list()
                self.literal("{")
                self.whitespace()
                normal, important = self.body()
                self.literal("}")
                if all(media_stack):
                    for sel in selectors:
                        if normal:
                            rules.append((sel, normal))
                        if important:
                            rules.append((ImportantSelector(sel),
                                          important))
            except Exception:
                why = self.ignore_until(["}"])
                if why == "}":
                    self.literal("}")
                else:
                    break
        return rules


def media_matches(prop, value, media):
    """연습문제 14-4(max-width), 14-7(forced-colors) 과 본문의 다크 모드."""
    if prop == "prefers-color-scheme":
        return media.get("prefers-color-scheme", "light") == value
    if prop == "forced-colors":
        active = media.get("forced-colors", False)
        return active if value == "active" else not active
    if prop == "max-width":
        return media.get("width", WIDTH) <= parse_px_value(value, WIDTH)
    if prop == "min-width":
        return media.get("width", WIDTH) >= parse_px_value(value, 0)
    return False


BROWSER_CSS_14 = ex6.BROWSER_CSS + ex8.EXTRA_CSS + """
input:focus { outline: 2px solid black; }
button:focus { outline: 2px solid black; }
div:focus { outline: 2px solid black; }
a:focus { outline: 2px solid black; }

a:hover { outline: 1px solid black; }

@media (prefers-color-scheme: dark) {
  a { color: lightblue; }
  input { background-color: #2222ff; }
  button { background-color: #992500; }
}

@media (max-width: 400px) {
  nav { display: block; }
}

@media (forced-colors: active) {
  a { color: #00ffff; }
}
"""


# ---------------------------------------------------------------------- #
# 확대 (연습문제 14-10)
# ---------------------------------------------------------------------- #

def parse_zoom(value):
    """zoom: 150% 또는 1.5"""
    if not value:
        return 1.0
    value = value.strip()
    try:
        if value.endswith("%"):
            return float(value[:-1]) / 100
        return float(value)
    except ValueError:
        return 1.0


def effective_zoom(node, base=1.0):
    """조상들의 zoom 을 모두 곱한다."""
    zoom = base
    chain = []
    while node is not None:
        if isinstance(node, Element):
            chain.append(node)
        node = node.parent
    for element in reversed(chain):
        zoom *= parse_zoom(element.style.get("zoom"))
    return zoom


# ---------------------------------------------------------------------- #
# 고대비 (연습문제 14-7)
# ---------------------------------------------------------------------- #

def force_colors(nodes):
    """색을 몇 개의 대비 좋은 색으로 눌러 덮는다."""
    for node in nodes:
        if not isinstance(node, Element):
            continue
        node.style["color"] = FORCED_COLORS["link"] if node.tag == "a" \
            else FORCED_COLORS["color"]
        if node.style.get("background-color", "transparent") != "transparent":
            node.style["background-color"] = FORCED_COLORS["background-color"]
        if node.style.get("outline"):
            width, _ = parse_outline(node.style["outline"])
            if width:
                node.style["outline"] = "%dpx solid %s" % (
                    width, FORCED_COLORS["outline"])


# ---------------------------------------------------------------------- #
# 포커스 링
# ---------------------------------------------------------------------- #

def parse_outline(value):
    """'2px solid black' -> (2, 'black')"""
    if not value:
        return None, None
    parts = value.split()
    if len(parts) != 3 or parts[1] != "solid":
        return None, None
    return int(parse_px_value(parts[0])), parts[2]


def paint_outline(node, cmds, rects, zoom=1.0):
    """연습문제 14-1 / 14-5: 두 겹 링을, 여러 사각형에."""
    width, color = parse_outline(node.style.get("outline"))
    if not width:
        return cmds
    for rect in rects:
        outer = Rect(rect.left - FOCUS_OUTER_WIDTH / 2,
                     rect.top - FOCUS_OUTER_WIDTH / 2,
                     rect.right + FOCUS_OUTER_WIDTH / 2,
                     rect.bottom + FOCUS_OUTER_WIDTH / 2)
        cmds.append(DrawOutline(outer, FOCUS_OUTER_COLOR,
                                dpx(FOCUS_OUTER_WIDTH, zoom), node))
        cmds.append(DrawOutline(rect, color or FOCUS_INNER_COLOR,
                                dpx(FOCUS_INNER_WIDTH, zoom), node))
    return cmds


def focus_rects(document, node):
    """연습문제 14-5: 인라인이 여러 줄에 걸치면 사각형도 여러 개."""
    boxes = [o for o in tree_to_list(document, [])
             if getattr(o, "node", None) is node
             and not isinstance(o, (ex11.LineLayout, ex11.TextLayout))]
    if boxes:
        return [o.self_rect() if hasattr(o, "self_rect")
                else Rect(o.x, o.y, o.x + o.width, o.y + o.height)
                for o in boxes]
    # 인라인 요소는 자기 상자가 없다. 자손 글자 상자들을 줄별로 묶는다.
    words = [o for o in tree_to_list(document, [])
             if isinstance(o, ex11.TextLayout)
             and is_descendant(o.node, node)]
    lines = {}
    for word in words:
        lines.setdefault(round(word.y), []).append(word)
    out = []
    for _, group in sorted(lines.items()):
        left = min(w.x for w in group)
        top = min(w.y for w in group)
        right = max(w.x + w.width for w in group)
        bottom = max(w.y + w.height for w in group)
        out.append(Rect(left, top, right, bottom))
    return out


def is_descendant(node, ancestor):
    while node is not None:
        if node is ancestor:
            return True
        node = node.parent
    return False


# ---------------------------------------------------------------------- #
# 포커스
# ---------------------------------------------------------------------- #

FOCUSABLE_TAGS = ("input", "button", "a")


def get_tabindex(node):
    if not isinstance(node, Element):
        return 9999999
    tabindex = node.attributes.get("tabindex")
    if tabindex is not None:
        try:
            return int(tabindex)
        except ValueError:
            return 9999999
    return 0 if node.tag in FOCUSABLE_TAGS else 9999999


def is_focusable(node):
    if not isinstance(node, Element):
        return False
    if "tabindex" in node.attributes:
        return get_tabindex(node) >= 0
    if node.tag == "a":
        return "href" in node.attributes
    return node.tag in ("input", "button")


def focusable_nodes(nodes):
    """탭 순서대로."""
    focusable = [n for n in nodes if is_focusable(n)]
    return sorted(focusable, key=lambda n: (get_tabindex(n),
                                            nodes.index(n)))


# ---------------------------------------------------------------------- #
# 접근성 트리
# ---------------------------------------------------------------------- #

ROLES = {
    "a": "link", "input": "textbox", "button": "button",
    "html": "document", "img": "image", "h1": "heading",
    "h2": "heading", "h3": "heading", "h4": "heading",
    "h5": "heading", "h6": "heading", "ul": "list", "ol": "list",
    "li": "listitem", "nav": "navigation",
}


def role_of(node):
    if isinstance(node, Text):
        return "StaticText"
    explicit = node.attributes.get("role")
    if explicit:
        return explicit
    return ROLES.get(node.tag, "none")


class AccessibilityNode:
    def __init__(self, node, parent=None):
        self.node = node
        self.parent = parent
        self.children = []
        self.role = role_of(node)
        self.bounds = []

    def build(self):
        for child in self.node.children:
            self.build_internal(child)
        return self

    def build_internal(self, child_node):
        if role_of(child_node) == "none":
            for grandchild in child_node.children:
                self.build_internal(grandchild)
            return
        child = AccessibilityNode(child_node, self)
        self.children.append(child)
        child.build()

    def text(self):
        if isinstance(self.node, Text):
            return "%s 라고 적혀 있음" % self.node.text
        if self.role == "link":
            return "링크: %s" % self.inner_text()
        if self.role == "textbox":
            value = self.node.attributes.get("value", "")
            name = self.node.attributes.get("name", "입력란")
            if self.node.attributes.get("type", "").casefold() == "password":
                value = "*" * len(value)
            return "%s 입력란, 값 %s" % (name, value)
        if self.role == "button":
            return "버튼: %s" % self.inner_text()
        if self.role == "heading":
            return "제목: %s" % self.inner_text()
        if self.role == "document":
            return "문서"
        return "%s: %s" % (self.role, self.inner_text())

    def inner_text(self):
        return " ".join(n.text for n in tree_to_list(self.node, [])
                        if isinstance(n, Text)).strip()

    def compute_bounds(self, document):
        self.bounds = focus_rects(document, self.node) \
            if isinstance(self.node, Element) else []
        for child in self.children:
            child.compute_bounds(document)

    def contains_point(self, x, y):
        return any(r.contains_point(x, y) for r in self.bounds)

    def hit_test(self, x, y):
        found = self if self.contains_point(x, y) else None
        for child in self.children:
            deeper = child.hit_test(x, y)
            if deeper is not None:
                found = deeper
        return found

    def flatten(self, out=None):
        out = [] if out is None else out
        out.append(self)
        for child in self.children:
            child.flatten(out)
        return out

    def __repr__(self):
        return "AccessibilityNode(%s)" % self.role


def build_accessibility_tree(nodes):
    return AccessibilityNode(nodes).build()


# ---------------------------------------------------------------------- #
# 자바스크립트 — focus() 와 focus/blur 이벤트 (연습문제 14-2)
# ---------------------------------------------------------------------- #

RUNTIME_JS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "runtime14ex.js"), encoding="utf8").read()


class JSContext(ex13.JSContext):
    RUNTIME = RUNTIME_JS

    def __init__(self, tab):
        super().__init__(tab)
        self.interp.export_function("focus", self.focus)
        self.interp.export_function("blur_element", self.blur_element)
        self.interp.evaljs(
            "Node.prototype.focus = function() {"
            "  call_python('focus', this.handle) };"
            "Node.prototype.blur = function() {"
            "  call_python('blur_element', this.handle) };0;")

    def focus(self, handle):
        self.tab.focus_element(self.node(handle), visible=True)
        return handle

    def blur_element(self, handle):
        if self.tab.tab_focus is self.node(handle):
            self.tab.focus_element(None)
        return handle


def install_js():
    ex10.JSContext = JSContext
    ex12.JSContext = JSContext
    ex13.JSContext = JSContext


install_js()


# ---------------------------------------------------------------------- #
# 탭
# ---------------------------------------------------------------------- #

class Tab(ex13.Tab):
    def __init__(self, browser, tab_height, speaker=None, **kwargs):
        super().__init__(browser, tab_height, **kwargs)
        self.zoom = 1.0
        self.dark_mode = False
        self.forced_colors = False                 # 14-7
        self.accessibility_tree = None
        self.accessibility_focus = None            # 14-3
        self.tab_focus = None
        self.hovered = None
        self.speaker = speaker or PrintSpeaker()
        self.needs_accessibility = True
        self.link_bodies = {}

    # -- 미디어 --------------------------------------------------------- #

    def load(self, url, payload=None, record=True):
        super().load(url, payload, record)
        self.rebuild_rules()
        self.restyle()
        self.force_render()

    def sheet_texts(self):
        """소스 순서대로의 CSS 원문. 미디어가 바뀌면 다시 읽는다."""
        texts = [BROWSER_CSS_14]
        for node in tree_to_list(self.nodes, []):
            if isinstance(node, Element) and node.tag == "style":
                texts.append("".join(c.text for c in node.children
                                     if isinstance(c, Text)))
        return texts

    def rebuild_rules(self):
        media = self.media()
        self.base_rules = []
        for text in self.sheet_texts():
            self.base_rules.extend(CSSParser(text, media).parse())
        for node, _ in list(self.link_rules.items()):
            body = self.link_bodies.get(node)
            if body is not None:
                self.link_rules[node] = CSSParser(body, media).parse()

    def add_stylesheet(self, node, restyle=True):
        body = self.sub_request(self.url.resolve(node.attributes["href"]))
        if body is None:
            return
        self.link_bodies[node] = body
        self.link_rules[node] = CSSParser(body, self.media()).parse()
        if restyle:
            self.restyle()

    def media(self):
        return {
            "prefers-color-scheme": "dark" if self.dark_mode else "light",
            "forced-colors": self.forced_colors,
            "width": WIDTH / self.zoom,            # 14-4
        }

    def all_rules(self):
        rules = list(self.base_rules)
        for extra in self.link_rules.values():
            rules.extend(extra)
        return sorted(rules, key=ex10.cascade_priority)

    def restyle(self):
        self.rebuild_rules()
        for node in tree_to_list(self.nodes, []):
            if isinstance(node, Element):
                if not hasattr(node, "is_focused"):
                    node.is_focused = False
                if not hasattr(node, "is_hovered"):
                    node.is_hovered = False
                if not hasattr(node, "focus_visible"):
                    node.focus_visible = False
        ex13.style(self.nodes, self.all_rules(), self, self.keyframes)
        if self.forced_colors:                     # 14-7
            force_colors(tree_to_list(self.nodes, []))
        self.needs_layout = True
        self.needs_accessibility = True
        self.set_needs_render()

    # -- 연습문제 14-10: zoom 속성과 확대 ------------------------------- #

    def zoom_by(self, factor):
        self.zoom = max(MIN_ZOOM, min(self.zoom * factor, MAX_ZOOM))
        self.restyle()
        return self.zoom

    def reset_zoom(self):
        self.zoom = 1.0
        self.restyle()

    def node_zoom(self, node):
        return effective_zoom(node, self.zoom)

    # -- 포커스 --------------------------------------------------------- #

    def focusable(self):
        return focusable_nodes(tree_to_list(self.nodes, []))

    def advance_tab(self):
        """탭 키. 다음 포커스 가능한 요소로."""
        nodes = self.focusable()
        if not nodes:
            return None
        if self.tab_focus is None or self.tab_focus not in nodes:
            nxt = nodes[0]
        else:
            i = nodes.index(self.tab_focus)
            nxt = nodes[(i + 1) % len(nodes)]
        self.focus_element(nxt, visible=True)       # 14-8: 탭이면 보인다
        return nxt

    def focus_element(self, node, visible=True):
        old = self.tab_focus
        if old is not None:
            old.is_focused = False
            old.focus_visible = False
            self.dispatch_focus_event("blur", old)
        self.tab_focus = node
        self.focus = node if node is not None \
            and node.tag == "input" else None
        if node is not None:
            node.is_focused = True
            node.focus_visible = visible            # 14-8
            self.dispatch_focus_event("focus", node)
            self.speak_node(node)
        self.restyle()

    def dispatch_focus_event(self, name, node):
        """연습문제 14-2."""
        if self.js is not None:
            self.js.dispatch_event(name, node)

    def click(self, x, y):
        node = self.node_at(x, y)
        target = node if isinstance(node, Element) else \
            (node.parent if node is not None else None)
        while target is not None and not is_focusable(target):
            target = target.parent
        if target is not None:
            # 연습문제 14-8: 클릭으로 얻은 포커스는 링을 보이지 않는다
            self.focus_element(target, visible=False)
        return super().click(x, y)

    # -- 호버 ----------------------------------------------------------- #

    def hover(self, x, y):
        node = self.node_at(x, y)
        element = node if isinstance(node, Element) else \
            (node.parent if node is not None else None)
        if element is self.hovered:
            return
        if self.hovered is not None:
            self.hovered.is_hovered = False
        self.hovered = element
        if element is not None:
            element.is_hovered = True
        self.restyle()

    # -- 접근성 --------------------------------------------------------- #

    def build_accessibility(self):
        self.accessibility_tree = build_accessibility_tree(self.nodes)
        if self.document is not None:
            self.accessibility_tree.compute_bounds(self.document)
        self.needs_accessibility = False
        return self.accessibility_tree

    def speak_node(self, node):
        for a11y in self.accessibility_nodes():
            if a11y.node is node:
                self.speaker.speak(a11y.text())
                return
        if isinstance(node, Element):
            self.speaker.speak(role_of(node))

    def accessibility_nodes(self):
        if self.accessibility_tree is None or self.needs_accessibility:
            self.build_accessibility()
        return self.accessibility_tree.flatten()

    def speak_document(self):
        for a11y in self.accessibility_nodes():
            self.speaker.speak(a11y.text())

    def advance_accessibility(self):
        """연습문제 14-3: 한 노드씩 옮기며 읽고, 그 자리를 강조한다."""
        nodes = self.accessibility_nodes()
        if not nodes:
            return None
        if self.accessibility_focus is None \
                or self.accessibility_focus not in nodes:
            nxt = nodes[0]
        else:
            nxt = nodes[(nodes.index(self.accessibility_focus) + 1)
                        % len(nodes)]
        self.accessibility_focus = nxt
        self.speaker.speak(nxt.text())
        self.set_needs_paint()
        return nxt

    def reading_highlight(self):
        """지금 읽고 있는 자리의 사각형들."""
        if self.accessibility_focus is None:
            return []
        return self.accessibility_focus.bounds

    def render(self):
        changed = super().render()
        if changed:
            self.needs_accessibility = True
        if changed and self.accessibility_focus is not None:
            # 강조 상자를 디스플레이 리스트 맨 앞에 얹는다 (14-3)
            for rect in self.reading_highlight():
                self.display_list.insert(
                    0, DrawRect(rect, READING_HIGHLIGHT,
                                self.accessibility_focus.node))
            self.flat_display_list = ex11.flatten(self.display_list)
        return changed


def main(argv):
    from ex14_sdl import run
    run(argv[0] if argv else ex11.HOME_URL)


if __name__ == "__main__":
    main(sys.argv[1:])
