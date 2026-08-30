"""13장 연습문제 검증.

    python3 test_ex13.py

SDL 창 없이 합성·애니메이션 알맹이를 직접 확인한다.
"""

import unittest
import urllib.parse

import skia

import ex11
import ex12
import ex13
from ex13 import (Tab, Transform, Blend, DrawCompositedLayer, CompositedLayer,
                  NumericAnimation, PxAnimation, ColorAnimation,
                  TranslateAnimation, ScrollAnimation, FlingAnimation,
                  parse_transform, parse_transition, parse_easing,
                  parse_keyframes, animation_shorthand, keyframe_animations,
                  diff_styles, cubic_bezier, EASINGS, style, run_animations,
                  paint_chunks, composited_ancestors, composite,
                  paint_draw_list, draw_list, hit_test, z_index, paint_tree,
                  overlaps, animated_bounds, MAX_LAYER_GAP, SHORT_LIST_LIMIT,
                  REFRESH_RATE_SEC, parse_rgb)
from ex11 import (DrawText, DrawRect, DrawRRect, Rect, DocumentLayout,
                  flatten, WIDTH, HEIGHT)
from ex10 import URL, HTMLParser, Element, Text, tree_to_list, CSSParser, \
    cascade_priority, DEFAULT_STYLE_SHEET


def data_url(html):
    return URL("data:text/html," + urllib.parse.quote(html))


def make_tab(html):
    tab = Tab(None, 500)
    tab.load(data_url(html))
    tab.force_render()
    return tab


def styled(html, css="", tab=None, keyframes=None):
    tree = HTMLParser(html).parse()
    for node in tree_to_list(tree, []):
        if isinstance(node, Element):
            node.is_focused = False
    rules = DEFAULT_STYLE_SHEET.copy()
    if css:
        rules.extend(CSSParser(css).parse())
    style(tree, sorted(rules, key=cascade_priority), tab, keyframes)
    return tree


def build(html, css=""):
    doc = DocumentLayout(styled(html, css))
    doc.layout()
    cmds = []
    paint_tree(doc, cmds)
    return doc, cmds


def find_el(node, tag, out=None):
    out = [] if out is None else out
    if isinstance(node, Element):
        if node.tag == tag:
            out.append(node)
        for c in node.children:
            find_el(c, tag, out)
    return out


def of_type(cmds, cls):
    return [c for c in flatten(cmds) if isinstance(c, cls)]


class FakeTab:
    def __init__(self):
        self.layout_asked = 0

    def set_needs_layout(self):
        self.layout_asked += 1


class ChapterThirteenBasics(unittest.TestCase):
    """13장 본문 — transition, transform, 페인트 청크, 합성 레이어"""

    def test_transition_is_parsed(self):
        out = parse_transition("opacity 2s")
        self.assertIn("opacity", out)
        self.assertAlmostEqual(out["opacity"][0], 2 / REFRESH_RATE_SEC,
                               places=3)

    def test_two_transitions(self):
        out = parse_transition("opacity 2s, transform 1s")
        self.assertEqual(set(out), {"opacity", "transform"})

    def test_diff_styles_finds_the_change(self):
        old = {"opacity": "1", "transition": "opacity 2s"}
        new = {"opacity": "0.5", "transition": "opacity 2s"}
        self.assertIn("opacity", diff_styles(old, new))

    def test_no_change_no_transition(self):
        same = {"opacity": "1", "transition": "opacity 2s"}
        self.assertEqual(diff_styles(same, same), {})

    def test_transform_is_parsed(self):
        self.assertEqual(parse_transform("translate(12px, 30px)"), (12.0, 30.0))

    def test_bad_transform_is_none(self):
        self.assertIsNone(parse_transform("rotate(45deg)"))
        self.assertIsNone(parse_transform(None))

    def test_transform_makes_a_transform_effect(self):
        _, cmds = build("<div>글</div>",
                        "div { transform: translate(10px, 20px); }")
        self.assertEqual(len(of_type(cmds, Transform)), 1)

    def test_paint_chunks_flatten_effects(self):
        _, cmds = build("<p>가</p>")
        chunks = paint_chunks(cmds)
        self.assertTrue(chunks)
        item, effects = chunks[0]
        self.assertFalse(ex13.is_effect(item))
        self.assertTrue(all(ex13.is_effect(e) for e in effects))

    def test_static_page_is_one_layer(self):
        _, cmds = build("<p>가</p><p>나</p>")
        self.assertEqual(len(composite(cmds)), 1)


class Exercise131(unittest.TestCase):
    """13-1 background-color"""

    def test_parses_named_colors(self):
        self.assertEqual(parse_rgb("red"), (255, 0, 0))

    def test_interpolates_each_channel(self):
        anim = ColorAnimation("#000000", "#ffffff", 2)
        self.assertEqual(anim.value(0.5), "#808080")

    def test_start_and_end(self):
        anim = ColorAnimation("red", "blue", 10)
        self.assertEqual(anim.value(0.0), "#ff0000")
        self.assertEqual(anim.value(1.0), "#0000ff")

    def test_channels_move_independently(self):
        """빨강은 줄고 초록은 0 인 채로, 파랑만 오릅니다."""
        mid = ColorAnimation("#ff0000", "#0000ff", 10).value(0.5)
        self.assertEqual(mid[3:5], "00", "초록은 움직이지 않습니다")
        self.assertNotEqual(mid[1:3], "ff")
        self.assertNotEqual(mid[5:7], "00")

    def test_background_color_is_animatable(self):
        tab = FakeTab()
        tree = styled("<div>글</div>",
                      "div { background-color: red; transition: "
                      "background-color 1s; }", tab)
        div = find_el(tree, "div")[0]
        div.style["background-color"] = "blue"
        old = dict(div.style)
        old["background-color"] = "red"
        ex13.apply_animations(div, old, tab, None)
        self.assertIsInstance(div.animations["background-color"],
                              ColorAnimation)

    def test_animated_color_reaches_the_paint_command(self):
        tree = styled("<div>글</div>", "div { background-color: red; }")
        div = find_el(tree, "div")[0]
        div.animations = {"background-color":
                          ColorAnimation("red", "blue", 4)}
        run_animations([div])
        doc = DocumentLayout(tree)
        doc.layout()
        cmds = []
        paint_tree(doc, cmds)
        colors = [c.color for c in of_type(cmds, DrawRect)]
        self.assertNotIn("red", colors)


class Exercise132(unittest.TestCase):
    """13-2 이징 함수"""

    def test_linear_is_the_identity(self):
        self.assertAlmostEqual(EASINGS["linear"](0.3), 0.3)

    def test_endpoints_are_exact(self):
        for name, fn in EASINGS.items():
            self.assertAlmostEqual(fn(0.0), 0.0, places=5, msg=name)
            self.assertAlmostEqual(fn(1.0), 1.0, places=5, msg=name)

    def test_ease_in_starts_slow(self):
        self.assertLess(EASINGS["ease-in"](0.25), 0.25)

    def test_ease_out_starts_fast(self):
        self.assertGreater(EASINGS["ease-out"](0.25), 0.25)

    def test_default_is_not_linear(self):
        default = parse_easing(None)
        self.assertNotAlmostEqual(default(0.25), 0.25, places=3)

    def test_cubic_bezier_is_parsed(self):
        fn = parse_easing("cubic-bezier(0.42, 0, 1, 1)")
        self.assertAlmostEqual(fn(0.25), EASINGS["ease-in"](0.25), places=4)

    def test_bad_easing_falls_back(self):
        self.assertAlmostEqual(parse_easing("무슨소리")(0.5),
                               EASINGS["ease"](0.5), places=6)

    def test_transition_takes_an_easing(self):
        out = parse_transition("opacity 1s ease-in")
        self.assertAlmostEqual(out["opacity"][1](0.25),
                               EASINGS["ease-in"](0.25), places=6)

    def test_animation_uses_the_easing(self):
        linear = NumericAnimation(0, 1, 10, EASINGS["linear"])
        eased = NumericAnimation(0, 1, 10, EASINGS["ease-in"])
        for _ in range(3):
            a, b = linear.animate(), eased.animate()
        self.assertLess(float(b), float(a))


class Exercise133(unittest.TestCase):
    """13-3 합성되고 스레드화된 애니메이션"""

    def test_transform_is_animatable(self):
        anim = TranslateAnimation("translate(0px, 0px)",
                                  "translate(100px, 0px)", 10)
        self.assertEqual(anim.value(0.5), "translate(50px, 0px)")

    def test_transform_transition_makes_an_animation(self):
        tab = FakeTab()
        tree = styled("<div>글</div>",
                      "div { transform: translate(0px, 0px); "
                      "transition: transform 1s; }", tab)
        div = find_el(tree, "div")[0]
        old = dict(div.style)
        div.style["transform"] = "translate(50px, 0px)"
        ex13.apply_animations(div, old, tab, None)
        self.assertIsInstance(div.animations["transform"], TranslateAnimation)

    def test_animating_transform_needs_compositing(self):
        tree = styled("<div>글</div>",
                      "div { transform: translate(0px, 0px); }")
        div = find_el(tree, "div")[0]
        div.animations = {"transform": TranslateAnimation(
            "translate(0px, 0px)", "translate(100px, 0px)", 30)}
        doc = DocumentLayout(tree)
        doc.layout()
        cmds = []
        paint_tree(doc, cmds)
        transform = of_type(cmds, Transform)[0]
        self.assertTrue(transform.needs_compositing())

    def test_finished_animation_stops_compositing(self):
        tree = styled("<div>글</div>",
                      "div { transform: translate(0px, 0px); }")
        div = find_el(tree, "div")[0]
        anim = TranslateAnimation("translate(0px,0px)",
                                  "translate(1px,0px)", 1)
        anim.frame_count = 1
        div.animations = {"transform": anim}
        doc = DocumentLayout(tree)
        doc.layout()
        cmds = []
        paint_tree(doc, cmds)
        self.assertFalse(of_type(cmds, Transform)[0].needs_compositing())

    def test_transform_animation_gets_its_own_layer(self):
        tree = styled("<div>가</div><p>나</p>",
                      "div { transform: translate(0px, 0px); }")
        div = find_el(tree, "div")[0]
        div.animations = {"transform": TranslateAnimation(
            "translate(0px, 0px)", "translate(300px, 0px)", 30)}
        doc = DocumentLayout(tree)
        doc.layout()
        cmds = []
        paint_tree(doc, cmds)
        self.assertGreater(len(composite(cmds)), 1)

    def test_opacity_animation_gets_its_own_layer(self):
        tree = styled("<div>가</div><p>나</p>", "div { opacity: 1; }")
        div = find_el(tree, "div")[0]
        div.animations = {"opacity": NumericAnimation(1, 0, 30)}
        doc = DocumentLayout(tree)
        doc.layout()
        cmds = []
        paint_tree(doc, cmds)
        self.assertGreater(len(composite(cmds)), 1)

    def test_draw_list_rewraps_the_effects(self):
        tree = styled("<div>가</div>", "div { opacity: 1; }")
        div = find_el(tree, "div")[0]
        div.animations = {"opacity": NumericAnimation(1, 0, 30)}
        doc = DocumentLayout(tree)
        doc.layout()
        cmds = []
        paint_tree(doc, cmds)
        drawn = paint_draw_list(composite(cmds))
        self.assertTrue(of_type(drawn, DrawCompositedLayer))


class Exercise134(unittest.TestCase):
    """13-4 너비/높이 애니메이션"""

    def test_px_values_round_trip(self):
        anim = PxAnimation("100px", "200px", 10)
        self.assertEqual(anim.value(0.5), "150px")

    def test_produces_px_suffix(self):
        self.assertTrue(PxAnimation("0px", "10px", 4).value(1.0).endswith("px"))

    def test_width_animation_needs_layout(self):
        self.assertTrue(PxAnimation("0px", "1px", 4).needs_layout)

    def test_opacity_animation_does_not_need_layout(self):
        self.assertFalse(NumericAnimation(0, 1, 4).needs_layout)

    def test_starting_a_width_transition_asks_for_layout(self):
        tab = FakeTab()
        tree = styled("<div>글</div>",
                      "div { width: 100px; transition: width 1s; }", tab)
        div = find_el(tree, "div")[0]
        old = dict(div.style)
        div.style["width"] = "200px"
        ex13.apply_animations(div, old, tab, None)
        self.assertGreater(tab.layout_asked, 0)

    def test_animated_width_changes_the_box(self):
        tree = styled("<div>글</div>", "div { width: 100px; }")
        div = find_el(tree, "div")[0]
        div.animations = {"width": PxAnimation("100px", "300px", 4)}
        run_animations([div])
        doc = DocumentLayout(tree)
        doc.layout()
        box = next(o for o in tree_to_list(doc, [])
                   if isinstance(o, ex11.BlockLayout) and o.element("div"))
        self.assertGreater(box.width, 100)


class Exercise135(unittest.TestCase):
    """13-5 CSS 애니메이션"""

    CSS = ("@keyframes fade { from { opacity: 1; } to { opacity: 0; } }"
           "@keyframes slide { 0% { transform: translate(0px, 0px); }"
           " 100% { transform: translate(100px, 0px); } }")

    def test_keyframes_are_parsed(self):
        out = parse_keyframes(self.CSS)
        self.assertEqual(set(out), {"fade", "slide"})

    def test_from_and_to_become_stops(self):
        out = parse_keyframes(self.CSS)
        self.assertEqual(out["fade"][0.0]["opacity"], "1")
        self.assertEqual(out["fade"][1.0]["opacity"], "0")

    def test_percentages_work_too(self):
        out = parse_keyframes(self.CSS)
        self.assertIn("transform", out["slide"][0.0])

    def test_animation_shorthand(self):
        self.assertEqual(animation_shorthand("fade 2s")[0], "fade")

    def test_animation_makes_an_animation_object(self):
        keyframes = parse_keyframes(self.CSS)
        tree = styled("<div>글</div>", "div { animation: fade 2s; }",
                      None, keyframes)
        div = find_el(tree, "div")[0]
        self.assertIn("opacity", div.animations)

    def test_animation_sets_the_starting_value(self):
        keyframes = parse_keyframes(self.CSS)
        tree = styled("<div>글</div>", "div { animation: fade 2s; }",
                      None, keyframes)
        self.assertEqual(find_el(tree, "div")[0].style["opacity"], "1.0")

    def test_animation_progresses(self):
        keyframes = parse_keyframes(self.CSS)
        tree = styled("<div>글</div>", "div { animation: fade 2s; }",
                      None, keyframes)
        div = find_el(tree, "div")[0]
        for _ in range(10):
            run_animations([div])
        self.assertLess(float(div.style["opacity"]), 1.0)

    def test_unknown_animation_name_is_ignored(self):
        tree = styled("<div>글</div>", "div { animation: 없는것 2s; }",
                      None, parse_keyframes(self.CSS))
        self.assertEqual(find_el(tree, "div")[0].animations, {})

    def test_keyframes_come_from_the_page(self):
        tab = make_tab("<style>" + self.CSS + "</style>"
                       '<div style="animation: fade 2s">글</div>')
        self.assertIn("fade", tab.keyframes)
        div = find_el(tab.nodes, "div")[0]
        self.assertIn("opacity", div.animations)


class Exercise136(unittest.TestCase):
    """13-6 변환 애니메이션에서의 겹침 테스트"""

    def scene(self):
        """움직이는 상자가 가만히 있는 상자 위를 지나가는 데모."""
        tree = styled(
            '<div id="mover">움직임</div><div id="still">가만히</div>',
            "#mover { transform: translate(0px, 0px); "
            "background-color: red; } "
            "#still { background-color: blue; }")
        mover = find_el(tree, "div")[0]
        mover.animations = {"transform": TranslateAnimation(
            "translate(0px, 0px)", "translate(0px, 300px)", 30)}
        doc = DocumentLayout(tree)
        doc.layout()
        cmds = []
        paint_tree(doc, cmds)
        return tree, cmds

    def test_bounds_cover_the_whole_path(self):
        anim = TranslateAnimation("translate(0px, 0px)",
                                  "translate(0px, 300px)", 30)
        box = anim.bounds(Rect(0, 0, 10, 10))
        self.assertEqual(box.top, 0)
        self.assertEqual(box.bottom, 310)

    def test_plain_bounds_would_miss_the_overlap(self):
        rect = Rect(0, 0, 10, 10)
        still = Rect(0, 200, 10, 210)
        self.assertFalse(overlaps(rect, still), "지금 자리로는 안 겹칩니다")
        anim = TranslateAnimation("translate(0px, 0px)",
                                  "translate(0px, 300px)", 30)
        self.assertTrue(overlaps(anim.bounds(rect), still),
                        "지나갈 길까지 보면 겹칩니다")

    def test_animated_bounds_uses_the_animation(self):
        tree, cmds = self.scene()
        chunks = paint_chunks(cmds)
        item, effects = chunks[0]
        wide = animated_bounds(item, effects)
        self.assertGreaterEqual(wide.bottom - wide.top, 300)

    def test_overlapping_content_gets_its_own_layer(self):
        _, cmds = self.scene()
        self.assertGreater(len(composite(cmds)), 1)

    def test_no_animation_no_widening(self):
        tree = styled("<div>글</div>",
                      "div { transform: translate(0px, 10px); }")
        doc = DocumentLayout(tree)
        doc.layout()
        cmds = []
        paint_tree(doc, cmds)
        item, effects = paint_chunks(cmds)[0]
        box = animated_bounds(item, effects)
        self.assertLess(box.bottom - box.top, 200)


class Exercise137(unittest.TestCase):
    """13-7 희소한 합성 레이어 피하기"""

    def test_nearby_chunks_merge(self):
        layer = CompositedLayer(())
        layer.add(DrawRect(Rect(0, 0, 10, 10), "red"), (), Rect(0, 0, 10, 10))
        self.assertTrue(layer.can_merge((), Rect(0, 20, 10, 30)))

    def test_far_apart_chunks_do_not_merge(self):
        layer = CompositedLayer(())
        layer.add(DrawRect(Rect(0, 0, 10, 10), "red"), (), Rect(0, 0, 10, 10))
        far = Rect(0, MAX_LAYER_GAP + 100, 10, MAX_LAYER_GAP + 110)
        self.assertFalse(layer.can_merge((), far))

    def test_different_ancestors_never_merge(self):
        layer = CompositedLayer(("가짜",))
        layer.add(DrawRect(Rect(0, 0, 10, 10), "red"), (), Rect(0, 0, 10, 10))
        self.assertFalse(layer.can_merge((), Rect(0, 0, 10, 10)))

    def test_far_apart_content_makes_two_layers(self):
        """사이가 텅 빈 채로 아주 멀리 떨어진 두 덩어리."""
        _, cmds = build(
            '<div style="background-color:red">위</div>'
            '<div style="height:%dpx"></div>'
            '<div style="background-color:blue">아래</div>'
            % (MAX_LAYER_GAP + 500))
        self.assertGreater(len(composite(cmds)), 1)

    def test_continuous_content_still_merges(self):
        """줄줄이 이어진 긴 페이지는 희소하지 않으므로 합쳐도 됩니다."""
        _, cmds = build("<p>줄</p>" * 400)
        self.assertEqual(len(composite(cmds)), 1)

    def test_a_short_page_stays_one_layer(self):
        _, cmds = build("<p>줄</p>" * 5)
        self.assertEqual(len(composite(cmds)), 1)


class Exercise138(unittest.TestCase):
    """13-8 짧은 디스플레이 리스트"""

    def test_short_layer_has_no_surface(self):
        layer = CompositedLayer(())
        layer.add(DrawRect(Rect(0, 0, 10, 10), "red"), (), Rect(0, 0, 10, 10))
        layer.raster()
        self.assertIsNone(layer.surface)

    def test_long_layer_gets_a_surface(self):
        layer = CompositedLayer(())
        for i in range(SHORT_LIST_LIMIT + 1):
            layer.add(DrawRect(Rect(0, i, 10, i + 10), "red"), (),
                      Rect(0, i, 10, i + 10))
        layer.raster()
        self.assertIsNotNone(layer.surface)

    def test_short_layer_still_draws(self):
        layer = CompositedLayer(())
        layer.add(DrawRect(Rect(0, 0, 20, 20), "red"), (), Rect(0, 0, 20, 20))
        layer.raster()
        surface = skia.Surface(40, 40)
        with surface as canvas:
            canvas.clear(skia.ColorWHITE)
            DrawCompositedLayer(layer).execute(canvas)
        px = surface.makeImageSnapshot().toarray()[5][5]
        self.assertGreater(int(px[0]), 200)
        self.assertLess(int(px[1]), 60)

    def test_short_layer_respects_opacity(self):
        layer = CompositedLayer(())
        layer.add(DrawRect(Rect(0, 0, 20, 20), "red"), (), Rect(0, 0, 20, 20))
        layer.raster()
        surface = skia.Surface(40, 40)
        with surface as canvas:
            canvas.clear(skia.ColorWHITE)
            DrawCompositedLayer(layer).execute(canvas, 0.5)
        px = surface.makeImageSnapshot().toarray()[5][5]
        self.assertGreater(int(px[1]), 60, "반투명이면 흰 바탕이 비칩니다")


class Exercise139(unittest.TestCase):
    """13-9 히트 테스팅"""

    def test_finds_the_node_under_the_point(self):
        _, cmds = build("<p>글자</p>")
        text = of_type(cmds, DrawText)[0]
        node = hit_test(cmds, text.rect.left + 1, text.rect.top + 1)
        self.assertIsInstance(node, Text)

    def test_misses_outside(self):
        _, cmds = build("<p>글자</p>")
        self.assertIsNone(hit_test(cmds, 5000, 5000))

    def test_transform_moves_the_hit_area(self):
        _, cmds = build("<div>글자</div>",
                        "div { transform: translate(100px, 0px); }")
        text = of_type(cmds, DrawText)[0]
        # 변환 전 자리에서는 맞고
        self.assertIsNotNone(hit_test(cmds, text.rect.left + 1 + 100,
                                      text.rect.top + 1))

    def test_topmost_wins(self):
        _, cmds = build('<div style="background-color:red">글자</div>')
        node = hit_test(cmds, 20, 25)
        self.assertIsNotNone(node)

    def test_rounded_corner_still_misses(self):
        _, cmds = build("<div>글</div>",
                        "div { background-color: red; border-radius: 40px; "
                        "width: 100px; height: 100px; }")
        rrect = of_type(cmds, DrawRRect)[0]
        self.assertIsNone(hit_test(cmds, rrect.rect.left + 1,
                                   rrect.rect.top + 1))

    def test_tab_uses_local_hit_testing(self):
        tab = make_tab('<a href="https://example.com/" '
                       'style="display:block">링크</a>')
        text = next(c for c in tab.flat_display_list
                    if getattr(c, "text", None) == "링크")
        node = tab.node_at(text.rect.left + 1, text.rect.top + 1 - tab.scroll)
        self.assertIsNotNone(node)


class Exercise1310(unittest.TestCase):
    """13-10 z-index"""

    def test_default_is_zero(self):
        tree = styled("<div>글</div>")
        self.assertEqual(z_index(find_el(tree, "div")[0]), 0)

    def test_static_position_ignores_z_index(self):
        tree = styled("<div>글</div>", "div { z-index: 5; }")
        self.assertEqual(z_index(find_el(tree, "div")[0]), 0)

    def test_relative_position_honors_it(self):
        tree = styled("<div>글</div>",
                      "div { position: relative; z-index: 5; }")
        self.assertEqual(z_index(find_el(tree, "div")[0]), 5)

    def test_negative_z_index(self):
        tree = styled("<div>글</div>",
                      "div { position: relative; z-index: -1; }")
        self.assertEqual(z_index(find_el(tree, "div")[0]), -1)

    def test_higher_z_index_paints_later(self):
        _, cmds = build('<div id="a">가</div><div id="b">나</div>',
                        "#a { position: relative; z-index: 5; } "
                        "#b { position: relative; z-index: 1; }")
        order = [c.text for c in of_type(cmds, DrawText)]
        self.assertEqual(order, ["나", "가"], "z-index 가 큰 쪽이 나중에")

    def test_equal_z_index_keeps_document_order(self):
        _, cmds = build('<div id="a">가</div><div id="b">나</div>',
                        "div { position: relative; z-index: 1; }")
        self.assertEqual([c.text for c in of_type(cmds, DrawText)],
                         ["가", "나"])

    def test_bad_z_index_is_zero(self):
        tree = styled("<div>글</div>",
                      "div { position: relative; z-index: 이상함; }")
        self.assertEqual(z_index(find_el(tree, "div")[0]), 0)


class Exercise1311(unittest.TestCase):
    """13-11 애니메이션 스크롤"""

    def test_scroll_animation_reaches_the_target(self):
        anim = ScrollAnimation(0, 100, 5)
        last = 0
        while not anim.done():
            last = anim.animate()
        self.assertAlmostEqual(last, 100, places=3)

    def test_scroll_animation_is_gradual(self):
        anim = ScrollAnimation(0, 100, 5)
        first = anim.animate()
        self.assertGreater(first, 0)
        self.assertLess(first, 100)

    def test_retarget_keeps_going(self):
        anim = ScrollAnimation(0, 100, 5)
        anim.animate()
        anim.retarget(200)
        while not anim.done():
            last = anim.animate()
        self.assertAlmostEqual(last, 200, places=3)

    def test_tab_scrolls_smoothly(self):
        tab = make_tab("<p>줄</p>" * 200)
        target = tab.smooth_scroll_by(100)
        self.assertGreater(target, 0)
        self.assertEqual(tab.scroll, 0, "아직 옮기지 않았습니다")
        tab.run_animation_frame(None)
        self.assertGreater(tab.scroll, 0)
        self.assertLess(tab.scroll, target)

    def test_smooth_scroll_finishes(self):
        tab = make_tab("<p>줄</p>" * 200)
        target = tab.smooth_scroll_by(100)
        for _ in range(20):
            tab.run_animation_frame(None)
        self.assertAlmostEqual(tab.scroll, target, places=3)
        self.assertIsNone(tab.scroll_animation)

    def test_fling_slows_down(self):
        anim = FlingAnimation(0, 60, 10000)
        steps = []
        while not anim.done():
            steps.append(anim.animate())
        gaps = [b - a for a, b in zip(steps, steps[1:])]
        self.assertLess(gaps[-1], gaps[0], "마찰로 잦아들어야 합니다")

    def test_fling_stops_at_the_top(self):
        anim = FlingAnimation(50, -60, 10000)
        while not anim.done():
            anim.animate()
        self.assertEqual(anim.scroll, 0)

    def test_fling_stops_at_the_bottom(self):
        anim = FlingAnimation(0, 100, 200)
        while not anim.done():
            anim.animate()
        self.assertEqual(anim.scroll, 200)


class Exercise1312(unittest.TestCase):
    """13-12 불투명도와 그리기"""

    def layer_with(self, n=5):
        layer = CompositedLayer(())
        for i in range(n):
            layer.add(DrawRect(Rect(0, 0, 20, 20), "red"), (),
                      Rect(0, 0, 20, 20))
        layer.raster()
        return layer

    def test_execute_takes_an_alpha(self):
        layer = self.layer_with()
        surface = skia.Surface(40, 40)
        with surface as canvas:
            canvas.clear(skia.ColorWHITE)
            DrawCompositedLayer(layer).execute(canvas, 0.5)
        px = surface.makeImageSnapshot().toarray()[5][5]
        self.assertGreater(int(px[1]), 60)

    def test_full_alpha_is_opaque(self):
        layer = self.layer_with()
        surface = skia.Surface(40, 40)
        with surface as canvas:
            canvas.clear(skia.ColorWHITE)
            DrawCompositedLayer(layer).execute(canvas, 1.0)
        px = surface.makeImageSnapshot().toarray()[5][5]
        self.assertLess(int(px[1]), 60)

    def test_draw_list_folds_the_blend_in(self):
        layer = self.layer_with()
        seen = []
        cmd = DrawCompositedLayer(layer)
        cmd.execute = lambda canvas, alpha=1.0, mode=None: seen.append(alpha)
        blend = Blend(0.5, None, [cmd])
        surface = skia.Surface(40, 40)
        with surface as canvas:
            draw_list([blend], canvas)
        self.assertEqual(seen, [0.5], "서피스를 두 번 거치지 않습니다")

    def test_blur_still_uses_a_layer(self):
        layer = self.layer_with()
        seen = []
        cmd = DrawCompositedLayer(layer)
        cmd.execute = lambda canvas, alpha=1.0, mode=None: seen.append(alpha)
        blend = Blend(0.5, None, [cmd], None, 4.0)
        surface = skia.Surface(40, 40)
        with surface as canvas:
            draw_list([blend], canvas)
        self.assertEqual(seen, [1.0], "블러가 있으면 층을 떠야 합니다")


class CarriedForward(unittest.TestCase):
    """1~12장 연습문제가 그대로 도는지"""

    def test_chapter12_interval(self):
        tab = make_tab("<p>가</p><script>window_n = 0;"
                       "window_h = setInterval(function(){window_n++}, 5);"
                       "</script>")
        handle = next(iter(tab.js.interval_handles))
        tab.js.dispatch_setinterval(handle, 5)
        self.assertEqual(tab.js.interp.evaljs("window_n"), 1)
        tab.js.interval_handles.clear()

    def test_chapter11_blur(self):
        _, cmds = build("<div>글</div>", "div { filter: blur(4px); }")
        self.assertTrue([b for b in of_type(cmds, ex11.Blend) if b.blur > 0])

    def test_chapter11_overflow_scroll(self):
        _, cmds = build("<div>" + "<p>줄</p>" * 20 + "</div>",
                        "div { overflow: scroll; height: 50px; }")
        self.assertTrue(of_type(cmds, Transform))

    def test_chapter10_password(self):
        _, cmds = build('<input name="p" type="password" value="abc">')
        self.assertIn("***", [c.text for c in of_type(cmds, DrawText)])

    def test_chapter9_dom(self):
        tab = make_tab('<div id="d"><p>가</p>글자<b>나</b></div>')
        self.assertEqual(tab.js.interp.evaljs("d.children.length"), 2)

    def test_chapter5_bullets(self):
        _, cmds = build("<ul><li>하나</li><li>둘</li></ul>")
        self.assertEqual(len([c for c in of_type(cmds, DrawRect)
                              if c.color == "black"]), 2)

    def test_chapter3_smallcaps(self):
        _, cmds = build("<abbr>abc</abbr>")
        self.assertIn("ABC", "".join(c.text for c in of_type(cmds, DrawText)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
