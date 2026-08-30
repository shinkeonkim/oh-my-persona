"""16장 연습문제 구현 (16-1 ~ 16-10).

lab16.py 는 그대로 두고, 1~15장 연습문제를 이어받아 그 위에 16장 기능을 얹는다.

16장 본문 기능(ProtectedField, 의존성, 더티 플래그, 증분 스타일·레이아웃)에 더해

    16-1  요소 비우기           replaceChildren()
    16-2  레이아웃 단계 보호하기   document 자체를 보호 필드로
    16-3  자식 옮기기           replaceChildren(a, b, ...)
    16-4  style 을 위한 자손 플래그
    16-5  브라우저 크기 조절
    16-6  자식 매칭하기         appendChild 가 레이아웃을 다시 만들지 않게
    16-7  previous 무효화       insertBefore
    16-8  :hover 의사 클래스
    16-9  ProtectedField 없애기  필드 객체를 만들지 않는 저장소
    16-10 paint 최적화하기      디스플레이 리스트를 프레임 사이에 남긴다
"""

import sys

import ex6
import ex10
import ex11
import ex13
import ex14
import ex15
from ex4 import Text, Element
from ex6 import tree_to_list
from ex11 import Rect, DrawText, DrawRect, flatten, WIDTH, HEIGHT, HSTEP, VSTEP
from ex15 import Frame, Tab as Tab15, JSContext as JSContext15, resolve


class DependencyError(Exception):
    """읽지 않은 필드에 기대는 값을 계산하려 했다."""


# ---------------------------------------------------------------------- #
# 보호 필드
# ---------------------------------------------------------------------- #

class ProtectedField:
    """값 하나와 그 값이 누구에게 쓰였는지를 함께 들고 있는 상자."""

    def __init__(self, obj, name, parent=None, dependencies=None):
        self.obj = obj
        self.name = name
        self.parent = parent
        self.value = None
        self.dirty = True
        self.frozen_invalidations = dependencies is not None
        self.invalidations = set()
        if dependencies is not None:
            for field in dependencies:
                field.invalidations.add(self)

    def set_dependencies(self, dependencies):
        for field in dependencies:
            field.invalidations.add(self)
        self.frozen_invalidations = True

    def set_ancestor_dirty_flags(self):
        """연습문제 16-4: 조상들에게 '아래에 더러운 게 있다'고 알린다."""
        parent = self.parent
        while parent and not parent.has_dirty_descendants:
            parent.has_dirty_descendants = True
            parent = parent.parent

    def mark(self):
        if self.dirty:
            return
        self.dirty = True
        self.set_ancestor_dirty_flags()

    def notify(self):
        for field in self.invalidations:
            field.mark()
        self.set_ancestor_dirty_flags()

    def set(self, value):
        if value != self.value:
            self.notify()
        self.value = value
        self.dirty = False

    def get(self):
        if self.dirty:
            raise DependencyError("%s 를 계산하기 전에 읽었습니다" % self.name)
        return self.value

    def read(self, notify):
        """다른 필드가 이 값을 쓴다고 알리며 읽는다."""
        if notify is not None:
            if notify.frozen_invalidations:
                if notify not in self.invalidations:
                    raise DependencyError(
                        "%s 는 %s 에 기댄다고 미리 밝히지 않았습니다"
                        % (notify.name, self.name))
            else:
                self.invalidations.add(notify)
        return self.get()

    def copy(self, field):
        self.set(field.read(notify=self))

    def __repr__(self):
        return "ProtectedField(%s, dirty=%s)" % (self.name, self.dirty)


# ---------------------------------------------------------------------- #
# 연습문제 16-9: 필드 객체를 만들지 않는 저장소
# ---------------------------------------------------------------------- #

class FieldStore:
    """같은 의미를 객체 없이. 값·더티·의존을 주인 쪽 딕셔너리에 모아 둔다.

    노드마다 필드 객체를 수십 개씩 만드는 대신, 주인 하나에 딕셔너리 세 개만
    둔다. 필드를 가리킬 때는 (주인, 이름) 쌍을 쓴다 — 이것은 그때그때 만들었다
    버리는 튜플이라 오래 남지 않는다.
    """

    __slots__ = ("values", "dirty", "invalidations", "parent",
                 "has_dirty_descendants")

    def __init__(self, parent=None):
        self.values = {}
        self.dirty = set()
        self.invalidations = {}
        self.parent = parent
        self.has_dirty_descendants = False

    # -- 한 필드 다루기 ------------------------------------------------- #

    def declare(self, name):
        self.dirty.add(name)
        self.invalidations.setdefault(name, set())

    def is_dirty(self, name):
        return name in self.dirty

    def mark(self, name):
        if name in self.dirty:
            return
        self.dirty.add(name)
        self.set_ancestor_dirty_flags()

    def set_ancestor_dirty_flags(self):
        parent = self.parent
        while parent is not None and not parent.has_dirty_descendants:
            parent.has_dirty_descendants = True
            parent = parent.parent

    def notify(self, name):
        for store, other in self.invalidations.get(name, ()):
            store.mark(other)
        self.set_ancestor_dirty_flags()

    def set(self, name, value):
        if self.values.get(name) != value:
            self.notify(name)
        self.values[name] = value
        self.dirty.discard(name)

    def get(self, name):
        if name in self.dirty:
            raise DependencyError("%s 를 계산하기 전에 읽었습니다" % name)
        return self.values.get(name)

    def read(self, name, notify=None):
        if notify is not None:
            self.invalidations.setdefault(name, set()).add(notify)
        return self.get(name)

    def field_count(self):
        """만들어 둔 필드 '객체' 수. 언제나 0 이다."""
        return 0


# ---------------------------------------------------------------------- #
# 연습문제 16-6 / 16-7: 자식 레이아웃 객체 다시 쓰기
# ---------------------------------------------------------------------- #

def reconcile_children(old_children, new_nodes, make):
    """노드 목록에 맞춰 레이아웃 자식을 맞춘다.

    이미 있던 것은 그대로 쓰고, 새 노드만 새로 만든다. 앞 형제가 바뀐 것만
    다시 배치하면 되도록 그 목록도 함께 돌려준다.
    """
    by_node = {}
    for child in old_children:
        by_node.setdefault(id(child.node), []).append(child)

    out, changed, previous = [], [], None
    for node in new_nodes:
        bucket = by_node.get(id(node))
        child = bucket.pop(0) if bucket else None
        if child is None:
            child = make(node, previous)
            changed.append(child)
        elif child.previous is not previous:
            child.previous = previous       # 연습문제 16-7
            changed.append(child)
        out.append(child)
        previous = child
    return out, changed


# ---------------------------------------------------------------------- #
# 연습문제 16-4: style 을 위한 자손 플래그
# ---------------------------------------------------------------------- #

def mark_style_dirty(node):
    """이 노드의 스타일이 더러워졌다고 표시하고 조상들에게 알린다."""
    node.needs_style = True
    parent = node.parent
    while parent is not None and not getattr(parent, "has_dirty_style_descendants",
                                             False):
        parent.has_dirty_style_descendants = True
        parent = parent.parent


def mark_subtree_dirty(node):
    """이 노드와 그 아래를 모두 다시 스타일링하도록 표시한다."""
    for descendant in tree_to_list(node, []):
        mark_style_dirty(descendant)


def clear_style_flags(node):
    node.needs_style = False
    node.has_dirty_style_descendants = False


def style_incremental(node, rules, tab=None, keyframes=None, visited=None):
    """더러운 곳만 훑는다. 훑은 노드 수를 돌려준다."""
    visited = [] if visited is None else visited
    needs = getattr(node, "needs_style", True)
    below = getattr(node, "has_dirty_style_descendants", True)
    if not needs and not below:
        return visited
    visited.append(node)
    if needs:
        old_style = getattr(node, "style", None)
        _style_one(node, rules)
        ex13.apply_animations(node, old_style, tab, keyframes)
        node.needs_style = False
        for child in node.children:      # 부모가 바뀌면 상속도 다시
            mark_style_dirty(child)
    for child in node.children:
        style_incremental(child, rules, tab, keyframes, visited)
    node.has_dirty_style_descendants = False
    return visited


def _style_one(node, rules):
    """한 노드에만 캐스케이드를 적용한다 (자식으로 내려가지 않는다)."""
    node.style = {}
    for prop, default in ex6.INHERITED_PROPERTIES.items():
        node.style[prop] = node.parent.style[prop] if node.parent else default
    for selector, body in rules:
        if not selector.matches(node):
            continue
        for prop, value in body.items():
            node.style[prop] = value
    if isinstance(node, Element) and "style" in node.attributes:
        normal, important = ex15.CSSParser15(node.attributes["style"]).body()
        for prop, value in {**normal, **important}.items():
            node.style[prop] = value
    if node.style["font-size"].endswith("%"):
        parent_size = (node.parent.style["font-size"] if node.parent
                       else ex6.INHERITED_PROPERTIES["font-size"])
        pct = float(node.style["font-size"][:-1]) / 100
        node.style["font-size"] = str(pct * float(parent_size[:-2])) + "px"


# ---------------------------------------------------------------------- #
# 연습문제 16-10: 디스플레이 리스트를 프레임 사이에 남긴다
# ---------------------------------------------------------------------- #

def mark_paint_dirty(layout_object):
    obj = layout_object
    while obj is not None:
        if getattr(obj, "needs_paint", False) and \
                getattr(obj, "has_dirty_paint_descendants", False):
            return
        obj.needs_paint = True
        obj.has_dirty_paint_descendants = True
        obj = obj.parent


def paint_tree_cached(layout_object, display_list, stats=None):
    """더러운 상자만 다시 그리고, 나머지는 지난번 명령을 그대로 쓴다."""
    if stats is None:
        stats = {"repainted": 0, "reused": 0}
    needs = getattr(layout_object, "needs_paint", True)
    below = getattr(layout_object, "has_dirty_paint_descendants", True)
    cached = getattr(layout_object, "painted", None)

    if not needs and not below and cached is not None:
        stats["reused"] += 1
        display_list.extend(cached)
        return stats

    cmds = []
    if layout_object.should_paint():
        cmds = layout_object.paint()
    for child in layout_object.children:
        paint_tree_cached(child, cmds, stats)
    if layout_object.should_paint():
        cmds = layout_object.paint_effects(cmds)

    stats["repainted"] += 1
    layout_object.painted = cmds
    layout_object.needs_paint = False
    layout_object.has_dirty_paint_descendants = False
    display_list.extend(cmds)
    return stats


# ---------------------------------------------------------------------- #
# 자바스크립트 — replaceChildren 과 자식 옮기기
# ---------------------------------------------------------------------- #

RUNTIME_EXTRA = """
// 연습문제 16-1 / 16-3
Node.prototype.replaceChildren = function() {
    var handles = [];
    for (var i = 0; i < arguments.length; i++)
        handles.push(arguments[i].handle);
    call_python("replaceChildren", this.handle, handles);
    return undefined;
}
"""


class JSContext(JSContext15):
    RUNTIME = JSContext15.RUNTIME + RUNTIME_EXTRA

    def __init__(self, frame):
        super().__init__(frame)
        self.interp.export_function("replaceChildren", self.replaceChildren)

    # -- DOM 을 건드리면 그 자리만 더럽힌다 (연습문제 16-4) ------------- #

    # super() 안에서 곧바로 다시 스타일링하므로, 표시는 그 전에 해 둔다.

    def appendChild(self, parent_handle, child_handle):
        mark_style_dirty(self.node(parent_handle))
        return super().appendChild(parent_handle, child_handle)

    def insertBefore(self, parent_handle, child_handle, ref_handle):
        mark_style_dirty(self.node(parent_handle))
        return super().insertBefore(parent_handle, child_handle, ref_handle)

    def removeChild(self, parent_handle, child_handle):
        mark_style_dirty(self.node(parent_handle))
        return super().removeChild(parent_handle, child_handle)

    def innerHTML_set(self, handle, s):
        mark_style_dirty(self.node(handle))
        return super().innerHTML_set(handle, s)

    def setAttribute(self, handle, attr, value):
        mark_style_dirty(self.node(handle))
        return super().setAttribute(handle, attr, value)

    def replaceChildren(self, handle, child_handles):
        parent = self.node(handle)
        children = [self.node(h) for h in (child_handles or [])]

        for child in list(parent.children):        # 16-1
            self.detach_resources(child)
        parent.children = []

        for child in children:                     # 16-3: 옮겨 오기
            if child.parent is not None and child in child.parent.children:
                child.parent.children.remove(child)
                mark_style_dirty(child.parent)
            child.parent = parent
            parent.children.append(child)
            self.attach_resources(child)

        mark_style_dirty(parent)
        self.changed()
        return handle


# ---------------------------------------------------------------------- #
# 프레임 — 증분 스타일과 그리기
# ---------------------------------------------------------------------- #

class Frame16(Frame):
    def __init__(self, tab, parent_frame=None, frame_element=None):
        super().__init__(tab, parent_frame, frame_element)
        self.style_stats = []
        self.paint_stats = {"repainted": 0, "reused": 0}

    def restyle(self):
        self.rebuild_rules()
        rules = self.all_rules()
        if not hasattr(self.nodes, "needs_style"):
            for node in tree_to_list(self.nodes, []):
                mark_style_dirty(node)
        self.style_stats = style_incremental(self.nodes, rules, self.tab,
                                             self.keyframes)
        if self.tab is not None and self.tab.forced_colors:
            ex14.force_colors(tree_to_list(self.nodes, []))
        for node in tree_to_list(self.nodes, []):
            if isinstance(node, Element) \
                    and getattr(node, "style", {}).get("background-image"):
                self.load_background(node)

    def restyle_all(self):
        for node in tree_to_list(self.nodes, []):
            mark_style_dirty(node)
        self.restyle()

    def layout(self):
        if self.nodes is None:
            return
        if getattr(self, "styled_width", None) != self.width:
            self.restyle_all()
            self.styled_width = self.width
        self.document = ex15.DocumentLayout(self.nodes, self)
        self.document.layout(self.width)
        self.display_list = []
        self.paint_stats = paint_tree_cached(self.document, self.display_list)


# ---------------------------------------------------------------------- #
# 탭
# ---------------------------------------------------------------------- #

class Tab(Tab15):
    def make_js(self, frame):
        return JSContext(frame)

    def load(self, url, payload=None, record=True):
        self.root_frame = Frame16(self, None, None)
        self.root_frame.width = self.width if hasattr(self, "width") else WIDTH
        self.root_frame.height = self.tab_height
        self.root_frame.load(url, payload, record)
        self.url = url
        self.focused_frame = self.root_frame
        self.js = self.root_frame.js
        self.nodes = self.root_frame.nodes
        self.render()

    # -- 연습문제 16-5 -------------------------------------------------- #

    def resize(self, width, height):
        self.width = width
        self.tab_height = height
        if self.root_frame is None:
            return
        self.root_frame.width = width
        self.root_frame.height = height
        self.render()

    # -- 연습문제 16-8 -------------------------------------------------- #

    def hover(self, x, y):
        node = self.node_at(x, y)
        element = node if isinstance(node, Element) else \
            (node.parent if node is not None else None)
        if element is self.hovered:
            return False
        for old in (self.hovered,):
            if old is not None:
                old.is_hovered = False
                mark_style_dirty(old)
        self.hovered = element
        if element is not None:
            element.is_hovered = True
            mark_style_dirty(element)
        self.focused_frame.restyle()
        self.render()
        return True


def install():
    """15장 프레임을 16장 것으로 바꿔 끼운다."""
    ex15.Frame = Frame16
    ex15.JSContext = JSContext


install()


def main(argv):
    from ex16_sdl import run
    run(argv[0] if argv else ex11.HOME_URL)


if __name__ == "__main__":
    main(sys.argv[1:])
