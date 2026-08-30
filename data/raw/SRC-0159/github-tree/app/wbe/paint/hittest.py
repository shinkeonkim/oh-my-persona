"""히트 테스팅.

좌표를 절대 좌표로 **올리는** 대신 트리를 따라 **내리면서** 변환을 거꾸로
적용한다. 변환이 중첩돼도 자연스럽게 이어진다.
"""

from wbe.paint.commands import Transform, is_effect
from wbe.paint.effects import border_radius
from wbe.paint.commands import DrawRRect
from wbe.paint.geometry import inside_rounded


def hit(cmd, x, y):
    """이 그리기 명령이 그 점을 실제로 덮는가."""
    radius = 0.0
    if isinstance(cmd, DrawRRect):
        radius = cmd.radius
    elif cmd.node is not None and getattr(cmd.node, "style", None):
        radius = border_radius(cmd.node)
    return inside_rounded(cmd.rect, radius, x, y)


def hit_test(display_list, x, y):
    """맨 위에 있는, 그 점을 덮는 그리기 명령의 노드."""
    found = [None]

    def walk(items, px, py):
        for item in items:
            if is_effect(item):
                local_x, local_y = px, py
                if isinstance(item, Transform):
                    local_x -= item.dx
                    local_y -= item.dy
                walk(item.children, local_x, local_y)
            elif item.node is not None and hit(item, px, py):
                found[0] = item.node

    walk(display_list, x, y)
    return found[0]
