"""화면 좌표와 사각형."""

import math

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

# 스크롤할 때마다 페이지 전체를 다시 그리지 않도록, 화면 둘레 이만큼만
# 래스터해 둔다.
AOI_HEIGHT = 4 * HEIGHT


class Rect:
    __slots__ = ("left", "top", "right", "bottom")

    def __init__(self, left, top, right, bottom):
        self.left, self.top = left, top
        self.right, self.bottom = right, bottom

    def contains_point(self, x, y):
        return self.left <= x < self.right and self.top <= y < self.bottom

    def overlaps(self, other):
        return not (self.right <= other.left or other.right <= self.left
                    or self.bottom <= other.top or other.bottom <= self.top)

    def union(self, other):
        return Rect(min(self.left, other.left), min(self.top, other.top),
                    max(self.right, other.right),
                    max(self.bottom, other.bottom))

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.bottom - self.top

    def __repr__(self):
        return "Rect(%g, %g, %g, %g)" % (self.left, self.top,
                                         self.right, self.bottom)


EMPTY_RECT = Rect(0, 0, 0, 0)


def union_of(children):
    """그리기 명령들을 모두 감싸는 사각형."""
    if not children:
        return Rect(0, 0, 0, 0)
    left = min(c.rect.left for c in children)
    top = min(c.rect.top for c in children)
    right = max(c.rect.right for c in children)
    bottom = max(c.rect.bottom for c in children)
    return Rect(left, top, right, bottom)


def map_translation(rect, translation, reverse=False):
    if translation is None:
        return rect
    dx, dy = translation
    if reverse:
        dx, dy = -dx, -dy
    return Rect(rect.left + dx, rect.top + dy,
                rect.right + dx, rect.bottom + dy)


def inside_rounded(rect, radius, x, y):
    """둥근 모서리를 고려한 판정.

    화면에는 둥근 사각형을 그려 놓고 클릭 판정은 직사각형으로 하면 깎여 나간
    모서리를 눌러도 맞은 것이 된다. 네 모서리 구역만 따로 보고 중심에서의
    거리를 잰다.
    """
    if not rect.contains_point(x, y):
        return False
    if radius <= 0:
        return True
    r = min(radius, rect.width / 2, rect.height / 2)
    for cx, cy in ((rect.left + r, rect.top + r),
                   (rect.right - r, rect.top + r),
                   (rect.left + r, rect.bottom - r),
                   (rect.right - r, rect.bottom - r)):
        in_x = (x < cx) if cx == rect.left + r else (x > cx)
        in_y = (y < cy) if cy == rect.top + r else (y > cy)
        if in_x and in_y:
            return math.hypot(x - cx, y - cy) <= r
    return True


def skia_rect(rect):
    import skia
    return skia.Rect.MakeLTRB(rect.left, rect.top, rect.right, rect.bottom)
