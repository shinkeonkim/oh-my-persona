"""배치 트리를 훑어 그리기 명령을 만든다.

`paint_tree` 는 상자마다 만든 명령을 캐시해 두고, 자기도 자손도 더럽지
않으면 그대로 내놓는다. 한 곳이 바뀌어도 그 가지만 다시 그린다.
"""

from wbe.css.style import is_scrollable, z_index
from wbe.css.values import (parse_blur, parse_outline, parse_px_value)
from wbe.paint.commands import Blend, DrawOutline, DrawRRect, Transform
from wbe.paint.geometry import Rect

# 포커스 링은 두 겹이다. 바깥 흰 굵은 선이 어떤 배경 위에서도 대비를 만든다.
FOCUS_OUTER_COLOR = "white"
FOCUS_INNER_COLOR = "black"
FOCUS_OUTER_WIDTH = 4
FOCUS_INNER_WIDTH = 2


def border_radius(node):
    return parse_px_value(node.style.get("border-radius", "0px"))


def paint_visual_effects(node, cmds, rect):
    """한 요소의 시각 효과를 안쪽부터 바깥쪽으로 씌운다."""
    opacity = float(node.style.get("opacity", "1.0"))
    blend_mode = node.style.get("mix-blend-mode")
    blur = parse_blur(node.style.get("filter"))
    overflow = node.style.get("overflow", "visible")
    radius = border_radius(node)
    translation = None
    from wbe.css.values import parse_transform
    translation = parse_transform(node.style.get("transform"))

    if is_scrollable(node):
        cmds = [Transform((0, -getattr(node, "scroll_offset", 0)), cmds, node)]

    if overflow in ("clip", "scroll"):
        # destination-in 으로 둥근 사각형 밖을 지운다
        if not blend_mode:
            blend_mode = "source-over"
        cmds = cmds + [Blend(1.0, "destination-in",
                             [DrawRRect(rect, radius, "white", node)], node)]

    out = [Blend(opacity, blend_mode, cmds, node, blur)]
    if translation:
        out = [Transform(translation, out, node)]
    return out


def paint_outline(node, cmds, rects, zoom=1.0):
    """포커스 링. 인라인이 여러 줄에 걸치면 사각형마다 하나씩."""
    width, color = parse_outline(node.style.get("outline"))
    if not width:
        return cmds
    for rect in rects:
        outer = Rect(rect.left - FOCUS_OUTER_WIDTH / 2,
                     rect.top - FOCUS_OUTER_WIDTH / 2,
                     rect.right + FOCUS_OUTER_WIDTH / 2,
                     rect.bottom + FOCUS_OUTER_WIDTH / 2)
        cmds.append(DrawOutline(outer, FOCUS_OUTER_COLOR,
                                FOCUS_OUTER_WIDTH * zoom, node))
        cmds.append(DrawOutline(rect, color or FOCUS_INNER_COLOR,
                                FOCUS_INNER_WIDTH * zoom, node))
    return cmds


# ---------------------------------------------------------------------- #
# 트리 훑기
# ---------------------------------------------------------------------- #

def mark_paint_dirty(layout_object):
    """이 상자와 그 위로 뿌리까지 다시 그려야 한다고 표시한다."""
    obj = layout_object
    while obj is not None:
        if getattr(obj, "needs_paint", False) and \
                getattr(obj, "has_dirty_paint_descendants", False):
            return
        obj.needs_paint = True
        obj.has_dirty_paint_descendants = True
        obj = obj.parent


def paint_tree(layout_object, display_list, stats=None):
    """더러운 상자만 다시 그리고 나머지는 지난번 명령을 그대로 쓴다."""
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

    children = layout_object.children
    if any(z_index(getattr(c, "node", None)) for c in children):
        children = sorted(children,
                          key=lambda c: z_index(getattr(c, "node", None)))
    for child in children:
        paint_tree(child, cmds, stats)

    if layout_object.should_paint():
        cmds = layout_object.paint_effects(cmds)

    stats["repainted"] += 1
    layout_object.painted = cmds
    layout_object.needs_paint = False
    layout_object.has_dirty_paint_descendants = False
    display_list.extend(cmds)
    return stats
