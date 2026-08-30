"""선택자.

우선순위는 태그 1 < 클래스 10 < id 100 이고, 붙여 쓰거나 자손으로 이으면
합이 된다. `!important` 는 +10000 으로 얹는다.
"""

from wbe.dom.nodes import Element, tree_to_list

IMPORTANT_BONUS = 10000
PSEUDOCLASS_PRIORITY = 10
PSEUDOCLASSES = {"focus", "focus-visible", "hover"}


class TagSelector:
    def __init__(self, tag):
        self.tag = tag
        self.priority = 1

    def matches(self, node):
        return isinstance(node, Element) and self.tag == node.tag

    def __repr__(self):
        return self.tag


class ClassSelector:
    def __init__(self, cls):
        self.cls = cls
        self.priority = 10

    def matches(self, node):
        if not isinstance(node, Element):
            return False
        return self.cls in node.attributes.get("class", "").split()

    def __repr__(self):
        return "." + self.cls


class IdSelector:
    def __init__(self, id_):
        self.id = id_
        self.priority = 100

    def matches(self, node):
        return isinstance(node, Element) \
            and node.attributes.get("id") == self.id

    def __repr__(self):
        return "#" + self.id


class SelectorSequence:
    """붙여 쓴 선택자들 — `span.announce`. 우선순위는 합."""

    def __init__(self, selectors):
        self.selectors = selectors
        self.priority = sum(s.priority for s in selectors)

    def matches(self, node):
        return all(s.matches(node) for s in self.selectors)

    def __repr__(self):
        return "".join(repr(s) for s in self.selectors)


class DescendantSelector:
    """`div p` — 조상들을 목록으로 들고 사슬을 한 번만 거슬러 올라간다.

    안쪽부터 맞춰 보며 조상을 한 칸씩 올리므로 O(n + d) 다. 선택자마다
    사슬을 처음부터 다시 훑으면 O(n·d) 가 된다.
    """

    def __init__(self, selectors):
        self.selectors = selectors           # 바깥 -> 안쪽 순서
        self.priority = sum(s.priority for s in selectors)

    def matches(self, node):
        if not self.selectors[-1].matches(node):
            return False
        i = len(self.selectors) - 2
        ancestor = node.parent
        while i >= 0 and ancestor:
            if self.selectors[i].matches(ancestor):
                i -= 1
            ancestor = ancestor.parent
        return i < 0

    def __repr__(self):
        return " ".join(repr(s) for s in self.selectors)


class HasSelector:
    """`a:has(b)` — 자손 b 가 있는 a.

    매칭 때마다 서브트리를 뒤지면 전체가 O(n²) 이 된다. 대신 스타일을 입히기
    전에 트리를 한 번 훑어 조건을 만족하는 조상을 모두 표시해 둔다. 이미
    표시된 조상을 만나면 멈추므로 준비 단계가 O(n), 요소당 상각 O(1) 이다.
    """

    def __init__(self, base, inner):
        self.base = base
        self.inner = inner
        self.priority = base.priority + inner.priority
        self.satisfied = None

    def prepare(self, root):
        self.satisfied = set()
        for node in tree_to_list(root):
            if not self.inner.matches(node):
                continue
            ancestor = node.parent
            while ancestor is not None:
                if id(ancestor) in self.satisfied:
                    break            # 위쪽은 이미 표시돼 있다
                self.satisfied.add(id(ancestor))
                ancestor = ancestor.parent

    def matches(self, node):
        if self.satisfied is None:
            return False
        return self.base.matches(node) and id(node) in self.satisfied

    def __repr__(self):
        return "%r:has(%r)" % (self.base, self.inner)


class PseudoclassSelector:
    """`:focus`, `:focus-visible`, `:hover`.

    `:focus` 와 `:focus-visible` 은 다르다. 클릭으로 얻은 포커스도 포커스지만
    (키 입력이 거기로 간다) 링은 보여 주지 않는다.
    """

    def __init__(self, pseudoclass, base):
        self.pseudoclass = pseudoclass
        self.base = base
        # 의사 클래스는 클래스와 같은 무게를 갖는다. 그래야 div:hover 가
        # 같은 자리의 div 규칙을 이긴다.
        self.priority = base.priority + PSEUDOCLASS_PRIORITY

    def matches(self, node):
        if not self.base.matches(node):
            return False
        if self.pseudoclass == "focus":
            return getattr(node, "is_focused", False)
        if self.pseudoclass == "focus-visible":
            return getattr(node, "is_focused", False) \
                and getattr(node, "focus_visible", False)
        if self.pseudoclass == "hover":
            return getattr(node, "is_hovered", False)
        return False

    def prepare(self, root):
        if hasattr(self.base, "prepare"):
            self.base.prepare(root)

    def __repr__(self):
        return "%r:%s" % (self.base, self.pseudoclass)


class ImportantSelector:
    """같은 선언을 우선순위만 올려 한 번 더 적용한다."""

    def __init__(self, base):
        self.base = base
        self.priority = base.priority + IMPORTANT_BONUS

    def matches(self, node):
        return self.base.matches(node)

    def prepare(self, root):
        if hasattr(self.base, "prepare"):
            self.base.prepare(root)

    def __repr__(self):
        return "%r!important" % self.base


def cascade_priority(rule):
    selector, body = rule
    return selector.priority


def prepare_selectors(rules, root):
    """`:has` 처럼 미리 계산이 필요한 선택자를 준비시킨다."""
    for selector, _ in rules:
        if hasattr(selector, "prepare"):
            selector.prepare(root)
