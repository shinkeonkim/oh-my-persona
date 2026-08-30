"""탭 — 프레임 나무 하나와 그것을 다루는 손잡이들.

탭은 최상위 프레임을 들고 있고, 클릭·키·확대·접근성 같은 사용자 동작을
알맞은 프레임에 넘긴다.
"""

from wbe.a11y import (READING_HIGHLIGHT, build_accessibility_tree,
                      frame_tab_order, is_focusable, next_focus, role_of)
from wbe.animation import EASINGS, run_animations
from wbe.css.style import mark_style_dirty
from wbe.css.values import parse_px_value
from wbe.dom.nodes import Element, Text, is_descendant, tree_to_list
from wbe.layout.boxes import TextLayout
from wbe.layout.embed import is_checkbox
from wbe.net.url import URL, register_about
from wbe.paint.commands import DrawRect, flatten
from wbe.paint.geometry import HEIGHT, SCROLL_STEP, Rect
from wbe.paint.hittest import hit_test
from wbe.scheduling import CommitData, MeasureTime, NetworkThread, TaskRunner

ZOOM_STEP = 1.1
MIN_ZOOM, MAX_ZOOM = 0.5, 4.0

SCROLL_FRAMES = 8
FLING_FRICTION = 0.92
FLING_MIN_SPEED = 0.5

SEARCH_URL = "https://google.com/search?q={}"
HOME_URL = "https://browser.engineering/"

BOOKMARKS = []


# ---------------------------------------------------------------------- #
# 북마크와 주소창
# ---------------------------------------------------------------------- #

def bookmarks_page():
    items = "".join('<li><a href="{0}">{0}</a></li>'.format(b)
                    for b in BOOKMARKS)
    return ("<html><head><title>Bookmarks</title></head><body>"
            "<h1>Bookmarks</h1><ul>" + (items or "<li>(비어 있음)</li>")
            + "</ul></body></html>")


register_about("bookmarks", bookmarks_page)


def toggle_bookmark(url):
    key = str(url)
    if key in BOOKMARKS:
        BOOKMARKS.remove(key)
        return False
    BOOKMARKS.append(key)
    return True


def is_bookmarked(url):
    return str(url) in BOOKMARKS


def looks_like_url(text):
    """주소인가 검색어인가."""
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
    """주소창 글자를 URL 로. 주소가 아니면 검색어로 본다."""
    from wbe.net.url import percent_encode
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


class AddressBar:
    """주소창의 글자와 커서.

    커서는 글자 사이의 자리다. 0 부터 `len(text)` 까지 `len+1` 개가 있다.
    """

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
        if self.cursor < len(self.text):
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


# ---------------------------------------------------------------------- #
# 스크롤 애니메이션
# ---------------------------------------------------------------------- #

class ScrollAnimation:
    """방향키 스크롤을 한 칸에 툭 옮기지 않고 부드럽게."""

    def __init__(self, start, end, num_frames=SCROLL_FRAMES, easing=None):
        self.start = start
        self.end = end
        self.num_frames = max(1, num_frames)
        self.frame = 0
        self.easing = easing or EASINGS["ease-out"]

    def done(self):
        return self.frame >= self.num_frames

    def animate(self):
        if self.done():
            return None
        self.frame += 1
        t = self.easing(self.frame / self.num_frames)
        return self.start + (self.end - self.start) * t

    def retarget(self, end):
        """스크롤 중에 또 누르면 목표만 바꾼다."""
        self.end = end
        self.frame = 0


class FlingAnimation:
    """터치에서 손을 뗀 뒤의 관성. 마찰로 잦아든다."""

    def __init__(self, scroll, velocity, max_scroll,
                 friction=FLING_FRICTION):
        self.scroll = scroll
        self.velocity = velocity
        self.max_scroll = max_scroll
        self.friction = friction

    def done(self):
        return abs(self.velocity) < FLING_MIN_SPEED

    def animate(self):
        if self.done():
            return None
        self.scroll += self.velocity
        self.velocity *= self.friction
        if self.scroll <= 0:
            self.scroll, self.velocity = 0, 0
        elif self.scroll >= self.max_scroll:
            self.scroll, self.velocity = self.max_scroll, 0
        return self.scroll


# ---------------------------------------------------------------------- #
# 포커스 링의 자리
# ---------------------------------------------------------------------- #

def focus_rects(document, node):
    """이 요소를 덮는 사각형들.

    블록 요소는 자기 상자가 있지만 `<a>` 같은 인라인은 없다. 그럴 때는 자손
    글자 상자들을 **같은 줄끼리** 묶어 줄마다 사각형을 하나씩 만든다.
    """
    from wbe.frame import _layout_objects
    from wbe.layout.boxes import BlockLayout, LineLayout
    from wbe.layout.embed import EmbedLayout

    objects = _layout_objects(document)
    boxes = [o for o in objects
             if getattr(o, "node", None) is node
             and isinstance(o, (BlockLayout, EmbedLayout))]
    if boxes:
        return [o.self_rect() for o in boxes]

    words = [o for o in objects
             if isinstance(o, TextLayout) and is_descendant(o.node, node)]
    lines = {}
    for word in words:
        lines.setdefault(round(word.y), []).append(word)
    out = []
    for _, group in sorted(lines.items()):
        out.append(Rect(min(w.x for w in group),
                        min(w.y for w in group),
                        max(w.x + w.width for w in group),
                        max(w.y + w.height for w in group)))
    return out


# ---------------------------------------------------------------------- #
# 탭
# ---------------------------------------------------------------------- #

class Tab:
    def __init__(self, browser=None, tab_height=HEIGHT, speaker=None,
                 network=None, measure=None, task_runner=None):
        self.browser = browser
        self.tab_height = tab_height
        self.width = None
        self.measure = measure or MeasureTime()
        self.task_runner = task_runner or TaskRunner(self, self.measure)
        self.network = network or NetworkThread(None, self.measure)
        self.speaker = speaker

        self.root_frame = None
        self.focused_frame = None
        self.tab_order_focus = None
        self.url = None

        self.zoom = 1.0
        self.dark_mode = False
        self.forced_colors = False

        self.needs_render = False
        self.needs_layout = False
        self.needs_paint = False

        self.display_list = []
        self.flat_display_list = []
        self.document = None

        self.accessibility_tree = None
        self.accessibility_focus = None
        self.needs_accessibility = True

    # ------------------------------------------------------------------ #
    # 읽기
    # ------------------------------------------------------------------ #

    def load(self, url, payload=None, record=True):
        from wbe.frame import Frame
        self.root_frame = Frame(self, None, None)
        self.root_frame.width = self.width or self.frame_width()
        self.root_frame.height = self.tab_height
        self.root_frame.load(url, payload, record)
        self.url = url
        self.focused_frame = self.root_frame
        self.tab_order_focus = None
        self.render()

    def frame_width(self):
        from wbe.paint.geometry import WIDTH
        return WIDTH

    def frames(self):
        return self.root_frame.all_frames() if self.root_frame else []

    @property
    def js(self):
        return self.root_frame.js if self.root_frame else None

    @property
    def nodes(self):
        return self.root_frame.nodes if self.root_frame else None

    @property
    def scroll(self):
        return self.root_frame.scroll if self.root_frame else 0

    @scroll.setter
    def scroll(self, value):
        if self.root_frame:
            self.root_frame.scroll = value

    # ------------------------------------------------------------------ #
    # 렌더 예약
    # ------------------------------------------------------------------ #

    def set_needs_render(self):
        self.needs_render = True
        self.request_animation_frame()

    def set_needs_layout(self):
        self.needs_layout = True
        self.set_needs_render()

    def set_needs_paint(self):
        self.needs_paint = True
        self.set_needs_render()

    def request_animation_frame(self):
        if self.browser is not None:
            self.browser.set_needs_animation_frame(self)

    def render(self):
        if self.root_frame is None:
            return False
        self.measure.time("render")
        self.root_frame.layout()
        self.document = self.root_frame.document
        self.display_list = list(self.root_frame.display_list)
        self.flat_display_list = flatten(self.display_list)
        if self.accessibility_focus is not None:
            self.paint_reading_highlight()
        self.needs_render = self.needs_layout = self.needs_paint = False
        self.needs_accessibility = True
        self.measure.stop("render")
        return True

    def run_animation_frame(self, scroll=None):
        """한 프레임. 스크롤 애니메이션 → rAF 핸들러 → 애니메이션 → 렌더."""
        frame = self.root_frame
        if frame is None:
            return None
        if scroll is not None:
            frame.scroll = scroll
        if frame.scroll_animation is not None:
            value = frame.scroll_animation.animate()
            if value is None:
                frame.scroll_animation = None
            else:
                frame.scroll = value
                self.needs_paint = True
        for f in self.frames():
            if f.js is not None:
                f.js.run_raf_handlers()
            if run_animations(tree_to_list(f.nodes), self):
                self.needs_paint = True
        self.render()
        return CommitData(self.url, frame.scroll,
                          self.document.height if self.document else 0,
                          self.display_list)

    # ------------------------------------------------------------------ #
    # 클릭과 키
    # ------------------------------------------------------------------ #

    def node_at(self, x, y, frame=None):
        frame = frame or self.root_frame
        return hit_test(self.display_list, x, y + frame.scroll)

    def frame_at(self, node):
        """이 노드를 담고 있는 프레임."""
        for frame in self.frames():
            if frame.nodes is not None and is_descendant(node, frame.nodes):
                return frame
        return self.root_frame

    def click(self, x, y):
        node = self.node_at(x, y)
        if node is None:
            for frame in self.frames():
                frame.blur()
            return None
        frame = self.frame_at(node)
        self.focused_frame = frame
        for other in self.frames():
            if other is not frame:
                other.blur()

        target = node if isinstance(node, Element) else node.parent
        walk = target
        while walk is not None and not is_focusable(walk):
            walk = walk.parent
        if walk is not None:
            # 클릭으로 얻은 포커스는 링을 보여 주지 않는다
            frame.focus_element(walk, visible=False)
        else:
            frame.blur()

        if frame.js is not None and isinstance(target, Element) \
                and frame.js.dispatch_event("click", target):
            return None                  # preventDefault

        while node is not None:
            if isinstance(node, Text):
                pass
            elif node.tag == "a" and "href" in node.attributes:
                from wbe.net.url import resolve
                return self.follow(frame, resolve(frame.url,
                                                  node.attributes["href"]))
            elif node.tag == "input":
                if is_checkbox(node):
                    if "checked" in node.attributes:
                        del node.attributes["checked"]
                    else:
                        node.attributes["checked"] = ""
                else:
                    node.attributes["value"] = ""
                mark_style_dirty(node)
                frame.restyle()
                self.render()
                return None
            elif node.tag == "button":
                out = frame.submit_form(node)
                self.render()
                return out
            node = node.parent
        return None

    def follow(self, frame, url):
        if frame.url is not None and url.same_page(frame.url) and url.fragment:
            # 같은 페이지면 다시 읽지 않고 스크롤만 한다
            frame.history.visit(url)
            frame.url = url
            frame.scroll_to(url.fragment)
            self.render()
            return url
        frame.load(url)
        self.render()
        return url

    def keypress(self, char):
        frame = self.focused_frame or self.root_frame
        if frame is None or frame.focus is None:
            return False
        if frame.js is not None and \
                frame.js.dispatch_event("keydown", frame.focus):
            return True
        frame.focus.attributes["value"] = \
            frame.focus.attributes.get("value", "") + char
        mark_style_dirty(frame.focus)
        frame.restyle()
        self.render()
        return True

    def backspace(self):
        frame = self.focused_frame or self.root_frame
        if frame is None or frame.focus is None:
            return False
        value = frame.focus.attributes.get("value", "")
        frame.focus.attributes["value"] = value[:-1]
        mark_style_dirty(frame.focus)
        frame.restyle()
        self.render()
        return True

    def enter(self):
        """입력란 안에서 Enter 는 그 폼을 낸다."""
        frame = self.focused_frame or self.root_frame
        if frame is None or frame.focus is None:
            return None
        out = frame.submit_form(frame.focus)
        self.render()
        return out

    def hover(self, x, y):
        node = self.node_at(x, y)
        element = node if isinstance(node, Element) else \
            (node.parent if node is not None else None)
        frame = self.frame_at(element) if element is not None \
            else self.root_frame
        if not frame.hover(element):
            return False
        self.render()
        return True

    # ------------------------------------------------------------------ #
    # 포커스 옮기기
    # ------------------------------------------------------------------ #

    def advance_tab(self):
        """탭 키. 프레임을 넘나들며 다음 포커스 대상으로."""
        order = frame_tab_order(self.root_frame)
        nxt = next_focus(order, self.tab_order_focus)
        if nxt is None:
            return None
        self.tab_order_focus = nxt
        frame, node = nxt
        for other in self.frames():
            if other is not frame:
                other.blur()
        frame.focus_element(node, visible=True)
        self.focused_frame = frame
        self.render()
        return node

    # ------------------------------------------------------------------ #
    # 방문 기록
    # ------------------------------------------------------------------ #

    def last_navigated_frame(self):
        """가장 최근에 이동한, 뒤로 갈 곳이 있는 프레임."""
        best, best_time = None, -1
        for frame in self.frames():
            if not frame.history.can_back():
                continue
            if frame.nav_serial >= best_time:
                best, best_time = frame, frame.nav_serial
        return best

    def go_back(self, confirm_resubmit=None):
        frame = self.last_navigated_frame()
        if frame is None:
            return None
        entry = frame.history.back()
        if entry is None:
            return None
        if entry.is_post() and not (confirm_resubmit
                                    and confirm_resubmit(entry)):
            frame.history.forward()      # 되돌린다
            return None
        frame.load(entry.url, entry.body if entry.is_post() else None,
                   record=False)
        self.render()
        return entry.url

    def go_forward(self, confirm_resubmit=None):
        frame = self.focused_frame or self.root_frame
        if frame is None or not frame.history.can_forward():
            return None
        entry = frame.history.forward()
        if entry.is_post() and not (confirm_resubmit
                                    and confirm_resubmit(entry)):
            frame.history.back()
            return None
        frame.load(entry.url, entry.body if entry.is_post() else None,
                   record=False)
        self.render()
        return entry.url

    # ------------------------------------------------------------------ #
    # 스크롤
    # ------------------------------------------------------------------ #

    def scrollable_at(self, x, y):
        """그 자리에서 스크롤을 받을 요소. 없으면 None."""
        from wbe.css.style import is_scrollable
        node = self.node_at(x, y)
        while node is not None:
            if isinstance(node, Element) and is_scrollable(node):
                return node
            node = node.parent
        return None

    def scroll_by(self, delta, target=None):
        """스크롤 상자가 지정되면 그것을, 아니면 페이지를 움직인다."""
        frame = self.focused_frame or self.root_frame
        if target is not None:
            height = parse_px_value(target.style.get("height", ""), 0)
            inner = _content_height(self.document, target)
            top = getattr(target, "scroll_offset", 0)
            target.scroll_offset = max(
                0, min(top + delta, max(0, inner - height)))
            self.set_needs_paint()
            self.render()
            return True
        frame.scroll = max(0, min(frame.scroll + delta, frame.max_scroll()))
        return False

    def smooth_scroll_by(self, delta):
        frame = self.focused_frame or self.root_frame
        target = max(0, min(frame.scroll + delta, frame.max_scroll()))
        if frame.scroll_animation is not None:
            frame.scroll_animation.retarget(target)
        else:
            frame.scroll_animation = ScrollAnimation(frame.scroll, target)
        self.set_needs_paint()
        return target

    def fling(self, velocity):
        frame = self.focused_frame or self.root_frame
        frame.scroll_animation = FlingAnimation(frame.scroll, velocity,
                                                frame.max_scroll())
        self.set_needs_paint()

    def scrolldown(self):
        self.scroll_by(SCROLL_STEP)

    def scrollup(self):
        self.scroll_by(-SCROLL_STEP)

    # ------------------------------------------------------------------ #
    # 확대 · 다크 모드 · 고대비
    # ------------------------------------------------------------------ #

    def zoom_by(self, factor):
        self.zoom = max(MIN_ZOOM, min(self.zoom * factor, MAX_ZOOM))
        self.restyle_all()
        return self.zoom

    def reset_zoom(self):
        self.zoom = 1.0
        self.restyle_all()

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.restyle_all()
        return self.dark_mode

    def toggle_forced_colors(self):
        self.forced_colors = not self.forced_colors
        self.restyle_all()
        return self.forced_colors

    def restyle_all(self):
        for frame in self.frames():
            frame.styled_width = None
            frame.restyle_all()
        self.render()

    def resize(self, width, height):
        self.width = width
        self.tab_height = height
        if self.root_frame is None:
            return
        self.root_frame.width = width
        self.root_frame.height = height
        self.render()

    # ------------------------------------------------------------------ #
    # 제목과 접근성
    # ------------------------------------------------------------------ #

    def title(self):
        if self.nodes is not None:
            for node in tree_to_list(self.nodes):
                if isinstance(node, Element) and node.tag == "title":
                    text = "".join(c.text for c in node.children
                                   if isinstance(c, Text)).strip()
                    if text:
                        return text
        return str(self.url) if self.url else "새 탭"

    def build_accessibility(self):
        self.accessibility_tree = build_accessibility_tree(self.nodes)
        if self.document is not None:
            self.accessibility_tree.compute_bounds(self.document)
        self.needs_accessibility = False
        return self.accessibility_tree

    def accessibility_nodes(self):
        if self.accessibility_tree is None or self.needs_accessibility:
            self.build_accessibility()
        return self.accessibility_tree.flatten()

    def speak(self, text):
        if self.speaker is not None:
            self.speaker.speak(text)

    def speak_node(self, node):
        for a11y in self.accessibility_nodes():
            if a11y.node is node:
                self.speak(a11y.text())
                return
        if isinstance(node, Element):
            self.speak(role_of(node))

    def speak_document(self):
        for a11y in self.accessibility_nodes():
            self.speak(a11y.text())

    def advance_accessibility(self):
        """한 노드씩 옮기며 읽고 그 자리를 강조한다."""
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
        self.speak(nxt.text())
        self.render()
        return nxt

    def reading_highlight(self):
        if self.accessibility_focus is None:
            return []
        return self.accessibility_focus.bounds

    def paint_reading_highlight(self):
        for rect in self.reading_highlight():
            self.display_list.insert(
                0, DrawRect(rect, READING_HIGHLIGHT,
                            self.accessibility_focus.node))
        self.flat_display_list = flatten(self.display_list)

    def __repr__(self):
        return "Tab(%s)" % self.url


def _content_height(document, node):
    """그 요소 안쪽 내용의 실제 높이."""
    from wbe.frame import _layout_objects
    from wbe.layout.boxes import BlockLayout
    for obj in _layout_objects(document):
        if getattr(obj, "node", None) is node and isinstance(obj, BlockLayout):
            return sum(c.height for c in obj.children)
    return 0
