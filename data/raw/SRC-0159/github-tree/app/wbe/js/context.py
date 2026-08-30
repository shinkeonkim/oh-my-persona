"""자바스크립트 문맥.

프레임마다 하나씩 있다. DOM 노드는 **핸들**(정수)로 오간다. 자바스크립트
쪽에서 노드를 붙잡고 있어도 파이썬 객체가 새어 나가지 않게 하기 위해서다.

DOM 을 건드리는 메서드는 모두 `changed()` 를 지난다. 거기서 id 전역 변수를
맞추고, 스타일을 다시 입히고, 다시 그리도록 표시한다.
"""

import os
import re
import threading

import dukpy

from wbe.css.parser import CSSParser
from wbe.css.style import mark_style_dirty, mark_subtree_dirty
from wbe.dom.nodes import Element, Text, tree_to_list
from wbe.dom.parser import HTMLParser
from wbe.dom.serialize import serialize, serialize_children
from wbe.layout.embed import CanvasContext
from wbe.net import cookies as cookiejar
from wbe.net.security import cors_allows
from wbe.net.url import resolve

HERE = os.path.dirname(os.path.abspath(__file__))
RUNTIME_JS = open(os.path.join(HERE, "runtime.js"), encoding="utf8").read()

SETTIMEOUT_JS = "__runSetTimeout(dukpy.handle)"
SETINTERVAL_JS = "__runSetInterval(dukpy.handle)"
XHR_ONLOAD_JS = "__runXHROnload(dukpy.out, dukpy.handle)"
RAF_JS = "__runRAFHandlers()"
DISPATCH_JS = "__dispatch(dukpy.handles, dukpy.type)"
MESSAGE_JS = "__runWindowMessage(dukpy.data, dukpy.origin)"

IDENTIFIER = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*$")
RESERVED = {
    "break", "case", "catch", "class", "const", "continue", "debugger",
    "default", "delete", "do", "else", "export", "extends", "finally",
    "for", "function", "if", "import", "in", "instanceof", "new", "return",
    "super", "switch", "this", "throw", "try", "typeof", "var", "void",
    "while", "with", "yield", "let", "static", "enum", "await", "implements",
    "package", "protected", "interface", "private", "public", "null", "true",
    "false", "document", "console", "window", "Node", "Event", "LISTENERS",
}

EXPORTED = (
    "log", "querySelectorAll", "getAttribute", "setAttribute",
    "style_get", "style_set", "style_set_property",
    "innerHTML_get", "innerHTML_set", "outerHTML_get",
    "getChildren", "getParent", "ancestors",
    "createElement", "createTextNode",
    "appendChild", "insertBefore", "removeChild", "replaceChildren",
    "focus", "blur_element",
    "setTimeout", "clearTimeout", "setInterval", "clearInterval",
    "requestAnimationFrame", "XMLHttpRequest_send",
    "cookie_get", "cookie_set",
    "canvas_fill_style", "canvas_fill_rect", "canvas_fill_text",
    "canvas_clear", "post_message",
)


def origin_matches(target_origin, frame_origin):
    """`postMessage` 의 대상 출처가 맞는가."""
    if target_origin in (None, "", "*"):
        return True
    return target_origin.rstrip("/") == (frame_origin or "").rstrip("/")


class JSContext:
    def __init__(self, frame):
        self.frame = frame
        self.tab = frame.tab
        self.node_to_handle = {}
        self.handle_to_node = {}
        self.id_globals = {}
        self.interval_handles = set()
        self.discarded = False

        self.interp = dukpy.JSInterpreter()
        for name in EXPORTED:
            self.interp.export_function(name, getattr(self, name))
        self.interp.evaljs(RUNTIME_JS + "\n0;")

    # ------------------------------------------------------------------ #
    # 실행
    # ------------------------------------------------------------------ #

    def run(self, script, code):
        # 마지막 문장의 값은 쓰지 않는다. 그 값을 돌려받으려 하면
        # x.onload = function(){...} 처럼 함수로 끝나는 흔한 스크립트가
        # 멀쩡히 실행되고도 직렬화 오류로 보고된다.
        try:
            return self.interp.evaljs(code + "\n0;")
        except dukpy.JSRuntimeError as e:
            print("스크립트", script, "가 죽었습니다:", e)

    def log(self, *args):
        print(*args)

    # ------------------------------------------------------------------ #
    # 핸들
    # ------------------------------------------------------------------ #

    def get_handle(self, node):
        if node not in self.node_to_handle:
            handle = len(self.node_to_handle)
            self.node_to_handle[node] = handle
            self.handle_to_node[handle] = node
        return self.node_to_handle[node]

    def node(self, handle):
        return self.handle_to_node[handle]

    @property
    def nodes(self):
        return self.frame.nodes

    # ------------------------------------------------------------------ #
    # 조회
    # ------------------------------------------------------------------ #

    def querySelectorAll(self, selector_text):
        selector = CSSParser(selector_text).selector()
        if hasattr(selector, "prepare"):
            selector.prepare(self.nodes)
        return [self.get_handle(node) for node in tree_to_list(self.nodes)
                if selector.matches(node)]

    def getAttribute(self, handle, attr):
        return self.node(handle).attributes.get(attr, "") or ""

    def setAttribute(self, handle, attr, value):
        node = self.node(handle)
        node.attributes[attr] = value
        mark_style_dirty(node)
        self.changed()
        return value

    def getChildren(self, handle):
        """`Node.children` — 글자 마디는 빼고 요소만."""
        return [self.get_handle(child)
                for child in self.node(handle).children
                if isinstance(child, Element)]

    def getParent(self, handle):
        parent = self.node(handle).parent
        return self.get_handle(parent) if parent is not None else -1

    def ancestors(self, handle):
        """대상부터 뿌리까지. 이벤트 버블링이 쓴다."""
        out, node = [], self.node(handle)
        while node is not None:
            out.append(self.get_handle(node))
            node = node.parent
        return out

    # ------------------------------------------------------------------ #
    # 트리 고치기
    # ------------------------------------------------------------------ #

    def createElement(self, tag):
        return self.get_handle(Element(tag.casefold(), {}, None))

    def createTextNode(self, text):
        return self.get_handle(Text(text, None))

    def detach(self, node):
        if node.parent is not None and node in node.parent.children:
            node.parent.children.remove(node)
        node.parent = None

    def appendChild(self, parent_handle, child_handle):
        parent, child = self.node(parent_handle), self.node(child_handle)
        mark_style_dirty(parent)
        self.detach(child)
        parent.children.append(child)
        child.parent = parent
        self.attach_resources(child)
        self.changed()
        return child_handle

    def insertBefore(self, parent_handle, child_handle, ref_handle):
        parent, child = self.node(parent_handle), self.node(child_handle)
        mark_style_dirty(parent)
        self.detach(child)
        if ref_handle is None or ref_handle < 0:
            parent.children.append(child)
        else:
            ref = self.node(ref_handle)
            parent.children.insert(parent.children.index(ref), child)
        child.parent = parent
        self.attach_resources(child)
        self.changed()
        return child_handle

    def removeChild(self, parent_handle, child_handle):
        """떼어 내면 그 서브트리는 문서 밖으로 나간다. 다시 붙일 수 있다."""
        parent, child = self.node(parent_handle), self.node(child_handle)
        if child.parent is not parent:
            raise Exception("removeChild: 자식이 아닙니다")
        mark_style_dirty(parent)
        self.detach_resources(child)
        parent.children.remove(child)
        child.parent = None
        self.changed()
        return child_handle

    def replaceChildren(self, handle, child_handles):
        """인자가 없으면 비우고, 있으면 그것들로 갈아 끼운다."""
        parent = self.node(handle)
        children = [self.node(h) for h in (child_handles or [])]

        for child in list(parent.children):
            self.detach_resources(child)
        parent.children = []

        for child in children:
            if child.parent is not None and child in child.parent.children:
                child.parent.children.remove(child)
                mark_style_dirty(child.parent)
            child.parent = parent
            parent.children.append(child)
            self.attach_resources(child)

        mark_subtree_dirty(parent)
        self.changed()
        return handle

    # ------------------------------------------------------------------ #
    # innerHTML 과 style
    # ------------------------------------------------------------------ #

    def innerHTML_get(self, handle):
        return serialize_children(self.node(handle))

    def outerHTML_get(self, handle):
        return serialize(self.node(handle))

    def innerHTML_set(self, handle, s):
        elt = self.node(handle)
        mark_style_dirty(elt)
        for child in elt.children:
            self.detach_resources(child)
        doc = HTMLParser("<html><body>" + s + "</body></html>").parse()
        elt.children = doc.children[0].children
        for child in elt.children:
            child.parent = elt
            self.attach_resources(child)
        self.changed()

    def style_get(self, handle):
        return self.node(handle).attributes.get("style", "")

    def style_set(self, handle, text):
        node = self.node(handle)
        node.attributes["style"] = text
        mark_style_dirty(node)
        self.changed()
        return text

    def style_set_property(self, handle, prop, value):
        node = self.node(handle)
        decls = [d for d in node.attributes.get("style", "").split(";")
                 if d.strip() and d.split(":", 1)[0].strip() != prop]
        decls.append("%s: %s" % (prop, value))
        node.attributes["style"] = "; ".join(d.strip() for d in decls)
        mark_style_dirty(node)
        self.changed()
        return value

    # ------------------------------------------------------------------ #
    # 붙는 것과 떨어지는 것
    # ------------------------------------------------------------------ #

    def attach_resources(self, subtree):
        """새로 들어온 서브트리의 스크립트·스타일시트·이미지·프레임."""
        for node in tree_to_list(subtree):
            if not isinstance(node, Element):
                continue
            if node.tag == "script":
                self.frame.run_script(node)
            elif node.tag == "link" and "href" in node.attributes \
                    and node.attributes.get("rel") == "stylesheet":
                self.frame.add_stylesheet(node)
            elif node.tag == "iframe":
                self.frame.load_iframe(node)
            elif node.tag == "img":
                self.frame.load_image(node)
            elif node.tag == "canvas":
                node.canvas_context = CanvasContext(node)

    def detach_resources(self, subtree):
        """나가는 서브트리의 스타일시트 규칙과 자식 프레임을 뺀다."""
        for node in tree_to_list(subtree):
            if not isinstance(node, Element):
                continue
            if node.tag == "link":
                self.frame.remove_stylesheet(node)
            elif node.tag == "iframe":
                self.frame.unload_iframe(node)

    # ------------------------------------------------------------------ #
    # id 전역 변수
    # ------------------------------------------------------------------ #

    def usable_id(self, name):
        return bool(IDENTIFIER.match(name)) and name not in RESERVED

    def update_id_globals(self):
        """id 를 가진 요소마다 같은 이름의 전역 변수를 맞춘다."""
        current = {}
        for node in tree_to_list(self.nodes):
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
        """DOM 이 바뀌었다."""
        self.update_id_globals()
        self.frame.restyle()
        self.frame.layout()
        if self.tab is not None:
            self.tab.set_needs_paint()

    # ------------------------------------------------------------------ #
    # 이벤트
    # ------------------------------------------------------------------ #

    def dispatch_event(self, type, node):
        """대상에서 조상 순서로 핸들러를 부른다. preventDefault 면 True."""
        handles = self.ancestors(self.get_handle(node))
        do_default = self.interp.evaljs(DISPATCH_JS, handles=handles,
                                        type=type)
        return not do_default

    def focus(self, handle):
        self.frame.focus_element(self.node(handle), visible=True)
        return handle

    def blur_element(self, handle):
        if self.frame.tab_focus is self.node(handle):
            self.frame.focus_element(None)
        return handle

    # ------------------------------------------------------------------ #
    # 타이머
    # ------------------------------------------------------------------ #

    def schedule(self, fn, *args, name="타이머"):
        from wbe.scheduling import PRIORITY_TIMER, Task
        runner = self.tab.task_runner if self.tab is not None else None
        task = Task(fn, *args, priority=PRIORITY_TIMER, name=name,
                    measure=self.tab.measure if self.tab else None)
        if runner is not None:
            runner.schedule_task(task)
        else:
            task.run()

    def dispatch_settimeout(self, handle):
        if not self.discarded:
            self.interp.evaljs(SETTIMEOUT_JS, handle=handle)

    def setTimeout(self, handle, delay):
        timer = threading.Timer(
            delay / 1000.0,
            lambda: self.schedule(self.dispatch_settimeout, handle,
                                  name="setTimeout"))
        timer.daemon = True
        timer.start()
        return handle

    def clearTimeout(self, handle):
        return handle

    def dispatch_setinterval(self, handle, delay):
        if self.discarded or handle not in self.interval_handles:
            return
        again = self.interp.evaljs(SETINTERVAL_JS, handle=handle)
        if again and handle in self.interval_handles:
            self.arm_interval(handle, delay)

    def arm_interval(self, handle, delay):
        def fire():
            if handle in self.interval_handles:
                self.schedule(self.dispatch_setinterval, handle, delay,
                              name="setInterval")
        timer = threading.Timer(delay / 1000.0, fire)
        timer.daemon = True
        timer.start()

    def setInterval(self, handle, delay):
        self.interval_handles.add(handle)
        self.arm_interval(handle, delay)
        return handle

    def clearInterval(self, handle):
        self.interval_handles.discard(handle)
        return handle

    def requestAnimationFrame(self):
        if self.tab is not None:
            self.tab.request_animation_frame()

    def run_raf_handlers(self):
        self.interp.evaljs(RAF_JS)

    # ------------------------------------------------------------------ #
    # 네트워크
    # ------------------------------------------------------------------ #

    def dispatch_xhr_onload(self, out, handle):
        if not self.discarded:
            self.interp.evaljs(XHR_ONLOAD_JS, out=out, handle=handle)

    def XMLHttpRequest_send(self, method, url, body, is_async=False,
                            handle=None):
        full_url = resolve(self.frame.url, url)
        cross_origin = full_url.origin() != self.frame.origin()
        if not self.frame.allowed_request(full_url):
            raise Exception("콘텐츠 보안 정책이 %s 를 막았습니다" % full_url)

        def do_request():
            out = full_url.request(
                referrer=self.frame.url,
                payload=body if method.upper() == "POST" else None,
                origin=self.frame.origin() if cross_origin else None,
                referrer_policy=self.frame.referrer_policy,
                top_level=not cross_origin)
            if cross_origin and not cors_allows(full_url.response_headers,
                                                self.frame.origin()):
                # 요청은 나갔지만 서버가 허락하지 않았으므로 결과를 버린다
                raise Exception("교차 출처 요청이 허용되지 않았습니다")
            return out

        if not is_async:
            return do_request()

        from wbe.scheduling import PRIORITY_DEFAULT, Task

        def run_load():
            out = do_request()
            self.tab.task_runner.schedule_task(
                Task(self.dispatch_xhr_onload, out, handle,
                     priority=PRIORITY_DEFAULT, name="XHR onload",
                     measure=self.tab.measure))

        self.tab.network.schedule_task(
            Task(run_load, priority=PRIORITY_DEFAULT, name="XHR send",
                 measure=self.tab.measure))
        return ""

    # ------------------------------------------------------------------ #
    # 쿠키
    # ------------------------------------------------------------------ #

    def cookie_get(self):
        host = getattr(self.frame.url, "host", None)
        if not host:
            return ""
        return cookiejar.cookie_header(host, script_visible=True) or ""

    def cookie_set(self, text):
        host = getattr(self.frame.url, "host", None)
        if host:
            cookiejar.store_cookie(host, text)
        return text

    # ------------------------------------------------------------------ #
    # 캔버스
    # ------------------------------------------------------------------ #

    def context_of(self, handle):
        node = self.node(handle)
        if node.canvas_context is None:
            node.canvas_context = CanvasContext(node)
        return node.canvas_context

    def canvas_fill_style(self, handle, color):
        self.context_of(handle).setFillStyle(color)
        return color

    def canvas_fill_rect(self, handle, x, y, w, h):
        self.context_of(handle).fillRect(x, y, w, h)
        self.changed()

    def canvas_fill_text(self, handle, text, x, y):
        self.context_of(handle).fillText(text, x, y)
        self.changed()

    def canvas_clear(self, handle):
        self.context_of(handle).clear()
        self.changed()

    # ------------------------------------------------------------------ #
    # 프레임 사이의 메시지
    # ------------------------------------------------------------------ #

    def post_message(self, message, target_origin="*"):
        parent = self.frame.parent_frame
        if parent is None or parent.js is None:
            return 0
        if not origin_matches(target_origin, parent.origin()):
            return 0            # 대상 출처가 아니면 조용히 버린다
        return parent.js.deliver_message(message, self.frame.origin())

    def deliver_message(self, message, origin):
        return self.interp.evaljs(MESSAGE_JS, data=message,
                                  origin=origin or "")
