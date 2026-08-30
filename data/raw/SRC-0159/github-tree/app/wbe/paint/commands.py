"""그리기 명령과 시각 효과.

명령은 두 갈래다.
    `PaintCommand`  — 실제로 잉크를 놓는 것 (글자, 사각형, 이미지)
    `VisualEffect`  — 자식들을 감싸 층을 뜨는 것 (투명도, 블렌드, 변환)

효과는 `map`/`unmap` 으로 좌표를 앞뒤로 옮길 줄 알고, `clone` 으로 다른
자식들에 다시 씌워질 수 있다. 합성이 이 둘을 쓴다.
"""

import skia

from wbe.css.values import parse_blend_mode, parse_color
from wbe.paint.geometry import Rect, map_translation, skia_rect, union_of


class PaintCommand:
    """잉크를 놓는 명령. 자기를 만든 노드를 기억한다 — 히트 테스팅이 쓴다."""

    def __init__(self, rect, node=None):
        self.rect = rect
        self.node = node
        self.children = []

    @property
    def top(self):
        return self.rect.top

    @property
    def left(self):
        return self.rect.left

    @property
    def bottom(self):
        return self.rect.bottom

    @property
    def right(self):
        return self.rect.right


class VisualEffect:
    """자식들을 감싸는 효과."""

    def __init__(self, rect, children, node=None):
        self.rect = rect
        self.children = children
        self.node = node

    def map(self, rect):
        return rect

    def unmap(self, rect):
        return rect

    def clone(self, children):
        raise NotImplementedError

    def needs_compositing(self):
        return False


# ---------------------------------------------------------------------- #
# 잉크를 놓는 명령들
# ---------------------------------------------------------------------- #

class DrawText(PaintCommand):
    def __init__(self, x1, y1, text, font, color="black", node=None):
        super().__init__(
            Rect(x1, y1, x1 + font.measure(text),
                 y1 + font.metrics("linespace")), node)
        self.text, self.font, self.color = text, font, color

    def execute(self, canvas):
        paint = skia.Paint(AntiAlias=True, Color=parse_color(self.color))
        baseline = self.rect.top + self.font.metrics("ascent")
        canvas.drawString(self.text, float(self.rect.left), float(baseline),
                          self.font.skia_font, paint)

    def __repr__(self):
        return "DrawText(%r)" % self.text


class DrawRect(PaintCommand):
    def __init__(self, rect, color, node=None):
        super().__init__(rect, node)
        self.color = color

    def execute(self, canvas):
        canvas.drawRect(skia_rect(self.rect),
                        skia.Paint(Color=parse_color(self.color)))

    def __repr__(self):
        return "DrawRect(%s)" % self.color


class DrawRRect(PaintCommand):
    def __init__(self, rect, radius, color, node=None):
        super().__init__(rect, node)
        self.radius = radius
        self.color = color

    def execute(self, canvas):
        rrect = skia.RRect.MakeRectXY(skia_rect(self.rect), self.radius,
                                      self.radius)
        canvas.drawRRect(rrect, skia.Paint(Color=parse_color(self.color)))

    def __repr__(self):
        return "DrawRRect(r=%g, %s)" % (self.radius, self.color)


class DrawOutline(PaintCommand):
    def __init__(self, rect, color, thickness, node=None):
        super().__init__(rect, node)
        self.color, self.thickness = color, thickness

    def execute(self, canvas):
        canvas.drawRect(skia_rect(self.rect),
                        skia.Paint(Color=parse_color(self.color),
                                   Style=skia.Paint.kStroke_Style,
                                   StrokeWidth=self.thickness))

    def __repr__(self):
        return "DrawOutline(%s)" % self.color


class DrawLine(PaintCommand):
    def __init__(self, x1, y1, x2, y2, color, thickness, node=None):
        super().__init__(Rect(x1, y1, x2, y2), node)
        self.color, self.thickness = color, thickness

    def execute(self, canvas):
        path = skia.Path().moveTo(self.rect.left, self.rect.top) \
            .lineTo(self.rect.right, self.rect.bottom)
        canvas.drawPath(path, skia.Paint(Color=parse_color(self.color),
                                         Style=skia.Paint.kStroke_Style,
                                         StrokeWidth=self.thickness))

    def __repr__(self):
        return "DrawLine(%s)" % self.color


class DrawImage(PaintCommand):
    def __init__(self, image, rect, quality="auto", node=None):
        super().__init__(rect, node)
        self.image = image
        self.quality = skia.FilterMode.kNearest \
            if quality == "crisp-edges" else skia.FilterMode.kLinear

    def execute(self, canvas):
        if self.image is None:
            return
        canvas.drawImageRect(
            self.image,
            skia.Rect.MakeWH(self.image.width(), self.image.height()),
            skia_rect(self.rect),
            skia.SamplingOptions(self.quality))

    def __repr__(self):
        return "DrawImage(%s)" % (self.rect,)


# ---------------------------------------------------------------------- #
# 효과
# ---------------------------------------------------------------------- #

class Blend(VisualEffect):
    """투명도 · 블렌드 모드 · 블러를 한 겹 씌운다.

    블러는 투명도·블렌딩보다 **안쪽**에서 일어난다. 자식들을 흐리게 만든 뒤
    그 결과에 알파와 블렌드 모드를 먹인다. 반대로 하면 흐려진 가장자리가
    잘리거나 알파가 두 번 곱해진다.
    """

    def __init__(self, opacity, blend_mode, children, node=None, blur=0.0):
        super().__init__(union_of(children), children, node)
        self.opacity = opacity
        self.blend_mode = blend_mode
        self.blur = blur
        self.should_save = bool(blend_mode) or opacity < 1 or blur > 0

    def paint(self):
        paint = skia.Paint(Alphaf=self.opacity,
                           BlendMode=parse_blend_mode(self.blend_mode))
        if self.blur > 0:
            paint.setImageFilter(skia.ImageFilters.Blur(
                sigmaX=self.blur / 2, sigmaY=self.blur / 2))
        return paint

    def execute(self, canvas):
        if self.should_save:
            canvas.saveLayer(None, self.paint())
        for cmd in self.children:
            cmd.execute(canvas)
        if self.should_save:
            canvas.restore()

    def clone(self, children):
        return Blend(self.opacity, self.blend_mode, children, self.node,
                     self.blur)

    def needs_compositing(self):
        from wbe.animation import is_animating
        return is_animating(self.node, "opacity")

    def __repr__(self):
        return "Blend(op=%g, mode=%s, blur=%g)" % (
            self.opacity, self.blend_mode, self.blur)


class Transform(VisualEffect):
    """`translate()` 변환. 스크롤 상자의 안쪽 밀기에도 쓴다."""

    def __init__(self, translation, children, node=None):
        self.translation = translation or (0, 0)
        rect = map_translation(union_of(children), self.translation)
        super().__init__(rect, children, node)

    @property
    def dx(self):
        return self.translation[0]

    @property
    def dy(self):
        return self.translation[1]

    def map(self, rect):
        return map_translation(rect, self.translation)

    def unmap(self, rect):
        return map_translation(rect, self.translation, reverse=True)

    def clone(self, children):
        return Transform(self.translation, children, self.node)

    def needs_compositing(self):
        from wbe.animation import is_animating
        return is_animating(self.node, "transform")

    def execute(self, canvas):
        canvas.save()
        canvas.translate(*self.translation)
        for cmd in self.children:
            cmd.execute(canvas)
        canvas.restore()

    def __repr__(self):
        return "Transform(%s)" % (self.translation,)


def is_effect(item):
    return isinstance(item, VisualEffect)


def flatten(cmds, out=None):
    """중첩된 그리기 명령을 모두 훑는다."""
    out = [] if out is None else out
    for cmd in cmds:
        out.append(cmd)
        flatten(getattr(cmd, "children", []), out)
    return out
