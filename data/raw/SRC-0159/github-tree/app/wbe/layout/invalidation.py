"""무효화 — 무엇을 다시 계산해야 하는가.

두 가지 방법을 담고 있다.

`ProtectedField` 는 값 하나마다 객체를 만든다. 읽고 쓰는 자리가 분명해
읽기 좋지만, 노드마다 수십 개씩 만들면 실제 브라우저에는 비싸다.

`FieldStore` 는 같은 의미를 객체 없이 낸다. 주인 하나에 딕셔너리 셋(값 ·
더티 집합 · 의존 관계)만 두고 필드를 이름으로 가리킨다.
"""


class DependencyError(Exception):
    """계산하기 전에 읽었거나, 밝히지 않은 의존에 기댔다."""


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
        parent = self.parent
        while parent is not None and not parent.has_dirty_descendants:
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


class FieldStore:
    """필드 객체를 하나도 만들지 않는 저장소.

    필드를 가리켜야 할 때는 `(저장소, 이름)` 튜플을 그때그때 만들었다
    버린다. `__slots__` 를 써서 인스턴스 딕셔너리조차 없다.
    """

    __slots__ = ("values", "dirty", "invalidations", "parent",
                 "has_dirty_descendants")

    def __init__(self, parent=None):
        self.values = {}
        self.dirty = set()
        self.invalidations = {}
        self.parent = parent
        self.has_dirty_descendants = False

    def declare(self, name):
        self.dirty.add(name)
        self.invalidations.setdefault(name, set())

    def is_dirty(self, name):
        return name in self.dirty

    def set_ancestor_dirty_flags(self):
        parent = self.parent
        while parent is not None and not parent.has_dirty_descendants:
            parent.has_dirty_descendants = True
            parent = parent.parent

    def mark(self, name):
        if name in self.dirty:
            return
        self.dirty.add(name)
        self.set_ancestor_dirty_flags()

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


def reconcile_children(old_children, new_nodes, make):
    """노드 목록에 맞춰 레이아웃 자식을 맞춘다.

    이미 있던 것은 그대로 쓰고 새 노드만 새로 만든다. 앞 형제가 바뀐 것만
    다시 배치하면 되므로 그 목록도 함께 돌려준다. 목록 끝에 붙이면 손대는
    자식이 하나, 앞에 끼워 넣으면 둘뿐이다.
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
            child.previous = previous
            changed.append(child)
        out.append(child)
        previous = child
    return out, changed
