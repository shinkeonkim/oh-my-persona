"""스타일 적용 — 캐스케이드, 상속, 증분 재계산.

`style_incremental` 은 더러운 가지만 훑는다. 노드를 더럽힐 때
`mark_style_dirty` 가 조상들에게 "아래에 더러운 게 있다"고 알려 두므로,
깨끗한 가지를 만나면 즉시 되돌아설 수 있다.
"""

from wbe.animation import apply_animations
from wbe.css.parser import CSSParser
from wbe.dom.nodes import Element, tree_to_list

INHERITED_PROPERTIES = {
    "font-size": "16px",
    "font-style": "normal",
    "font-weight": "normal",
    "font-family": "",
    "color": "black",
}

# 고대비 모드에서 색을 눌러 덮을 값들
FORCED_COLORS = {
    "color": "#ffffff",
    "background-color": "#000000",
    "link": "#00ffff",
    "outline": "#ffff00",
}


# ---------------------------------------------------------------------- #
# 더티 플래그
# ---------------------------------------------------------------------- #

def mark_style_dirty(node):
    node.needs_style = True
    parent = node.parent
    while parent is not None and not getattr(
            parent, "has_dirty_style_descendants", False):
        parent.has_dirty_style_descendants = True
        parent = parent.parent


def mark_subtree_dirty(node):
    for descendant in tree_to_list(node):
        mark_style_dirty(descendant)


# ---------------------------------------------------------------------- #
# 캐스케이드
# ---------------------------------------------------------------------- #

def style_one(node, rules):
    """한 노드에만 캐스케이드를 적용한다. 자식으로 내려가지 않는다."""
    node.style = {}
    for prop, default in INHERITED_PROPERTIES.items():
        node.style[prop] = node.parent.style[prop] if node.parent else default

    for selector, body in rules:
        if not selector.matches(node):
            continue
        for prop, value in body.items():
            node.style[prop] = value

    if isinstance(node, Element) and "style" in node.attributes:
        normal, important = CSSParser(node.attributes["style"]).body()
        for prop, value in {**normal, **important}.items():
            node.style[prop] = value

    if node.style["font-size"].endswith("%"):
        parent_size = (node.parent.style["font-size"] if node.parent
                       else INHERITED_PROPERTIES["font-size"])
        pct = float(node.style["font-size"][:-1]) / 100
        node.style["font-size"] = str(pct * float(parent_size[:-2])) + "px"


def style_incremental(node, rules, tab=None, keyframes=None, visited=None):
    """더러운 곳만 훑는다. 다시 계산한 노드 목록을 돌려준다."""
    visited = [] if visited is None else visited
    needs = getattr(node, "needs_style", True)
    below = getattr(node, "has_dirty_style_descendants", True)
    if not needs and not below:
        return visited

    visited.append(node)
    if needs:
        old_style = node.style if node.style else None
        style_one(node, rules)
        apply_animations(node, old_style, tab, keyframes)
        node.needs_style = False
        # 상속 때문에 부모가 바뀌면 자식도 다시 봐야 한다
        for child in node.children:
            mark_style_dirty(child)

    for child in node.children:
        style_incremental(child, rules, tab, keyframes, visited)
    node.has_dirty_style_descendants = False
    return visited


def style(node, rules, tab=None, keyframes=None):
    """트리 전체를 다시 스타일링한다."""
    mark_subtree_dirty(node)
    return style_incremental(node, rules, tab, keyframes)


# ---------------------------------------------------------------------- #
# 계산된 값 읽기
# ---------------------------------------------------------------------- #

def is_block(node):
    """블록인가 인라인인가. 하드코딩 목록 대신 display 속성을 본다."""
    from wbe.dom.nodes import Text
    if isinstance(node, Text):
        return False
    return node.style.get("display", "inline") == "block"


def is_skipped(node):
    """화면에 나오지 않는 요소. 트리에는 남아 있다."""
    return isinstance(node, Element) and \
        node.tag in ("head", "script", "style")


def z_index(node):
    """`position` 이 `static` 이면 `z-index` 는 듣지 않는다."""
    if not isinstance(node, Element):
        return 0
    if node.style.get("position", "static") == "static":
        return 0
    try:
        return int(node.style.get("z-index", "0"))
    except ValueError:
        return 0


def is_scrollable(node):
    """`overflow: scroll` 이고 높이가 정해진 요소."""
    from wbe.css.values import parse_px_value
    return node.style.get("overflow", "visible") == "scroll" \
        and parse_px_value(node.style.get("height", ""), 0) > 0


def effective_zoom(node, base=1.0):
    """조상들의 `zoom` 을 모두 곱한다."""
    from wbe.css.values import parse_zoom
    chain = []
    while node is not None:
        if isinstance(node, Element):
            chain.append(node)
        node = node.parent
    zoom = base
    for element in reversed(chain):
        zoom *= parse_zoom(element.style.get("zoom"))
    return zoom


def force_colors(nodes):
    """고대비 모드 — 색을 몇 개의 대비 좋은 색으로 눌러 덮는다."""
    from wbe.css.values import parse_outline
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
