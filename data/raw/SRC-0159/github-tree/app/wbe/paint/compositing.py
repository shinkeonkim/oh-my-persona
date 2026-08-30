"""합성.

디스플레이 리스트를 **페인트 청크**(그리기 명령 + 그것을 감싼 효과들)로
펴고, 조상 효과가 같은 청크끼리 `CompositedLayer` 로 묶는다. 애니메이션이
걸린 효과만 층을 뜨므로, 투명도나 변환이 움직여도 그 층만 다시 합치면 된다.
"""

import math

import skia

from wbe.animation import is_animating
from wbe.paint.commands import (Blend, PaintCommand, Transform, VisualEffect,
                                is_effect)
from wbe.paint.geometry import Rect, union_of

# 사이가 이만큼 넘게 텅 빈 채 떨어져 있으면 층을 나눈다.
MAX_LAYER_GAP = 2000

# 명령이 이보다 적으면 서피스를 만들지 않고 그때그때 그린다.
SHORT_LIST_LIMIT = 3


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
    return tuple(e for e in effects if e.needs_compositing())


def animated_bounds(item, effects):
    """이 명령이 **지나갈** 자리까지 아우른 절대 사각형.

    지금 자리로만 보면 안 겹치는 두 상자가 변환 애니메이션 도중에는 겹칠 수
    있다. 그 경우를 놓치면 잘못된 순서로 합쳐진다.
    """
    rect = item.rect
    for effect in reversed(effects):
        anim = None
        if isinstance(effect, Transform) and effect.node is not None:
            anim = getattr(effect.node, "animations", {}).get("transform")
        if anim is not None and not anim.done() and hasattr(anim, "bounds"):
            rect = anim.bounds(rect)
        else:
            rect = effect.map(rect)
    return rect


class CompositedLayer:
    def __init__(self, ancestors, skia_context=None):
        self.ancestors = ancestors
        self.skia_context = skia_context
        self.display_items = []
        self.surface = None
        self.absolute = None

    def add(self, item, absolute):
        self.display_items.append(item)
        self.absolute = absolute if self.absolute is None \
            else self.absolute.union(absolute)

    def can_merge(self, ancestors, absolute):
        if self.ancestors != ancestors:
            return False
        if self.absolute is None:
            return True
        # 사이가 텅 빈 채 아주 멀면 따로 둔다. 줄줄이 이어진 긴 페이지는
        # 아무리 길어도 희소하지 않으므로 합쳐도 된다.
        gap = max(0.0,
                  absolute.top - self.absolute.bottom,
                  self.absolute.top - absolute.bottom)
        return gap <= MAX_LAYER_GAP

    def composited_bounds(self):
        if not self.display_items:
            return Rect(0, 0, 0, 0)
        return union_of(self.display_items)

    def absolute_bounds(self):
        return self.absolute or Rect(0, 0, 0, 0)

    def is_short(self):
        return len(self.display_items) < SHORT_LIST_LIMIT

    def raster(self):
        if self.is_short():
            self.surface = None
            return
        bounds = self.composited_bounds()
        w = max(1, int(math.ceil(bounds.width)))
        h = max(1, int(math.ceil(bounds.height)))
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


class DrawCompositedLayer(PaintCommand):
    """이미 래스터해 둔 합성 레이어 하나를 화면에 올린다."""

    def __init__(self, layer):
        super().__init__(layer.composited_bounds(), None)
        self.layer = layer

    def execute(self, canvas, alpha=1.0, blend_mode=None):
        from wbe.css.values import parse_blend_mode
        paint = None
        if alpha < 1.0 or blend_mode:
            paint = skia.Paint(Alphaf=alpha,
                               BlendMode=parse_blend_mode(blend_mode))
        if self.layer.surface is None:
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


def composite(display_list, skia_context=None):
    """디스플레이 리스트를 합성 레이어 목록으로."""
    layers = []
    for item, effects in paint_chunks(display_list):
        ancestors = composited_ancestors(effects)
        absolute = animated_bounds(item, effects)
        target = None
        for layer in reversed(layers):
            if layer.can_merge(ancestors, absolute):
                target = layer
                break
            if layer.absolute_bounds().overlaps(absolute):
                break            # 겹치면 그 위로 올라갈 수 없다
        if target is None:
            target = CompositedLayer(ancestors, skia_context)
            layers.append(target)
        target.add(item, absolute)
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


def draw_list(display_list, canvas):
    """그리기 목록을 캔버스에 올린다.

    `Blend` 안에 합성 레이어 하나뿐이면 층을 뜨지 않고 그릴 때 알파를 바로
    먹인다. 서피스 복사가 한 번 줄어든다. 블러가 있으면 층을 떠야 한다.
    """
    for item in display_list:
        if isinstance(item, Blend) and len(item.children) == 1 \
                and isinstance(item.children[0], DrawCompositedLayer) \
                and item.blur == 0:
            item.children[0].execute(canvas, item.opacity, item.blend_mode)
        else:
            item.execute(canvas)
