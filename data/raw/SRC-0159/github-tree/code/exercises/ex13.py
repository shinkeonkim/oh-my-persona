"""13장 연습문제 구현 (13-1 ~ 13-12).

lab13.py 는 그대로 두고, 1~12장 연습문제를 이어받아 그 위에 13장 기능을 얹는다.
자바스크립트 쪽은 runtime13ex.js, 창은 ex13_sdl.py 에 있다.

13장 본문 기능(transition, NumericAnimation, transform, 페인트 청크,
CompositedLayer, 합성·래스터·그리기 분리)에 더해

    13-1  background-color   색 채널마다 보간
    13-2  이징 함수           cubic-bezier 와 이름 붙은 것들
    13-3  합성되고 스레드화된 애니메이션 (transform 과 스크롤)
    13-4  너비/높이 애니메이션  px 값 보간 + 레이아웃 무효화
    13-5  CSS 애니메이션      @keyframes
    13-6  변환 애니메이션에서의 겹침 테스트
    13-7  희소한 합성 레이어 피하기
    13-8  짧은 디스플레이 리스트
    13-9  히트 테스팅         지역 좌표로 내려가며
    13-10 z-index
    13-11 애니메이션 스크롤    부드러운 스크롤과 플링
    13-12 불투명도와 그리기    서피스 복사를 한 번으로
"""

import math
import os
import sys

import skia

import ex10
import ex11
import ex12
from ex4 import Text, Element
from ex6 import tree_to_list
from ex11 import (Rect, DrawText, DrawRect, DrawRRect, DrawLine, DrawOutline,
                  parse_color, parse_blend_mode, parse_px_value, parse_blur,
                  border_radius, is_scrollable, skia_rect, union,
                  WIDTH, HEIGHT, VSTEP, SCROLL_STEP)

HERE = os.path.dirname(os.path.abspath(__file__))

REFRESH_RATE_SEC = 0.033
MAX_LAYER_GAP = 2000            # 연습문제 13-7
SHORT_LIST_LIMIT = 3            # 연습문제 13-8


# ---------------------------------------------------------------------- #
# 시각 효과 — 좌표를 옮길 줄 안다
# ---------------------------------------------------------------------- #

def map_translation(rect, translation, reverse=False):
    if translation is None:
        return rect
    dx, dy = translation
    if reverse:
        dx, dy = -dx, -dy
    return Rect(rect.left + dx, rect.top + dy,
                rect.right + dx, rect.bottom + dy)


def parse_transform(value):
    """'translate(12px, 30px)' -> (12.0, 30.0). 아니면 None."""
    if not value:
        return None
    value = value.strip()
    if not value.casefold().startswith("translate(") or not value.endswith(")"):
        return None
    parts = value[len("translate("):-1].split(",")
    if len(parts) != 2:
        return None
    return parse_px_value(parts[0]), parse_px_value(parts[1])


class Transform(ex11.Translate):
    """translate() 변환. 좌표를 앞뒤로 옮길 수 있다."""

    def __init__(self, translation, children, node=None):
        self.translation = translation
        dx, dy = translation or (0, 0)
        super().__init__(dx, dy, children, node)

    def map(self, rect):
        return map_translation(rect, self.translation)

    def unmap(self, rect):
        return map_translation(rect, self.translation, reverse=True)

    def clone(self, children):
        return Transform(self.translation, children, self.node)

    def needs_compositing(self):
        return is_animating(self.node, "transform")

    def __repr__(self):
        return "Transform(%s)" % (self.translation,)


class Blend(ex11.Blend):
    def map(self, rect):
        return rect

    def unmap(self, rect):
        return rect

    def clone(self, children):
        return Blend(self.opacity, self.blend_mode, children, self.node,
                     self.blur)

    def needs_compositing(self):
        return is_animating(self.node, "opacity")


def is_animating(node, prop):
    animations = getattr(node, "animations", None) if node is not None else None
    return bool(animations and prop in animations
                and not animations[prop].done())


class DrawCompositedLayer:
    """이미 래스터해 둔 합성 레이어 하나를 화면에 올린다."""

    def __init__(self, layer):
        self.layer = layer
        self.rect = layer.composited_bounds()
        self.node = None
        self.children = []

    def execute(self, canvas, alpha=1.0, blend_mode=None):
        # 연습문제 13-12: 알파를 여기서 바로 먹인다 (서피스 복사 한 번 줄임)
        paint = None
        if alpha < 1.0 or blend_mode:
            paint = skia.Paint(Alphaf=alpha,
                               BlendMode=parse_blend_mode(blend_mode))
        if self.layer.surface is None:
            # 연습문제 13-8: 명령이 몇 개 안 되면 서피스 없이 바로 그린다
            canvas.save()
            if paint is not None:
                canvas.saveLayer(None, paint)
            for item in self.layer.display_items:
                item.execute(canvas)
            if paint is not None:
                canvas.restore()
            canvas.restore()
            return
        bounds = self.layer.composited_bounds()
        canvas.save()
        canvas.translate(bounds.left, bounds.top)
        canvas.drawImage(self.layer.surface.makeImageSnapshot(), 0, 0,
                         skia.SamplingOptions(), paint)
        canvas.restore()

    def __repr__(self):
        return "DrawCompositedLayer(%s)" % self.layer


def is_effect(item):
    return isinstance(item, (Transform, Blend, ex11.Blend, ex11.Translate))


# ---------------------------------------------------------------------- #
# 이징 (연습문제 13-2)
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
    if not name:
        return EASINGS["ease"]          # 실제 브라우저의 기본값
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
# 애니메이션
# ---------------------------------------------------------------------- #

class Animation:
    """공통 뼈대. frame 번째의 값을 낸다."""

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
    """연습문제 13-4: width / height 처럼 px 가 붙은 값."""

    needs_layout = True

    def __init__(self, old_value, new_value, num_frames, easing=None):
        super().__init__(num_frames, easing)
        self.old = parse_px_value(old_value)
        self.new = parse_px_value(new_value)

    def value(self, t):
        return "%gpx" % (self.old + (self.new - self.old) * t)

    def __repr__(self):
        return "PxAnimation(%gpx -> %gpx)" % (self.old, self.new)


def parse_rgb(color):
    """색 이름이나 #rrggbb 를 (r, g, b) 로."""
    color = ex11.NAMED_COLORS.get(color, color)
    if color.startswith("#") and len(color) >= 7:
        return (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16))
    return (0, 0, 0)


class ColorAnimation(Animation):
    """연습문제 13-1: 색 채널마다 따로 보간한다."""

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
    """연습문제 13-3: transform: translate(...) 도 애니메이션한다."""

    def __init__(self, old_value, new_value, num_frames, easing=None):
        super().__init__(num_frames, easing)
        self.old = parse_transform(old_value) or (0.0, 0.0)
        self.new = parse_transform(new_value) or (0.0, 0.0)

    def value(self, t):
        x = self.old[0] + (self.new[0] - self.old[0]) * t
        y = self.old[1] + (self.new[1] - self.old[1]) * t
        return "translate(%gpx, %gpx)" % (x, y)

    def bounds(self, rect):
        """연습문제 13-6: 애니메이션이 지나갈 모든 자리를 아우른다."""
        a = map_translation(rect, self.old)
        b = map_translation(rect, self.new)
        return union([_R(a), _R(b)])

    def __repr__(self):
        return "TranslateAnimation(%s -> %s)" % (self.old, self.new)


class _R:
    def __init__(self, rect):
        self.rect = rect


ANIMATED_PROPERTIES = {
    "opacity": NumericAnimation,
    "background-color": ColorAnimation,      # 13-1
    "color": ColorAnimation,
    "width": PxAnimation,                    # 13-4
    "height": PxAnimation,
    "transform": TranslateAnimation,         # 13-3
}


# ---------------------------------------------------------------------- #
# 트랜지션과 CSS 애니메이션
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


def parse_keyframes(css_text):
    """연습문제 13-5: @keyframes 블록을 읽는다.

    @keyframes 이름 { from { ... } to { ... } }  또는 0% / 100%
    """
    out = {}
    i = 0
    text = css_text
    while True:
        at = text.find("@keyframes", i)
        if at < 0:
            return out
        j = text.find("{", at)
        if j < 0:
            return out
        name = text[at + len("@keyframes"):j].strip()
        depth, k = 0, j
        while k < len(text):
            if text[k] == "{":
                depth += 1
            elif text[k] == "}":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        body = text[j + 1:k]
        out[name] = parse_keyframe_body(body)
        i = k + 1


def parse_keyframe_body(body):
    frames = {}
    i = 0
    while True:
        brace = body.find("{", i)
        if brace < 0:
            return frames
        selector = body[i:brace].strip().casefold()
        end = body.find("}", brace)
        if end < 0:
            return frames
        pairs = {}
        for decl in body[brace + 1:end].split(";"):
            if ":" not in decl:
                continue
            prop, _, value = decl.partition(":")
            pairs[prop.strip().casefold()] = value.strip()
        for key in selector.split(","):
            key = key.strip()
            stop = {"from": 0.0, "to": 1.0}.get(key)
            if stop is None and key.endswith("%"):
                try:
                    stop = float(key[:-1]) / 100
                except ValueError:
                    stop = None
            if stop is not None:
                frames[stop] = pairs
        i = end + 1


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
    easing = parse_easing(parts[2] if len(parts) > 2 else "linear")
    return name, frames, easing


def keyframe_animations(node, keyframes):
    """연습문제 13-5: animation 속성을 애니메이션 객체들로."""
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
        if cls is None:
            continue
        out[prop] = cls(stops[0.0][prop], stops[1.0][prop], frames, easing)
    return out


# ---------------------------------------------------------------------- #
# 스타일 — 값이 바뀌면 애니메이션을 만든다
# ---------------------------------------------------------------------- #

def style(node, rules, tab=None, keyframes=None):
    old_style = getattr(node, "style", None)
    ex10.style(node, rules)          # 6~10장의 캐스케이드를 그대로 쓴다
    apply_animations(node, old_style, tab, keyframes)
    for child in node.children:
        style(child, rules, tab, keyframes)


def apply_animations(node, old_style, tab, keyframes):
    if not isinstance(node, Element):
        return
    if not hasattr(node, "animations"):
        node.animations = {}

    if keyframes:                                     # 13-5
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


# ---------------------------------------------------------------------- #
# 그리기 — 시각 효과와 z-index
# ---------------------------------------------------------------------- #

def z_index(node):
    """연습문제 13-10: position 이 static 이 아닐 때만 듣는다."""
    if not isinstance(node, Element):
        return 0
    if node.style.get("position", "static") == "static":
        return 0
    try:
        return int(node.style.get("z-index", "0"))
    except ValueError:
        return 0


def paint_visual_effects(node, cmds, rect):
    opacity = float(node.style.get("opacity", "1.0"))
    blend_mode = node.style.get("mix-blend-mode")
    blur = parse_blur(node.style.get("filter"))
    overflow = node.style.get("overflow", "visible")
    radius = border_radius(node)
    translation = parse_transform(node.style.get("transform"))

    if is_scrollable(node):
        cmds = [Transform((0, -getattr(node, "scroll_offset", 0)), cmds, node)]

    if overflow in ("clip", "scroll"):
        if not blend_mode:
            blend_mode = "source-over"
        cmds = cmds + [Blend(1.0, "destination-in",
                             [DrawRRect(rect, radius, "white", node)], node)]

    out = [Blend(opacity, blend_mode, cmds, node, blur)]
    if translation:
        out = [Transform(translation, out, node)]
    return out


def paint_tree(layout_object, display_list):
    cmds = []
    if layout_object.should_paint():
        cmds = layout_object.paint()
    children = layout_object.children
    if any(z_index(getattr(c, "node", None)) for c in children):   # 13-10
        children = sorted(children,
                          key=lambda c: z_index(getattr(c, "node", None)))
    for child in children:
        paint_tree(child, cmds)
    if layout_object.should_paint():
        cmds = layout_object.paint_effects(cmds)
    display_list.extend(cmds)


def install_compositing():
    """앞 장 배치 코드가 13장의 효과·순서를 쓰도록 바꿔 끼운다."""
    ex11.paint_visual_effects = paint_visual_effects
    ex11.paint_tree = paint_tree
    ex12.paint_tree = paint_tree


install_compositing()


# ---------------------------------------------------------------------- #
# 페인트 청크와 합성 레이어
# ---------------------------------------------------------------------- #

def paint_chunks(display_list, effects=(), out=None):
    """(그리기 명령, 조상 효과들) 쌍의 목록으로 편다."""
    out = [] if out is None else out
    for item in display_list:
        if is_effect(item):
            paint_chunks(item.children, tuple(effects) + (item,), out)
        else:
            out.append((item, tuple(effects)))
    return out


def composited_ancestors(effects):
    return tuple(e for e in effects if getattr(e, "needs_compositing",
                                               lambda: False)())


def absolute_bounds(rect, effects):
    for effect in reversed(effects):
        rect = effect.map(rect) if hasattr(effect, "map") else rect
    return rect


def animated_bounds(item, effects):
    """연습문제 13-6: 변환 애니메이션이 지나갈 자리까지 아우른다."""
    rect = item.rect
    for effect in reversed(effects):
        anim = None
        if isinstance(effect, Transform) and effect.node is not None:
            anim = getattr(effect.node, "animations", {}).get("transform")
        if anim is not None and not anim.done() \
                and hasattr(anim, "bounds"):
            rect = anim.bounds(rect)
        elif hasattr(effect, "map"):
            rect = effect.map(rect)
    return rect


def overlaps(a, b):
    return not (a.right <= b.left or b.right <= a.left
                or a.bottom <= b.top or b.bottom <= a.top)


class CompositedLayer:
    def __init__(self, ancestors, skia_context=None):
        self.ancestors = ancestors
        self.skia_context = skia_context
        self.display_items = []
        self.effects_for = []
        self.surface = None
        self.absolute = None

    def add(self, item, effects, absolute):
        self.display_items.append(item)
        self.effects_for.append(effects)
        self.absolute = absolute if self.absolute is None \
            else union([_R(self.absolute), _R(absolute)])

    def can_merge(self, ancestors, absolute):
        if self.ancestors != ancestors:
            return False
        if self.absolute is None:
            return True
        # 연습문제 13-7: 사이가 텅 빈 채 아주 멀면 따로 둔다
        gap = max(0.0,
                  absolute.top - self.absolute.bottom,
                  self.absolute.top - absolute.bottom)
        return gap <= MAX_LAYER_GAP

    def composited_bounds(self):
        return union([_R(i.rect) for i in self.display_items]) \
            if self.display_items else Rect(0, 0, 0, 0)

    def absolute_bounds(self):
        return self.absolute or Rect(0, 0, 0, 0)

    def is_short(self):
        """연습문제 13-8: 명령이 몇 개 안 되면 서피스를 두지 않는다."""
        return len(self.display_items) < SHORT_LIST_LIMIT

    def raster(self):
        if self.is_short():
            self.surface = None
            return
        bounds = self.composited_bounds()
        w = max(1, int(math.ceil(bounds.right - bounds.left)))
        h = max(1, int(math.ceil(bounds.bottom - bounds.top)))
        if self.surface is None or self.surface.width() != w \
                or self.surface.height() != h:
            self.surface = skia.Surface(w, h)
        with self.surface as canvas:
            canvas.clear(skia.ColorTRANSPARENT)
            canvas.save()
            canvas.translate(-bounds.left, -bounds.top)
            for item in self.display_items:
                item.execute(canvas)
            canvas.restore()

    def __repr__(self):
        return "CompositedLayer(%d개 명령)" % len(self.display_items)


def composite(display_list, skia_context=None):
    """디스플레이 리스트를 합성 레이어 목록으로."""
    layers = []
    for item, effects in paint_chunks(display_list):
        ancestors = composited_ancestors(effects)
        absolute = animated_bounds(item, effects)          # 13-6
        target = None
        for layer in reversed(layers):
            if layer.can_merge(ancestors, absolute):
                target = layer
                break
            if overlaps(layer.absolute_bounds(), absolute):
                break            # 겹치면 그 위로 올라갈 수 없다
        if target is None:
            target = CompositedLayer(ancestors, skia_context)
            layers.append(target)
        target.add(item, effects, absolute)
    return layers


def paint_draw_list(layers):
    """합성 레이어들을 조상 효과로 다시 감싼다."""
    out = []
    for layer in layers:
        cmds = [DrawCompositedLayer(layer)]
        for effect in reversed(layer.ancestors):
            cmds = [effect.clone(cmds)]
        out.extend(cmds)
    return out


def draw_list(display_list, canvas, layers=None):
    """연습문제 13-12: Blend 안에 합성 레이어 하나뿐이면 알파를 바로 먹인다."""
    for item in display_list:
        if isinstance(item, Blend) and len(item.children) == 1 \
                and isinstance(item.children[0], DrawCompositedLayer) \
                and item.blur == 0:
            item.children[0].execute(canvas, item.opacity, item.blend_mode)
        elif is_effect(item):
            item.execute(canvas)
        else:
            item.execute(canvas)


# ---------------------------------------------------------------------- #
# 연습문제 13-9: 지역 좌표로 내려가는 히트 테스팅
# ---------------------------------------------------------------------- #

def hit_test(display_list, x, y):
    """맨 위에 있는, 그 점을 덮는 그리기 명령의 노드."""
    found = [None]

    def walk(items, px, py):
        for item in items:
            if is_effect(item):
                local_x, local_y = px, py
                if isinstance(item, Transform) and item.translation:
                    dx, dy = item.translation
                    local_x, local_y = px - dx, py - dy
                walk(item.children, local_x, local_y)
            elif item.node is not None and ex11.hit(item, px, py):
                found[0] = item.node
    walk(display_list, x, y)
    return found[0]


# ---------------------------------------------------------------------- #
# 연습문제 13-11: 애니메이션 스크롤
# ---------------------------------------------------------------------- #

SCROLL_FRAMES = 8
FLING_FRICTION = 0.92
FLING_MIN_SPEED = 0.5


class ScrollAnimation:
    """방향키 스크롤을 한 칸에 툭 옮기지 않고 부드럽게 옮긴다."""

    def __init__(self, start, end, num_frames=SCROLL_FRAMES, easing=None):
        self.start = start
        self.end = end
        self.num_frames = max(1, num_frames)
        self.frame = 0
        self.easing = easing or EASINGS["ease-out"]

    def done(self):
        return self.frame >= self.num_frames

    def animate(self):
        if self.done():
            return None
        self.frame += 1
        t = self.easing(self.frame / self.num_frames)
        return self.start + (self.end - self.start) * t

    def retarget(self, end):
        """스크롤 중에 또 누르면 목표만 바꾼다."""
        self.end = end
        self.frame = 0


class FlingAnimation:
    """터치에서 손을 뗀 뒤의 관성. 마찰로 잦아든다."""

    def __init__(self, scroll, velocity, max_scroll,
                 friction=FLING_FRICTION):
        self.scroll = scroll
        self.velocity = velocity
        self.max_scroll = max_scroll
        self.friction = friction

    def done(self):
        return abs(self.velocity) < FLING_MIN_SPEED

    def animate(self):
        if self.done():
            return None
        self.scroll += self.velocity
        self.velocity *= self.friction
        if self.scroll <= 0:
            self.scroll, self.velocity = 0, 0
        elif self.scroll >= self.max_scroll:
            self.scroll, self.velocity = self.max_scroll, 0
        return self.scroll


# ---------------------------------------------------------------------- #
# 자바스크립트 — style 을 건드리면 트랜지션이 걸린다
# ---------------------------------------------------------------------- #

RUNTIME_JS = open(os.path.join(HERE, "runtime13ex.js"), encoding="utf8").read()


class JSContext(ex12.JSContext):
    # 하위 장은 이 클래스 속성만 갈아 끼우면 된다
    RUNTIME = RUNTIME_JS

    def __init__(self, tab):
        self.tab = tab
        self.node_to_handle = {}
        self.handle_to_node = {}
        self.id_globals = {}
        self.discarded = False
        self.interval_handles = set()

        import dukpy
        self.interp = dukpy.JSInterpreter()
        for name in ("log", "querySelectorAll", "getAttribute", "setAttribute",
                     "innerHTML_get", "innerHTML_set", "outerHTML_get",
                     "getChildren", "getParent", "ancestors",
                     "createElement", "createTextNode",
                     "appendChild", "insertBefore", "removeChild",
                     "cookie_get", "cookie_set",
                     "setTimeout", "clearTimeout",
                     "setInterval", "clearInterval",
                     "XMLHttpRequest_send", "requestAnimationFrame",
                     "style_get", "style_set", "style_set_property"):
            self.interp.export_function(name, getattr(self, name))
        self.interp.evaljs(self.RUNTIME + "\n0;")

    def style_get(self, handle):
        return self.node(handle).attributes.get("style", "")

    def style_set(self, handle, text):
        self.node(handle).attributes["style"] = text
        self.tab.restyle()
        return text

    def style_set_property(self, handle, prop, value):
        node = self.node(handle)
        decls = [d for d in node.attributes.get("style", "").split(";")
                 if d.strip() and d.split(":", 1)[0].strip() != prop]
        decls.append("%s: %s" % (prop, value))
        node.attributes["style"] = "; ".join(d.strip() for d in decls)
        self.tab.restyle()
        return value


def install_js():
    ex10.JSContext = JSContext
    ex12.JSContext = JSContext


install_js()


# ---------------------------------------------------------------------- #
# 탭
# ---------------------------------------------------------------------- #

class Tab(ex12.Tab):
    def __init__(self, browser, tab_height, **kwargs):
        super().__init__(browser, tab_height, **kwargs)
        self.needs_layout = False
        self.needs_paint = False
        self.keyframes = {}
        self.scroll_animation = None

    def set_needs_layout(self):
        self.needs_layout = True
        self.set_needs_render()

    def set_needs_paint(self):
        self.needs_paint = True
        self.set_needs_render()

    def restyle(self):
        for node in tree_to_list(self.nodes, []):
            if isinstance(node, Element) and not hasattr(node, "is_focused"):
                node.is_focused = False
        style(self.nodes, self.all_rules(), self, self.keyframes)
        self.needs_layout = True
        self.set_needs_render()

    def load(self, url, payload=None, record=True):
        super().load(url, payload, record)
        # @keyframes 는 캐스케이드를 타지 않으므로 따로 모은다 (13-5)
        self.keyframes = {}
        for node in tree_to_list(self.nodes, []):
            if isinstance(node, Element) and node.tag == "style":
                text = "".join(c.text for c in node.children
                               if isinstance(c, Text))
                self.keyframes.update(parse_keyframes(text))
        if self.keyframes:
            self.restyle()
            self.force_render()

    def run_animation_frame(self, scroll):
        if scroll is not None:
            self.scroll = scroll
        if self.scroll_animation is not None:              # 13-11
            value = self.scroll_animation.animate()
            if value is None:
                self.scroll_animation = None
            else:
                self.scroll = value
                self.set_needs_paint()
        if self.js is not None:
            self.js.interp.evaljs(ex12.RAF_JS)
        if run_animations(tree_to_list(self.nodes, []), self):
            self.set_needs_paint()
        self.render()
        return ex12.CommitData(self.url, self.scroll, self.document.height,
                               self.display_list)

    def render(self):
        if not (self.needs_render or self.needs_layout or self.needs_paint):
            return False
        self.measure.time("render")
        if self.needs_layout or self.document is None:
            self.document = ex11.DocumentLayout(self.nodes)
            self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)
        self.flat_display_list = ex11.flatten(self.display_list)
        self.needs_render = self.needs_layout = self.needs_paint = False
        self.measure.stop("render")
        return True

    # -- 연습문제 13-9 -------------------------------------------------- #

    def node_at(self, x, y):
        return hit_test(self.display_list, x, y + self.scroll)

    # -- 연습문제 13-11 ------------------------------------------------- #

    def smooth_scroll_by(self, delta):
        target = max(0, min(self.scroll + delta, self.max_scroll()))
        if self.scroll_animation is not None:
            self.scroll_animation.retarget(target)
        else:
            self.scroll_animation = ScrollAnimation(self.scroll, target)
        self.set_needs_paint()
        return target

    def fling(self, velocity):
        self.scroll_animation = FlingAnimation(self.scroll, velocity,
                                               self.max_scroll())
        self.set_needs_paint()


def main(argv):
    from ex13_sdl import run
    run(argv[0] if argv else ex11.HOME_URL)


if __name__ == "__main__":
    main(sys.argv[1:])
