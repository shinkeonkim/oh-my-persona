"""접근성 — 접근성 트리, 포커스 순서, 낭독.

말하기 뒷단은 갈아 끼울 수 있다. 시험할 때는 `RecordingSpeaker` 를 넣어
소리 없이 무엇을 말했는지 확인한다.
"""

import shutil
import subprocess
import threading

from wbe.dom.nodes import Element, Text, inner_text, tree_to_list

FOCUSABLE_TAGS = ("input", "button", "a")

ROLES = {
    "a": "link", "input": "textbox", "button": "button",
    "html": "document", "img": "image", "h1": "heading",
    "h2": "heading", "h3": "heading", "h4": "heading",
    "h5": "heading", "h6": "heading", "ul": "list", "ol": "list",
    "li": "listitem", "nav": "navigation", "canvas": "image",
    "iframe": "document",
}

READING_HIGHLIGHT = "#ffff88"


# ---------------------------------------------------------------------- #
# 포커스
# ---------------------------------------------------------------------- #

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
    return sorted(focusable, key=lambda n: (get_tabindex(n), nodes.index(n)))


def frame_tab_order(root_frame):
    """모든 프레임의 포커스 대상을 프레임 순서대로 이어 붙인 목록."""
    out = []
    for frame in root_frame.all_frames():
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
# 접근성 트리
# ---------------------------------------------------------------------- #

def role_of(node):
    if isinstance(node, Text):
        return "StaticText"
    explicit = node.attributes.get("role")
    return explicit if explicit else ROLES.get(node.tag, "none")


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
            return "링크: %s" % inner_text(self.node)
        if self.role == "textbox":
            from wbe.layout.embed import display_value
            name = self.node.attributes.get("name", "입력란")
            return "%s 입력란, 값 %s" % (name, display_value(self.node))
        if self.role == "button":
            return "버튼: %s" % inner_text(self.node)
        if self.role == "heading":
            return "제목: %s" % inner_text(self.node)
        if self.role == "document":
            return "문서"
        return "%s: %s" % (self.role, inner_text(self.node))

    def compute_bounds(self, document):
        from wbe.tab import focus_rects
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
# 말하기
# ---------------------------------------------------------------------- #

class Speaker:
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
    """macOS 의 내장 음성 합성기를 그대로 쓴다."""

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
    """pyttsx3 로 소리 내어 읽는다."""

    def __init__(self):
        import pyttsx3
        self.engine = pyttsx3.init()

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()


def default_speaker():
    """쓸 수 있는 뒷단 중 가장 나은 것."""
    mac = MacSaySpeaker()
    if mac.available():
        return mac
    try:
        return PyttsxSpeaker()
    except Exception:
        return PrintSpeaker()


class AccessibilityThread:
    """말하기가 브라우저 스레드를 막지 않게 한다."""

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
