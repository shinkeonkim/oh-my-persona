"""그리기 — 효과, 합성, 히트 테스팅, 애니메이션."""

import unittest

import skia

from wbe.animation import (ColorAnimation, EASINGS, NumericAnimation,
                           PxAnimation, TranslateAnimation, animation_shorthand,
                           cubic_bezier, diff_styles, keyframe_animations,
                           parse_easing, parse_transition, run_animations)
from wbe.css.parser import parse_keyframes
from wbe.layout.boxes import BlockLayout
from wbe.paint.commands import (Blend, DrawRRect, DrawRect, DrawText,
                                Transform, flatten)
from wbe.paint.compositing import (CompositedLayer, DrawCompositedLayer,
                                   MAX_LAYER_GAP, SHORT_LIST_LIMIT,
                                   animated_bounds, composite, draw_list,
                                   paint_chunks, paint_draw_list)
from wbe.paint.effects import (FOCUS_OUTER_COLOR, mark_paint_dirty,
                               paint_outline, paint_tree)
from wbe.paint.geometry import Rect, inside_rounded
from wbe.paint.hittest import hit_test
from wbe.tests.helpers import build, find_el, layouts, of_type, styled, texts


class TestVisualEffects(unittest.TestCase):
    def test_opacity_makes_a_layer(self):
        _, cmds = build("<div>글</div>", "div { opacity: 0.5; }")
        blends = [b for b in of_type(cmds, Blend) if b.opacity < 1]
        self.assertTrue(blends and blends[0].should_save)

    def test_full_opacity_saves_nothing(self):
        _, cmds = build("<div>글</div>", "div { opacity: 1.0; }")
        self.assertTrue(all(not b.should_save for b in of_type(cmds, Blend)))

    def test_blend_mode(self):
        _, cmds = build("<div>글</div>", "div { mix-blend-mode: multiply; }")
        self.assertTrue(any(b.blend_mode == "multiply"
                            for b in of_type(cmds, Blend)))

    def test_border_radius_uses_rrect(self):
        _, cmds = build("<div>글</div>",
                        "div { background-color: red; border-radius: 10px; }")
        self.assertTrue(of_type(cmds, DrawRRect))

    def test_overflow_clip_masks(self):
        _, cmds = build("<div>글</div>",
                        "div { overflow: clip; border-radius: 10px; }")
        masks = [b for b in of_type(cmds, Blend)
                 if b.blend_mode == "destination-in"]
        self.assertEqual(len(masks), 1)

    def test_transform(self):
        _, cmds = build("<div>글</div>",
                        "div { transform: translate(10px, 20px); }")
        self.assertEqual(len(of_type(cmds, Transform)), 1)

    def test_blur_is_inside_opacity(self):
        """흐리게 만든 결과에 투명도가 걸려야 한다."""
        _, cmds = build("<div>글</div>",
                        "div { filter: blur(4px); opacity: 0.5; }")
        blend = next(b for b in of_type(cmds, Blend) if b.blur > 0)
        self.assertEqual(blend.opacity, 0.5)
        self.assertIsNotNone(blend.paint().getImageFilter())

    def test_scrollable_translates_and_masks(self):
        _, cmds = build("<div>" + "<p>줄</p>" * 20 + "</div>",
                        "div { overflow: scroll; height: 50px; }")
        self.assertTrue(of_type(cmds, Transform))
        self.assertTrue([b for b in of_type(cmds, Blend)
                         if b.blend_mode == "destination-in"])

    def test_focus_ring_is_two_toned(self):
        tree = styled('<a href="/x">글</a>')
        a = find_el(tree, "a")[0]
        a.style["outline"] = "2px solid black"
        rings = paint_outline(a, [], [Rect(10, 10, 60, 30)])
        self.assertEqual(len(rings), 2)
        self.assertEqual(rings[0].color, FOCUS_OUTER_COLOR)
        self.assertGreater(rings[0].thickness, rings[1].thickness)

    def test_z_index_reorders(self):
        _, cmds = build('<div id="a">가</div><div id="b">나</div>',
                        "#a { position: relative; z-index: 5; } "
                        "#b { position: relative; z-index: 1; }")
        self.assertEqual(texts(cmds), ["나", "가"])


class TestPaintCache(unittest.TestCase):
    HTML = "<div><p>가</p></div><div><p>나</p></div><div><p>다</p></div>"

    def fresh(self):
        from wbe.layout.boxes import DocumentLayout
        doc = DocumentLayout(styled(self.HTML))
        doc.layout()
        cmds = []
        stats = paint_tree(doc, cmds)
        return doc, cmds, stats

    def test_first_paint_paints(self):
        _, _, stats = self.fresh()
        self.assertGreater(stats["repainted"], 0)
        self.assertEqual(stats["reused"], 0)

    def test_second_paint_reuses(self):
        doc, _, _ = self.fresh()
        stats = paint_tree(doc, [])
        self.assertEqual(stats["repainted"], 0)
        self.assertEqual(stats["reused"], 1)

    def test_dirty_branch_repaints_partially(self):
        doc, _, _ = self.fresh()
        target = [o for o in layouts(doc, BlockLayout)
                  if o.element("p")][1]
        mark_paint_dirty(target)
        cmds = []
        stats = paint_tree(doc, cmds)
        self.assertGreater(stats["reused"], 0)
        for word in ("가", "나", "다"):
            self.assertIn(word, texts(flatten(cmds)))

    def test_dirty_reaches_the_root(self):
        doc, _, _ = self.fresh()
        target = [o for o in layouts(doc, BlockLayout) if o.element("p")][1]
        mark_paint_dirty(target)
        self.assertTrue(doc.has_dirty_paint_descendants)


class TestHitTest(unittest.TestCase):
    def test_plain_rect(self):
        self.assertTrue(inside_rounded(Rect(0, 0, 100, 100), 0, 1, 1))

    def test_rounded_corner_is_outside(self):
        self.assertFalse(inside_rounded(Rect(0, 0, 100, 100), 40, 2, 2))

    def test_all_four_corners_cut(self):
        r = Rect(0, 0, 100, 100)
        for x, y in ((2, 2), (98, 2), (2, 98), (98, 98)):
            self.assertFalse(inside_rounded(r, 40, x, y))

    def test_middle_is_inside(self):
        self.assertTrue(inside_rounded(Rect(0, 0, 100, 100), 40, 50, 50))

    def test_radius_clamped(self):
        self.assertTrue(inside_rounded(Rect(0, 0, 20, 20), 999, 10, 10))

    def test_finds_node(self):
        _, cmds = build("<p>글자</p>")
        cmd = of_type(cmds, DrawText)[0]
        self.assertIsNotNone(hit_test(cmds, cmd.rect.left + 1,
                                      cmd.rect.top + 1))

    def test_misses_outside(self):
        _, cmds = build("<p>글자</p>")
        self.assertIsNone(hit_test(cmds, 5000, 5000))

    def test_transform_moves_the_hit_area(self):
        _, cmds = build("<div>글자</div>",
                        "div { transform: translate(100px, 0px); }")
        cmd = of_type(cmds, DrawText)[0]
        self.assertIsNotNone(hit_test(cmds, cmd.rect.left + 1,
                                      cmd.rect.top + 1))

    def test_rounded_corner_misses(self):
        _, cmds = build("<div>글</div>",
                        "div { background-color: red; border-radius: 40px; "
                        "width: 100px; height: 100px; }")
        rrect = of_type(cmds, DrawRRect)[0]
        self.assertIsNone(hit_test(cmds, rrect.rect.left + 1,
                                   rrect.rect.top + 1))


class TestEasing(unittest.TestCase):
    def test_linear(self):
        self.assertAlmostEqual(EASINGS["linear"](0.3), 0.3)

    def test_endpoints(self):
        for name, fn in EASINGS.items():
            self.assertAlmostEqual(fn(0.0), 0.0, places=5, msg=name)
            self.assertAlmostEqual(fn(1.0), 1.0, places=5, msg=name)

    def test_ease_in_starts_slow(self):
        self.assertLess(EASINGS["ease-in"](0.25), 0.25)

    def test_default_is_not_linear(self):
        self.assertNotAlmostEqual(parse_easing(None)(0.25), 0.25, places=3)

    def test_cubic_bezier_parsed(self):
        fn = parse_easing("cubic-bezier(0.42, 0, 1, 1)")
        self.assertAlmostEqual(fn(0.25), EASINGS["ease-in"](0.25), places=4)


class TestAnimations(unittest.TestCase):
    def test_numeric(self):
        self.assertEqual(NumericAnimation(0, 1, 2).value(0.5), "0.5")

    def test_px_keeps_unit_and_needs_layout(self):
        anim = PxAnimation("100px", "200px", 10)
        self.assertEqual(anim.value(0.5), "150px")
        self.assertTrue(anim.needs_layout)

    def test_opacity_does_not_need_layout(self):
        self.assertFalse(NumericAnimation(0, 1, 4).needs_layout)

    def test_color_channels_independent(self):
        mid = ColorAnimation("#ff0000", "#0000ff", 10).value(0.5)
        self.assertEqual(mid[3:5], "00")
        self.assertNotEqual(mid[1:3], "ff")

    def test_translate(self):
        anim = TranslateAnimation("translate(0px, 0px)",
                                  "translate(100px, 0px)", 10)
        self.assertEqual(anim.value(0.5), "translate(50px, 0px)")

    def test_translate_bounds_cover_the_path(self):
        anim = TranslateAnimation("translate(0px, 0px)",
                                  "translate(0px, 300px)", 30)
        box = anim.bounds(Rect(0, 0, 10, 10))
        self.assertEqual((box.top, box.bottom), (0, 310))

    def test_transition_parsed(self):
        out = parse_transition("opacity 2s, transform 1s ease-in")
        self.assertEqual(set(out), {"opacity", "transform"})

    def test_diff_styles(self):
        old = {"opacity": "1", "transition": "opacity 2s"}
        new = {"opacity": "0.5", "transition": "opacity 2s"}
        self.assertIn("opacity", diff_styles(old, new))

    def test_no_change_no_transition(self):
        same = {"opacity": "1", "transition": "opacity 2s"}
        self.assertEqual(diff_styles(same, same), {})

    def test_keyframes_make_animations(self):
        keyframes = parse_keyframes(
            "@keyframes fade { from { opacity: 1; } to { opacity: 0; } }")
        tree = styled("<div>글</div>", "div { animation: fade 2s; }")
        div = find_el(tree, "div")[0]
        anims = keyframe_animations(div, keyframes)
        self.assertIn("opacity", anims)

    def test_animation_shorthand(self):
        self.assertEqual(animation_shorthand("fade 2s")[0], "fade")

    def test_run_animations_advances(self):
        tree = styled("<div>글</div>", "div { opacity: 1; }")
        div = find_el(tree, "div")[0]
        div.animations = {"opacity": NumericAnimation(1, 0, 4)}
        self.assertTrue(run_animations([div]))
        self.assertLess(float(div.style["opacity"]), 1.0)


class TestCompositing(unittest.TestCase):
    def animated(self, css, prop, anim):
        tree = styled("<div>가</div><p>나</p>", css)
        div = find_el(tree, "div")[0]
        div.animations = {prop: anim}
        from wbe.layout.boxes import DocumentLayout
        doc = DocumentLayout(tree)
        doc.layout()
        cmds = []
        paint_tree(doc, cmds)
        return cmds

    def test_static_page_is_one_layer(self):
        _, cmds = build("<p>가</p><p>나</p>")
        self.assertEqual(len(composite(cmds)), 1)

    def test_paint_chunks_flatten(self):
        _, cmds = build("<p>가</p>")
        item, effects = paint_chunks(cmds)[0]
        self.assertTrue(hasattr(item, "execute"))

    def test_opacity_animation_gets_a_layer(self):
        cmds = self.animated("div { opacity: 1; }", "opacity",
                             NumericAnimation(1, 0, 30))
        self.assertGreater(len(composite(cmds)), 1)

    def test_transform_animation_gets_a_layer(self):
        cmds = self.animated("div { transform: translate(0px, 0px); }",
                             "transform",
                             TranslateAnimation("translate(0px, 0px)",
                                                "translate(300px, 0px)", 30))
        self.assertGreater(len(composite(cmds)), 1)

    def test_finished_animation_stops_compositing(self):
        anim = TranslateAnimation("translate(0px,0px)",
                                  "translate(1px,0px)", 1)
        anim.frame_count = 1
        cmds = self.animated("div { transform: translate(0px, 0px); }",
                             "transform", anim)
        self.assertEqual(len(composite(cmds)), 1)

    def test_animated_bounds_widen(self):
        cmds = self.animated("div { transform: translate(0px, 0px); "
                             "background-color: red; }", "transform",
                             TranslateAnimation("translate(0px, 0px)",
                                                "translate(0px, 300px)", 30))
        item, effects = paint_chunks(cmds)[0]
        box = animated_bounds(item, effects)
        self.assertGreaterEqual(box.height, 300)

    def test_far_apart_content_splits(self):
        _, cmds = build(
            '<div style="background-color:red">위</div>'
            '<div style="height:%dpx"></div>'
            '<div style="background-color:blue">아래</div>'
            % (MAX_LAYER_GAP + 500))
        self.assertGreater(len(composite(cmds)), 1)

    def test_continuous_content_merges(self):
        _, cmds = build("<p>줄</p>" * 400)
        self.assertEqual(len(composite(cmds)), 1)

    def test_short_layer_has_no_surface(self):
        layer = CompositedLayer(())
        layer.add(DrawRect(Rect(0, 0, 10, 10), "red"), Rect(0, 0, 10, 10))
        layer.raster()
        self.assertIsNone(layer.surface)

    def test_long_layer_gets_a_surface(self):
        layer = CompositedLayer(())
        for i in range(SHORT_LIST_LIMIT + 1):
            layer.add(DrawRect(Rect(0, i, 10, i + 10), "red"),
                      Rect(0, i, 10, i + 10))
        layer.raster()
        self.assertIsNotNone(layer.surface)

    def test_short_layer_still_draws(self):
        layer = CompositedLayer(())
        layer.add(DrawRect(Rect(0, 0, 20, 20), "red"), Rect(0, 0, 20, 20))
        layer.raster()
        surface = skia.Surface(40, 40)
        with surface as canvas:
            canvas.clear(skia.ColorWHITE)
            DrawCompositedLayer(layer).execute(canvas)
        px = surface.makeImageSnapshot().toarray()[5][5]
        self.assertGreater(int(px[0]), 200)
        self.assertLess(int(px[1]), 60)

    def test_alpha_folds_into_the_draw(self):
        layer = CompositedLayer(())
        for i in range(5):
            layer.add(DrawRect(Rect(0, 0, 20, 20), "red"), Rect(0, 0, 20, 20))
        layer.raster()
        seen = []
        cmd = DrawCompositedLayer(layer)
        cmd.execute = lambda canvas, alpha=1.0, mode=None: seen.append(alpha)
        surface = skia.Surface(40, 40)
        with surface as canvas:
            draw_list([Blend(0.5, None, [cmd])], canvas)
        self.assertEqual(seen, [0.5])

    def test_blur_still_uses_a_layer(self):
        layer = CompositedLayer(())
        layer.add(DrawRect(Rect(0, 0, 20, 20), "red"), Rect(0, 0, 20, 20))
        layer.raster()
        seen = []
        cmd = DrawCompositedLayer(layer)
        cmd.execute = lambda canvas, alpha=1.0, mode=None: seen.append(alpha)
        surface = skia.Surface(40, 40)
        with surface as canvas:
            draw_list([Blend(0.5, None, [cmd], None, 4.0)], canvas)
        self.assertEqual(seen, [1.0])

    def test_draw_list_rewraps_effects(self):
        cmds = self.animated("div { opacity: 1; }", "opacity",
                             NumericAnimation(1, 0, 30))
        drawn = paint_draw_list(composite(cmds))
        self.assertTrue([c for c in flatten(drawn)
                         if isinstance(c, DrawCompositedLayer)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
