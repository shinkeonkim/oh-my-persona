"""애니메이션 — 이징, 값 보간, 트랜지션, `@keyframes`.

애니메이션마다 `needs_layout` 이 있다. `opacity` 나 `transform` 은 그리기만
다시 하면 되지만 `width`/`height` 는 상자 크기가 바뀌므로 배치를 다시 해야
한다.
"""

from wbe.css.parser import parse_keyframes  # noqa: F401  (다시 내보낸다)
from wbe.css.values import parse_px_value, parse_rgb, parse_transform
from wbe.dom.nodes import Element

REFRESH_RATE_SEC = 0.033


# ---------------------------------------------------------------------- #
# 이징
# ---------------------------------------------------------------------- #

def cubic_bezier(x1, y1, x2, y2):
    """CSS 의 cubic-bezier. x 로부터 t 를 이분법으로 찾아 y 를 낸다."""

    def bezier(a, b, t):
        u = 1 - t
        return 3 * u * u * t * a + 3 * u * t * t * b + t * t * t

    def ease(x):
        if x <= 0:
            return 0.0
        if x >= 1:
            return 1.0
        lo, hi = 0.0, 1.0
        for _ in range(24):
            mid = (lo + hi) / 2
            if bezier(x1, x2, mid) < x:
                lo = mid
            else:
                hi = mid
        return bezier(y1, y2, (lo + hi) / 2)

    return ease


EASINGS = {
    "linear": lambda x: x,
    "ease": cubic_bezier(0.25, 0.1, 0.25, 1.0),
    "ease-in": cubic_bezier(0.42, 0.0, 1.0, 1.0),
    "ease-out": cubic_bezier(0.0, 0.0, 0.58, 1.0),
    "ease-in-out": cubic_bezier(0.42, 0.0, 0.58, 1.0),
}


def parse_easing(name):
    """이름이 없으면 CSS 기본값인 `ease` — 선형이 아니다."""
    if not name:
        return EASINGS["ease"]
    name = name.strip().casefold()
    if name in EASINGS:
        return EASINGS[name]
    if name.startswith("cubic-bezier(") and name.endswith(")"):
        try:
            nums = [float(p) for p in name[len("cubic-bezier("):-1].split(",")]
        except ValueError:
            return EASINGS["ease"]
        if len(nums) == 4:
            return cubic_bezier(*nums)
    return EASINGS["ease"]


# ---------------------------------------------------------------------- #
# 값 보간
# ---------------------------------------------------------------------- #

class Animation:
    """공통 뼈대. `value(t)` 만 채우면 된다."""

    needs_layout = False

    def __init__(self, num_frames, easing=None):
        self.num_frames = max(1, int(num_frames))
        self.frame_count = 1
        self.easing = easing or EASINGS["linear"]

    def progress(self):
        return self.easing(min(1.0, self.frame_count / self.num_frames))

    def done(self):
        return self.frame_count >= self.num_frames

    def animate(self):
        """한 프레임 나아간다. 끝났으면 None."""
        if self.frame_count >= self.num_frames:
            return None
        self.frame_count += 1
        return self.value(self.progress())

    def value(self, t):
        raise NotImplementedError


class NumericAnimation(Animation):
    def __init__(self, old_value, new_value, num_frames, easing=None):
        super().__init__(num_frames, easing)
        self.old = float(old_value)
        self.new = float(new_value)

    def value(self, t):
        return str(self.old + (self.new - self.old) * t)

    def __repr__(self):
        return "NumericAnimation(%g -> %g)" % (self.old, self.new)


class PxAnimation(Animation):
    """`width` / `height` 처럼 px 가 붙은 값. 배치를 다시 하게 만든다."""

    needs_layout = True

    def __init__(self, old_value, new_value, num_frames, easing=None):
        super().__init__(num_frames, easing)
        self.old = parse_px_value(old_value)
        self.new = parse_px_value(new_value)

    def value(self, t):
        return "%gpx" % (self.old + (self.new - self.old) * t)

    def __repr__(self):
        return "PxAnimation(%gpx -> %gpx)" % (self.old, self.new)


class ColorAnimation(Animation):
    """색 채널마다 따로 보간한다."""

    def __init__(self, old_value, new_value, num_frames, easing=None):
        super().__init__(num_frames, easing)
        self.old = parse_rgb(old_value)
        self.new = parse_rgb(new_value)

    def value(self, t):
        channels = [round(a + (b - a) * t) for a, b in zip(self.old, self.new)]
        return "#%02x%02x%02x" % tuple(max(0, min(255, c)) for c in channels)

    def __repr__(self):
        return "ColorAnimation(%s -> %s)" % (self.old, self.new)


class TranslateAnimation(Animation):
    def __init__(self, old_value, new_value, num_frames, easing=None):
        super().__init__(num_frames, easing)
        self.old = parse_transform(old_value) or (0.0, 0.0)
        self.new = parse_transform(new_value) or (0.0, 0.0)

    def value(self, t):
        x = self.old[0] + (self.new[0] - self.old[0]) * t
        y = self.old[1] + (self.new[1] - self.old[1]) * t
        return "translate(%gpx, %gpx)" % (x, y)

    def bounds(self, rect):
        """이 애니메이션이 지나갈 모든 자리를 아우른 사각형.

        겹침 테스트가 이것을 쓴다. 지금 자리로만 보면 안 겹치는 두 상자가
        애니메이션 도중에는 겹칠 수 있다.
        """
        from wbe.paint.geometry import Rect, map_translation
        a = map_translation(rect, self.old)
        b = map_translation(rect, self.new)
        return Rect(min(a.left, b.left), min(a.top, b.top),
                    max(a.right, b.right), max(a.bottom, b.bottom))

    def __repr__(self):
        return "TranslateAnimation(%s -> %s)" % (self.old, self.new)


ANIMATED_PROPERTIES = {
    "opacity": NumericAnimation,
    "background-color": ColorAnimation,
    "color": ColorAnimation,
    "width": PxAnimation,
    "height": PxAnimation,
    "transform": TranslateAnimation,
}


def is_animating(node, prop):
    animations = getattr(node, "animations", None) if node is not None else None
    return bool(animations and prop in animations
                and not animations[prop].done())


# ---------------------------------------------------------------------- #
# 트랜지션
# ---------------------------------------------------------------------- #

def parse_transition(value):
    """'opacity 2s, transform 1s ease-in' -> {속성: (프레임 수, 이징)}"""
    out = {}
    if not value:
        return out
    for item in value.split(","):
        parts = item.split()
        if len(parts) < 2:
            continue
        prop, duration = parts[0], parts[1]
        easing = parse_easing(parts[2] if len(parts) > 2 else None)
        frames = float(duration[:-1]) / REFRESH_RATE_SEC \
            if duration.endswith("s") else 0
        if frames > 0:
            out[prop] = (frames, easing)
    return out


def diff_styles(old_style, new_style):
    """트랜지션이 걸린 속성 중 값이 바뀐 것들."""
    transitions = {}
    for prop, (frames, easing) in parse_transition(
            new_style.get("transition")).items():
        if prop not in old_style or prop not in new_style:
            continue
        if old_style[prop] == new_style[prop]:
            continue
        transitions[prop] = (old_style[prop], new_style[prop], frames, easing)
    return transitions


# ---------------------------------------------------------------------- #
# CSS 애니메이션
# ---------------------------------------------------------------------- #

def animation_shorthand(value):
    """'fade 2s ease-in' -> (이름, 프레임 수, 이징)"""
    if not value:
        return None
    parts = value.split()
    if len(parts) < 2:
        return None
    name, duration = parts[0], parts[1]
    if not duration.endswith("s"):
        return None
    try:
        frames = float(duration[:-1]) / REFRESH_RATE_SEC
    except ValueError:
        return None
    return name, frames, parse_easing(parts[2] if len(parts) > 2 else "linear")


def keyframe_animations(node, keyframes):
    """`animation` 속성을 애니메이션 객체들로."""
    shorthand = animation_shorthand(node.style.get("animation"))
    if not shorthand:
        return {}
    name, frames, easing = shorthand
    stops = keyframes.get(name)
    if not stops or 0.0 not in stops or 1.0 not in stops:
        return {}
    out = {}
    for prop in set(stops[0.0]) & set(stops[1.0]):
        cls = ANIMATED_PROPERTIES.get(prop)
        if cls is not None:
            out[prop] = cls(stops[0.0][prop], stops[1.0][prop], frames, easing)
    return out


# ---------------------------------------------------------------------- #
# 스타일 단계에서 부르는 것들
# ---------------------------------------------------------------------- #

def apply_animations(node, old_style, tab=None, keyframes=None):
    """스타일을 새로 입힌 직후, 바뀐 값에 애니메이션을 건다."""
    if not isinstance(node, Element):
        return
    if not hasattr(node, "animations") or node.animations is None:
        node.animations = {}

    if keyframes:
        for prop, anim in keyframe_animations(node, keyframes).items():
            if prop not in node.animations:
                node.animations[prop] = anim
                node.style[prop] = anim.value(0.0)

    if old_style is None:
        return
    for prop, (old, new, frames, easing) in \
            diff_styles(old_style, node.style).items():
        cls = ANIMATED_PROPERTIES.get(prop)
        if cls is None:
            continue
        anim = cls(old, new, frames, easing)
        node.animations[prop] = anim
        value = anim.animate()
        if value is not None:
            node.style[prop] = value
        if anim.needs_layout and tab is not None:
            tab.set_needs_layout()


def run_animations(nodes, tab=None):
    """프레임마다 한 칸씩 나아간다. 무언가 움직였으면 True."""
    moved = False
    for node in nodes:
        for prop, anim in list(getattr(node, "animations", {}).items()):
            value = anim.animate()
            if value is None:
                continue
            node.style[prop] = value
            moved = True
            if anim.needs_layout and tab is not None:
                tab.set_needs_layout()
    return moved
