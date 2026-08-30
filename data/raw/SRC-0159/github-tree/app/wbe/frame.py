"""프레임 — 문서 하나.

최상위 문서도, `<iframe>` 안의 문서도 모두 `Frame` 이다. 프레임마다 자기
URL·트리·자바스크립트 문맥·스크롤 위치·방문 기록·포커스를 갖는다.
"""

import itertools

from wbe.a11y import focusable_nodes
from wbe.animation import parse_keyframes
from wbe.css.parser import CSSParser
from wbe.css.style import (force_colors, mark_style_dirty, style_incremental)
from wbe.css.selectors import cascade_priority, prepare_selectors
from wbe.css.values import parse_url_value
from wbe.dom.nodes import Element, Text, tree_to_list
from wbe.dom.parser import parse_document
from wbe.js.context import JSContext
from wbe.layout.boxes import DocumentLayout
from wbe.layout.embed import CanvasContext, decode_image, is_lazy
from wbe.net import cookies as cookiejar
from wbe.net.security import (CertificateError, allowed_by_csp,
                              frame_allowed, parse_csp,
                              referrer_policy_of)
from wbe.net.url import URL, form_encode, resolve
from wbe.paint.effects import paint_tree
from wbe.paint.geometry import HEIGHT, WIDTH
from wbe.stylesheets import BROWSER_CSS

# 어느 프레임이 가장 최근에 이동했는지 재는 번호표
NAV_SERIAL = itertools.count()

BLOCKED_PAGE = ("<html><body><h1>이 페이지는 프레임 안에 넣을 수 없습니다</h1>"
                "</body></html>")


def error_page(title, url, detail):
    """읽지 못한 페이지 자리에 보여 줄 문서."""
    from wbe.dom.serialize import escape_text
    return ("<html><head><title>%s</title></head><body><h1>%s</h1>"
            "<p>%s</p><p>%s</p></body></html>"
            % (escape_text(title), escape_text(title),
               escape_text(str(url)), escape_text(str(detail))))

# 방문한 주소. 링크를 보라색으로 칠하는 데 쓴다.
VISITED = set()


class HistoryEntry:
    """어떤 메서드로 갔는지 기억한다. `POST` 로 갔던 곳은 다시 물어봐야 한다."""

    def __init__(self, url, method="GET", body=None):
        self.url = url
        self.method = method
        self.body = body

    def is_post(self):
        return self.method == "POST"

    def __repr__(self):
        return "%s %s" % (self.method, self.url)


class History:
    def __init__(self):
        self.past = []
        self.future = []

    def visit(self, url, method="GET", body=None):
        self.past.append(HistoryEntry(url, method, body))
        self.future.clear()          # 새로 이동하면 앞으로 갈 곳은 사라진다

    def can_back(self):
        return len(self.past) > 1

    def can_forward(self):
        return len(self.future) > 0

    def back(self):
        """돌아갈 곳을 돌려준다 (지금 있는 곳이 아니라)."""
        if not self.can_back():
            return None
        self.future.append(self.past.pop())
        return self.past[-1]

    def forward(self):
        if not self.can_forward():
            return None
        entry = self.future.pop()
        self.past.append(entry)
        return entry

    def current(self):
        return self.past[-1] if self.past else None


class Frame:
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
        self.scroll_animation = None
        self.focus = None                 # 글자를 받는 입력란
        self.tab_focus = None             # 포커스 링이 붙은 요소
        self.hovered = None
        self.width = WIDTH
        self.height = HEIGHT
        self.styled_width = None
        self.base_rules = []
        self.link_rules = {}
        self.link_bodies = {}
        self.keyframes = {}
        self.history = History()
        self.children = []
        self.blocked = False
        self.allowed_origins = None       # 콘텐츠 보안 정책
        self.referrer_policy = None
        self.insecure = False
        self.nav_serial = -1
        self.style_stats = []
        self.paint_stats = {"repainted": 0, "reused": 0}

    # ------------------------------------------------------------------ #
    # 정체
    # ------------------------------------------------------------------ #

    def origin(self):
        return self.url.origin() if self.url is not None else None

    def all_frames(self, out=None):
        out = [] if out is None else out
        out.append(self)
        for child in self.children:
            child.all_frames(out)
        return out

    def zoom(self):
        return self.tab.zoom if self.tab is not None else 1.0

    def allowed_request(self, url):
        return allowed_by_csp(self.allowed_origins, url)

    # ------------------------------------------------------------------ #
    # 읽기
    # ------------------------------------------------------------------ #

    def load(self, url, payload=None, record=True):
        parent_origin = self.parent_frame.origin() if self.parent_frame \
            else None
        self.insecure = False
        try:
            body = url.request(referrer=self.url, payload=payload,
                               referrer_policy=self.referrer_policy)
        except CertificateError as e:
            body = error_page("이 사이트의 인증서를 믿을 수 없습니다", url, e)
            self.insecure = True
            url.response_headers = {}
        except Exception as e:
            # 페이지 하나를 못 읽었다고 브라우저가 멈추면 안 된다.
            # 오류를 페이지로 보여 주고 계속 간다.
            body = error_page("페이지를 열 수 없습니다", url, e)
            url.response_headers = {}

        headers = getattr(url, "response_headers", {}) or {}
        if self.parent_frame is not None and \
                not frame_allowed(headers, parent_origin, url.origin()):
            self.blocked = True
            body = BLOCKED_PAGE
        else:
            self.blocked = False

        self.url = url
        if record:
            self.history.visit(url, "POST" if payload is not None else "GET",
                               payload)
            self.nav_serial = next(NAV_SERIAL)
        VISITED.add(url.base_str())

        self.allowed_origins = parse_csp(headers.get("content-security-policy"))
        self.referrer_policy = referrer_policy_of(headers)

        self.nodes = parse_document(body, url.view_source)
        self.keyframes = {}
        for node in tree_to_list(self.nodes):
            if isinstance(node, Element) and node.tag == "style":
                text = "".join(c.text for c in node.children
                               if isinstance(c, Text))
                self.keyframes.update(parse_keyframes(text))

        self.js = JSContext(self)
        self.load_resources()
        self.mark_visited_links()
        self.styled_width = None
        self.restyle()
        self.js.update_id_globals()

        for node in tree_to_list(self.nodes):
            if isinstance(node, Element) and node.tag == "script" \
                    and "src" not in node.attributes:
                self.run_script(node)

        self.scroll = 0
        self.layout()
        if url.fragment:
            self.scroll_to(url.fragment)

    # -- 딸린 자원 ------------------------------------------------------ #

    def sub_request(self, url):
        """스크립트나 스타일시트 하나 가져오기. 정책에 막히면 None."""
        if not self.allowed_request(url):
            print("콘텐츠 보안 정책이", url, "를 막았습니다")
            return None
        try:
            return url.request(referrer=self.url,
                               referrer_policy=self.referrer_policy)
        except Exception:
            return None

    def load_resources(self):
        """스타일시트와 스크립트를 병렬로 받고, 처리는 소스 순서로.

        네트워크는 동시에 열되 결과는 원래 목록 순서대로 처리한다. 그래야
        나중에 도착한 스타일시트가 앞선 것을 이기지 않는다.
        """
        from wbe.scheduling import parallel_fetch

        links, scripts = [], []
        for node in tree_to_list(self.nodes):
            if not isinstance(node, Element):
                continue
            if node.tag == "link" and "href" in node.attributes \
                    and node.attributes.get("rel") == "stylesheet":
                links.append(node)
            elif node.tag == "script" and "src" in node.attributes:
                scripts.append(node)
            elif node.tag == "img":
                self.load_image(node)
            elif node.tag == "canvas":
                node.canvas_context = CanvasContext(node)
            elif node.tag == "iframe":
                self.load_iframe(node)

        def fetch(node):
            attr = "href" if node.tag == "link" else "src"
            return self.sub_request(resolve(self.url, node.attributes[attr]))

        bodies, _ = parallel_fetch(links + scripts, fetch)
        for node, body in zip(links, bodies[:len(links)]):
            if body is not None:
                self.link_bodies[node] = body
        for node, body in zip(scripts, bodies[len(links):]):
            if body:
                self.js.run(node.attributes["src"], body)

    def run_script(self, node):
        src = node.attributes.get("src")
        if src:
            code = self.sub_request(resolve(self.url, src))
            if code is None:
                return
        else:
            code = "".join(c.text for c in node.children
                           if isinstance(c, Text))
        if code.strip():
            self.js.run(src or "인라인 스크립트", code)

    def add_stylesheet(self, node, restyle=True):
        body = self.sub_request(resolve(self.url, node.attributes["href"]))
        if body is None:
            return
        self.link_bodies[node] = body
        self.link_rules[node] = CSSParser(body, self.media()).parse()
        if restyle:
            self.restyle()

    def remove_stylesheet(self, node):
        self.link_bodies.pop(node, None)
        if self.link_rules.pop(node, None) is not None:
            self.restyle()

    def load_image(self, node, force=False):
        node.image = None
        if is_lazy(node) and not force:
            node.image_pending = True
            return
        node.image_pending = False
        src = node.attributes.get("src")
        if not src:
            return
        try:
            node.image = decode_image(
                resolve(self.url, src).request_bytes())
        except Exception:
            node.image = None

    def load_background(self, node):
        node.background_image = None
        src = parse_url_value(node.style.get("background-image"))
        if not src:
            return
        try:
            node.background_image = decode_image(
                resolve(self.url, src).request_bytes())
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
        child = node.frame
        if child is None:
            return
        if child in self.children:
            self.children.remove(child)
        if child.js is not None:
            child.js.discarded = True
        node.frame = None

    def mark_visited_links(self):
        """방문한 `<a>` 에 visited 클래스를 붙인다.

        그리기 코드를 건드릴 필요가 없다. 기본 스타일시트의
        `a.visited { color: purple }` 이 나머지를 한다.
        """
        for node in tree_to_list(self.nodes):
            if not isinstance(node, Element) or node.tag != "a":
                continue
            href = node.attributes.get("href")
            if not href:
                continue
            try:
                target = resolve(self.url, href)
            except Exception:
                continue
            if target.base_str() not in VISITED:
                continue
            classes = node.attributes.get("class", "").split()
            if "visited" not in classes:
                classes.append("visited")
            node.attributes["class"] = " ".join(classes)

    # ------------------------------------------------------------------ #
    # 스타일과 배치
    # ------------------------------------------------------------------ #

    def media(self):
        """지금의 미디어 상태. 확대하면 CSS 픽셀 너비가 줄어든다."""
        tab = self.tab
        return {
            "prefers-color-scheme":
                "dark" if tab is not None and tab.dark_mode else "light",
            "forced-colors": bool(tab is not None and tab.forced_colors),
            "width": self.width / self.zoom(),
        }

    def sheet_texts(self):
        texts = [BROWSER_CSS]
        for node in tree_to_list(self.nodes):
            if isinstance(node, Element) and node.tag == "style":
                texts.append("".join(c.text for c in node.children
                                     if isinstance(c, Text)))
        return texts

    def rebuild_rules(self):
        """미디어 쿼리 결과가 바뀔 수 있으므로 원문에서 다시 읽는다."""
        media = self.media()
        self.base_rules = []
        for text in self.sheet_texts():
            self.base_rules.extend(CSSParser(text, media).parse())
        for node, body in self.link_bodies.items():
            self.link_rules[node] = CSSParser(body, media).parse()

    def all_rules(self):
        rules = list(self.base_rules)
        for extra in self.link_rules.values():
            rules.extend(extra)
        rules.sort(key=cascade_priority)
        return rules

    def restyle(self):
        self.rebuild_rules()
        rules = self.all_rules()
        prepare_selectors(rules, self.nodes)
        self.style_stats = style_incremental(self.nodes, rules, self.tab,
                                             self.keyframes)
        if self.tab is not None and self.tab.forced_colors:
            force_colors(tree_to_list(self.nodes))
        for node in tree_to_list(self.nodes):
            if isinstance(node, Element) \
                    and node.style.get("background-image"):
                self.load_background(node)

    def restyle_all(self):
        from wbe.css.style import mark_subtree_dirty
        mark_subtree_dirty(self.nodes)
        self.restyle()

    def layout(self):
        if self.nodes is None:
            return
        if self.styled_width != self.width:
            # 너비가 바뀌면 미디어 쿼리 결과도 바뀐다
            self.restyle_all()
            self.styled_width = self.width
        self.document = DocumentLayout(self.nodes, self)
        self.document.layout(self.width)
        self.display_list = []
        self.paint_stats = paint_tree(self.document, self.display_list)

    # ------------------------------------------------------------------ #
    # 포커스
    # ------------------------------------------------------------------ #

    def focusable(self):
        return focusable_nodes(tree_to_list(self.nodes))

    def focus_element(self, node, visible=True):
        old = self.tab_focus
        if old is not None:
            old.is_focused = False
            old.focus_visible = False
            mark_style_dirty(old)
            self.dispatch_focus_event("blur", old)
        self.tab_focus = node
        self.focus = node if node is not None and node.tag == "input" else None
        if node is not None:
            node.is_focused = True
            node.focus_visible = visible
            mark_style_dirty(node)
            self.dispatch_focus_event("focus", node)
            if self.tab is not None:
                self.tab.speak_node(node)
        self.restyle()

    def blur(self):
        if self.tab_focus is not None:
            self.focus_element(None)

    def dispatch_focus_event(self, name, node):
        if self.js is not None:
            self.js.dispatch_event(name, node)

    def hover(self, node):
        """마우스가 올라온 요소만 다시 스타일링한다."""
        if node is self.hovered:
            return False
        if self.hovered is not None:
            self.hovered.is_hovered = False
            mark_style_dirty(self.hovered)
        self.hovered = node
        if node is not None:
            node.is_hovered = True
            mark_style_dirty(node)
        self.restyle()
        return True

    # ------------------------------------------------------------------ #
    # 스크롤
    # ------------------------------------------------------------------ #

    def max_scroll(self):
        from wbe.paint.geometry import VSTEP
        if self.document is None:
            return 0
        return max(self.document.height + 2 * VSTEP - self.height, 0)

    def scroll_to(self, fragment):
        """그 id 를 가진 요소를 화면 맨 위로."""
        from wbe.dom.nodes import Element as El
        from wbe.paint.geometry import VSTEP
        for obj in _layout_objects(self.document):
            node = getattr(obj, "node", None)
            if isinstance(node, El) and \
                    node.attributes.get("id") == fragment:
                self.scroll = max(0, min(obj.y - VSTEP, self.max_scroll()))
                return True
        return False

    # ------------------------------------------------------------------ #
    # 폼
    # ------------------------------------------------------------------ #

    def form_for(self, node):
        while node is not None:
            if isinstance(node, Element) and node.tag == "form" \
                    and "action" in node.attributes:
                return node
            node = node.parent
        return None

    def form_pairs(self, form):
        """제출할 이름=값 쌍. 체크박스는 체크된 것만 실린다."""
        from wbe.layout.embed import input_type
        pairs = []
        for node in tree_to_list(form):
            if not isinstance(node, Element) or node.tag != "input":
                continue
            if "name" not in node.attributes:
                continue
            type_ = input_type(node)
            if type_ in ("submit", "button"):
                continue
            if type_ == "checkbox":
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
        if self.js is not None and self.js.dispatch_event("submit", form):
            return None
        body = form_encode(self.form_pairs(form))
        url = resolve(self.url, form.attributes["action"])
        method = form.attributes.get("method", "post").casefold()
        if method == "get":
            target = url.with_query(body)     # GET 제출에는 본문이 없다
            self.load(target)
            return target
        self.load(url, payload=body)
        return url

    def __repr__(self):
        return "Frame(%s)" % self.url


def _layout_objects(obj, out=None):
    out = [] if out is None else out
    if obj is None:
        return out
    out.append(obj)
    for child in obj.children:
        _layout_objects(child, out)
    if getattr(obj, "inner", None) is not None:
        _layout_objects(obj.inner, out)
    return out
