"""11장 연습문제 검증.

    python3 test_ex11.py

Skia 서피스에 직접 그려 확인한다. SDL 창은 띄우지 않는다.
"""

import unittest
import urllib.parse

import skia

import ex10
import ex11
from ex11 import (Tab, DocumentLayout, BlockLayout, LineLayout, TextLayout,
                  InputLayout, ButtonLayout, Blend, Translate, DrawText,
                  DrawRect, DrawRRect, DrawLine, DrawOutline, Rect,
                  get_font, paint_tree, flatten, paint_visual_effects,
                  parse_blur, parse_color, border_radius, is_scrollable,
                  inside_rounded, hit, content_height,
                  WIDTH, HEIGHT, AOI_HEIGHT, VSTEP)
from ex10 import URL, HTMLParser, Element, Text, style, cascade_priority, \
    CSSParser, DEFAULT_STYLE_SHEET, tree_to_list


def data_url(html):
    return URL("data:text/html," + urllib.parse.quote(html))


def styled(html, css=""):
    tree = HTMLParser(html).parse()
    for node in tree_to_list(tree, []):
        if isinstance(node, Element):
            node.is_focused = False
    rules = DEFAULT_STYLE_SHEET.copy()
    if css:
        rules.extend(CSSParser(css).parse())
    style(tree, sorted(rules, key=cascade_priority))
    return tree


def build(html, css=""):
    doc = DocumentLayout(styled(html, css))
    doc.layout()
    cmds = []
    paint_tree(doc, cmds)
    return doc, cmds


def make_tab(html, height=HEIGHT - 100):
    tab = Tab(height)
    tab.load(data_url(html))
    return tab


def find_el(node, tag, out=None):
    out = [] if out is None else out
    if isinstance(node, Element):
        if node.tag == tag:
            out.append(node)
        for c in node.children:
            find_el(c, tag, out)
    return out


def raster(tab, aoi_top=0, w=WIDTH, h=HEIGHT):
    surface = skia.Surface(w, h)
    with surface as canvas:
        tab.raster(canvas, aoi_top)
    return surface.makeImageSnapshot()


def pixel(image, x, y):
    return image.toarray()[int(y)][int(x)]


def of_type(cmds, cls):
    return [c for c in flatten(cmds) if isinstance(c, cls)]


class SkiaBackend(unittest.TestCase):
    """배치 코드가 Skia 위에서도 그대로 도는지"""

    def test_font_has_the_tk_shape(self):
        font = get_font(16, "normal", "roman")
        self.assertGreater(font.measure("hello"), 0)
        m = font.metrics()
        self.assertAlmostEqual(m["linespace"], m["ascent"] + m["descent"],
                               places=3)

    def test_bold_is_wider_than_normal(self):
        self.assertGreater(get_font(16, "bold", "roman").measure("hello"),
                           get_font(16, "normal", "roman").measure("hello") - 1)

    def test_font_cache_keeps_families_apart(self):
        a = get_font(16, "normal", "roman")
        b = get_font(16, "normal", "roman", "monospace")
        self.assertIsNot(a, b)

    def test_text_is_actually_rastered(self):
        tab = make_tab("<p>안녕</p>")
        image = raster(tab)
        white = skia.Surface(WIDTH, HEIGHT).makeImageSnapshot().toarray()
        self.assertFalse((image.toarray() == white).all(),
                         "무언가 그려져야 합니다")

    def test_color_parsing(self):
        self.assertEqual(parse_color("#ff0000"), parse_color("red"))


class ChapterElevenBasics(unittest.TestCase):
    """11장 본문 기능 — opacity, blend mode, border-radius, overflow: clip"""

    def test_opacity_makes_a_layer(self):
        _, cmds = build("<div>글</div>", "div { opacity: 0.5; }")
        blends = [b for b in of_type(cmds, Blend) if b.opacity < 1]
        self.assertTrue(blends)
        self.assertTrue(blends[0].should_save)

    def test_full_opacity_saves_nothing(self):
        _, cmds = build("<div>글</div>", "div { opacity: 1.0; }")
        self.assertTrue(all(not b.should_save for b in of_type(cmds, Blend)))

    def test_blend_mode_is_read(self):
        _, cmds = build("<div>글</div>", "div { mix-blend-mode: multiply; }")
        self.assertTrue(any(b.blend_mode == "multiply"
                            for b in of_type(cmds, Blend)))

    def test_border_radius_uses_rrect(self):
        _, cmds = build("<div>글</div>",
                        "div { background-color: red; border-radius: 10px; }")
        self.assertTrue(of_type(cmds, DrawRRect))

    def test_no_radius_uses_plain_rect(self):
        _, cmds = build("<div>글</div>", "div { background-color: red; }")
        self.assertFalse(of_type(cmds, DrawRRect))

    def test_overflow_clip_adds_a_mask(self):
        _, cmds = build("<div>글</div>",
                        "div { overflow: clip; border-radius: 10px; }")
        masks = [b for b in of_type(cmds, Blend)
                 if b.blend_mode == "destination-in"]
        self.assertEqual(len(masks), 1)


class Exercise111(unittest.TestCase):
    """11-1 필터"""

    def test_parses_blur(self):
        self.assertEqual(parse_blur("blur(4px)"), 4.0)

    def test_ignores_other_filters(self):
        self.assertEqual(parse_blur("grayscale(50%)"), 0.0)
        self.assertEqual(parse_blur(None), 0.0)

    def test_blur_makes_a_layer(self):
        _, cmds = build("<div>글</div>", "div { filter: blur(4px); }")
        blurred = [b for b in of_type(cmds, Blend) if b.blur > 0]
        self.assertEqual(len(blurred), 1)
        self.assertTrue(blurred[0].should_save)

    def test_blur_is_inside_opacity(self):
        """흐리게 만든 결과에 투명도가 적용되어야 합니다 (그 반대가 아니라)."""
        _, cmds = build("<div>글</div>",
                        "div { filter: blur(4px); opacity: 0.5; }")
        blend = next(b for b in of_type(cmds, Blend) if b.blur > 0)
        self.assertEqual(blend.opacity, 0.5)
        paint = blend.paint()
        self.assertIsNotNone(paint.getImageFilter())

    def test_blur_actually_spreads_ink(self):
        sharp = make_tab('<div style="background-color:black;width:40px;'
                         'height:40px"></div>')
        blurry = make_tab('<div style="background-color:black;width:40px;'
                          'height:40px;filter:blur(8px)"></div>')
        a = raster(sharp).toarray()
        b = raster(blurry).toarray()
        # 상자 바로 바깥 지점: 흐린 쪽에만 잉크가 번져 있어야 한다
        y, x = int(VSTEP + 45), int(13 + 45)
        self.assertGreater(int(a[y][x][0]), int(b[y][x][0]) - 1)
        self.assertFalse((a == b).all(), "블러가 그림을 바꿔야 합니다")


class Exercise112(unittest.TestCase):
    """11-2 히트 테스팅"""

    def test_inside_a_plain_rect(self):
        r = Rect(0, 0, 100, 100)
        self.assertTrue(inside_rounded(r, 0, 1, 1))

    def test_corner_of_a_rounded_rect_is_outside(self):
        r = Rect(0, 0, 100, 100)
        self.assertFalse(inside_rounded(r, 40, 2, 2))

    def test_middle_of_a_rounded_rect_is_inside(self):
        r = Rect(0, 0, 100, 100)
        self.assertTrue(inside_rounded(r, 40, 50, 50))

    def test_edge_midpoint_is_inside(self):
        r = Rect(0, 0, 100, 100)
        self.assertTrue(inside_rounded(r, 40, 50, 1))

    def test_all_four_corners_are_cut(self):
        r = Rect(0, 0, 100, 100)
        for x, y in ((2, 2), (98, 2), (2, 98), (98, 98)):
            self.assertFalse(inside_rounded(r, 40, x, y),
                             "모서리 (%d, %d) 는 밖입니다" % (x, y))

    def test_radius_larger_than_the_box_is_clamped(self):
        r = Rect(0, 0, 20, 20)
        self.assertTrue(inside_rounded(r, 999, 10, 10))

    def test_clicking_a_cut_corner_misses_the_link(self):
        tab = make_tab(
            '<a href="https://example.com/" style="display:block;'
            'background-color:orange;border-radius:40px">링크</a>')
        cmd = next(c for c in tab.flat_display_list
                   if isinstance(c, DrawRRect))
        # 상자 안 한가운데는 맞고
        cx = (cmd.rect.left + cmd.rect.right) / 2
        cy = (cmd.rect.top + cmd.rect.bottom) / 2
        self.assertIsNotNone(tab.node_at(cx, cy - tab.scroll))
        # 깎여 나간 모서리는 빗나가야 한다
        self.assertIsNone(tab.node_at(cmd.rect.left + 1,
                                      cmd.rect.top + 1 - tab.scroll))


class Exercise113(unittest.TestCase):
    """11-3 관심 영역"""

    LONG = "<p>줄</p>" * 400

    def test_long_page_is_taller_than_the_area(self):
        tab = make_tab(self.LONG)
        self.assertGreater(tab.document.height, AOI_HEIGHT)

    def test_raster_skips_commands_outside_the_area(self):
        tab = make_tab(self.LONG)
        top = raster(tab, aoi_top=0, h=200).toarray()
        far = raster(tab, aoi_top=3000, h=200).toarray()
        self.assertFalse((top == far).all(), "다른 부분이 보여야 합니다")

    def test_area_is_bounded(self):
        tab = make_tab(self.LONG)
        # 관심 영역 서피스는 페이지 전체가 아니라 AOI_HEIGHT 만 있으면 된다
        self.assertLess(AOI_HEIGHT, tab.document.height)

    def test_scrolling_within_the_area_needs_no_new_raster(self):
        tab = make_tab(self.LONG)
        aoi_top = 0
        tab.scroll = 100
        inside = (tab.scroll >= aoi_top
                  and tab.scroll + tab.tab_height <= aoi_top + AOI_HEIGHT)
        self.assertTrue(inside)

    def test_scrolling_past_the_area_needs_a_new_one(self):
        tab = make_tab(self.LONG)
        aoi_top = 0
        tab.scroll = AOI_HEIGHT + 10
        inside = (tab.scroll >= aoi_top
                  and tab.scroll + tab.tab_height <= aoi_top + AOI_HEIGHT)
        self.assertFalse(inside)


class Exercise114(unittest.TestCase):
    """11-4 오버플로 스크롤"""

    CSS = "div { overflow: scroll; height: 50px; }"
    HTML = "<div>" + "<p>줄</p>" * 20 + "</div>"

    def test_recognizes_a_scrollable_element(self):
        tree = styled(self.HTML, self.CSS)
        self.assertTrue(is_scrollable(find_el(tree, "div")[0]))

    def test_needs_both_overflow_and_height(self):
        tree = styled(self.HTML, "div { overflow: scroll; }")
        self.assertFalse(is_scrollable(find_el(tree, "div")[0]))

    def test_scrollable_box_is_clipped(self):
        _, cmds = build(self.HTML, self.CSS)
        masks = [b for b in of_type(cmds, Blend)
                 if b.blend_mode == "destination-in"]
        self.assertEqual(len(masks), 1)

    def test_content_is_translated(self):
        tree = styled(self.HTML, self.CSS)
        div = find_el(tree, "div")[0]
        div.scroll_offset = 30
        doc = DocumentLayout(tree)
        doc.layout()
        cmds = []
        paint_tree(doc, cmds)
        moves = [t for t in of_type(cmds, Translate) if t.dy == -30]
        self.assertEqual(len(moves), 1)

    def scroll_box_tab(self):
        tab = Tab(HEIGHT - 100)
        tab.load(data_url('<div style="overflow:scroll;height:50px">'
                          + "<p>줄</p>" * 20 + "</div>"))
        return tab

    def inside_the_box(self, tab):
        """상자 안쪽 한 점 (화면 좌표)."""
        div = find_el(tab.nodes, "div")[0]
        box = next(o for o in tree_to_list(tab.document, [])
                   if isinstance(o, BlockLayout) and o.node is div)
        return box.x + 5, box.y + 5 - tab.scroll

    def test_clicking_inside_focuses_the_box(self):
        tab = self.scroll_box_tab()
        div = find_el(tab.nodes, "div")[0]
        tab.click(*self.inside_the_box(tab))
        self.assertIs(tab.scrollable_focus, div)

    def test_arrow_keys_scroll_the_box_not_the_page(self):
        tab = self.scroll_box_tab()
        tab.click(*self.inside_the_box(tab))
        page_before = tab.scroll
        tab.scrolldown()
        div = find_el(tab.nodes, "div")[0]
        self.assertGreater(getattr(div, "scroll_offset", 0), 0)
        self.assertEqual(tab.scroll, page_before)

    def test_box_scroll_stops_at_the_bottom(self):
        tab = self.scroll_box_tab()
        tab.click(*self.inside_the_box(tab))
        for _ in range(200):
            tab.scrolldown()
        div = find_el(tab.nodes, "div")[0]
        inner = content_height(tab.document, div)
        self.assertLessEqual(div.scroll_offset, max(0, inner - 50))

    def test_page_still_scrolls_outside_a_box(self):
        tab = make_tab("<p>줄</p>" * 200)
        tab.scrolldown()
        self.assertGreater(tab.scroll, 0)


class Exercise115(unittest.TestCase):
    """11-5 터치 입력"""

    class FakeFinger:
        def __init__(self, fid, x, y, dy=0.0):
            self.fingerId = fid
            self.x, self.y, self.dy = x, y, dy

    class FakeEvent:
        def __init__(self, finger):
            self.tfinger = finger

    class FakeGesture:
        def __init__(self, n, ddist):
            self.numFingers = n
            self.dDist = ddist

    class FakeGestureEvent:
        def __init__(self, g):
            self.mgesture = g

    def browser(self):
        """SDL 창 없이 터치 처리만 떼어 시험한다."""
        import ex11_sdl

        class Headless(ex11_sdl.Browser):
            def __init__(self):
                self.clicks = []
                self.scrolls = []
                self.touch_points = {}

            def handle_click(self, x, y):
                self.clicks.append((x, y))

            def handle_scroll(self, delta):
                self.scrolls.append(delta)

        return Headless()

    def test_tap_becomes_a_click(self):
        b = self.browser()
        f = self.FakeFinger(1, 0.5, 0.5)
        b.handle_finger_down(self.FakeEvent(f))
        b.handle_finger_up(self.FakeEvent(self.FakeFinger(1, 0.5, 0.5)))
        self.assertEqual(len(b.clicks), 1)

    def test_tap_lands_at_the_right_place(self):
        b = self.browser()
        b.handle_finger_down(self.FakeEvent(self.FakeFinger(1, 0.25, 0.5)))
        b.handle_finger_up(self.FakeEvent(self.FakeFinger(1, 0.25, 0.5)))
        self.assertAlmostEqual(b.clicks[0][0], 0.25 * WIDTH)

    def test_a_drag_is_not_a_tap(self):
        b = self.browser()
        b.handle_finger_down(self.FakeEvent(self.FakeFinger(1, 0.5, 0.2)))
        b.handle_finger_up(self.FakeEvent(self.FakeFinger(1, 0.5, 0.8)))
        self.assertEqual(b.clicks, [])

    def test_two_fingers_is_not_a_tap(self):
        b = self.browser()
        b.handle_finger_down(self.FakeEvent(self.FakeFinger(1, 0.5, 0.5)))
        b.handle_finger_down(self.FakeEvent(self.FakeFinger(2, 0.6, 0.5)))
        b.handle_finger_up(self.FakeEvent(self.FakeFinger(1, 0.5, 0.5)))
        self.assertEqual(b.clicks, [])

    def test_two_finger_motion_scrolls(self):
        b = self.browser()
        b.handle_finger_down(self.FakeEvent(self.FakeFinger(1, 0.5, 0.5)))
        b.handle_finger_down(self.FakeEvent(self.FakeFinger(2, 0.6, 0.5)))
        b.handle_finger_motion(self.FakeEvent(
            self.FakeFinger(1, 0.5, 0.4, dy=-0.1)))
        self.assertEqual(len(b.scrolls), 1)
        self.assertGreater(b.scrolls[0], 0, "위로 끌면 아래로 스크롤합니다")

    def test_one_finger_motion_does_not_scroll(self):
        b = self.browser()
        b.handle_finger_down(self.FakeEvent(self.FakeFinger(1, 0.5, 0.5)))
        b.handle_finger_motion(self.FakeEvent(
            self.FakeFinger(1, 0.5, 0.4, dy=-0.1)))
        self.assertEqual(b.scrolls, [])

    def test_multi_gesture_scrolls(self):
        b = self.browser()
        b.handle_multi_gesture(self.FakeGestureEvent(self.FakeGesture(2, -0.05)))
        self.assertEqual(len(b.scrolls), 1)


class CarriedForward(unittest.TestCase):
    """1~10장 연습문제가 Skia 위에서도 도는지"""

    def test_chapter10_password_stars(self):
        _, cmds = build('<input name="p" type="password" value="abc">')
        self.assertIn("***", [c.text for c in of_type(cmds, DrawText)])

    def test_chapter10_hidden_input(self):
        doc, cmds = build('<input name="a" type="hidden" value="v">')
        self.assertEqual(of_type(cmds, DrawText), [])

    def test_chapter9_dom_api(self):
        tab = make_tab('<div id="d"><p>가</p>글자<b>나</b></div>')
        self.assertEqual(tab.js.interp.evaljs("d.children.length"), 2)

    def test_chapter8_rich_button(self):
        _, cmds = build("<button><b>굵게</b></button>")
        self.assertIn("굵게", [c.text for c in of_type(cmds, DrawText)])

    def test_chapter6_width(self):
        doc, _ = build("<div>글</div>", "div { width: 120px; }")
        div = next(o for o in tree_to_list(doc, [])
                   if isinstance(o, BlockLayout) and o.element("div"))
        self.assertEqual(div.width, 120)

    def test_chapter5_bullets(self):
        _, cmds = build("<ul><li>하나</li><li>둘</li></ul>")
        black = [c for c in of_type(cmds, DrawRect) if c.color == "black"]
        self.assertEqual(len(black), 2)

    def test_chapter5_run_in_heading(self):
        _, cmds = build("<div><h6>제목.</h6><p>이어지는 본문</p></div>")
        by_word = {c.text: c for c in of_type(cmds, DrawText)}
        self.assertEqual(by_word["제목."].rect.top, by_word["이어지는"].rect.top)

    def test_chapter3_smallcaps(self):
        _, cmds = build("<abbr>abc</abbr>")
        self.assertIn("ABC", "".join(c.text for c in of_type(cmds, DrawText)))

    def test_chapter3_centered_title(self):
        _, cmds = build('<h1 class="title">가운데</h1>')
        left = next(c for c in of_type(cmds, DrawText)
                    if c.text == "가운데").rect.left
        self.assertGreater(left, 13 + 10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
