"""15장 연습문제 검증.

    python3 test_ex15.py

이미지는 그때그때 만든 PNG 를 data: URL 로 넣어 쓴다. 네트워크는 쓰지 않는다.
"""

import base64
import unittest
import urllib.parse

import skia

import ex11
import ex13
import ex14
import ex15
from ex15 import (Tab, Frame, JSContext, ImageLayout, IframeLayout,
                  CanvasLayout, CanvasContext, EmbedLayout, DocumentLayout,
                  BlockLayout, DrawImage, decode_image, request_bytes,
                  resolve, origin_of, object_fit_rect, parse_url_value,
                  parse_aspect_ratio, size_from_ratio, is_lazy, has_alt,
                  placeholder_size, should_hide_broken, frame_allowed,
                  frame_tab_order, next_focus, origin_matches,
                  IFRAME_WIDTH_PX, IFRAME_HEIGHT_PX,
                  IMAGE_PLACEHOLDER_COLOR, BROWSER_CSS_15)
from ex14 import CSSParser, media_matches
from ex11 import DrawText, DrawRect, DrawOutline, Rect, flatten
from ex10 import URL, Element, Text, tree_to_list, cascade_priority


def png(width=20, height=10, color=skia.ColorRED):
    surface = skia.Surface(width, height)
    with surface as canvas:
        canvas.clear(color)
    return surface.makeImageSnapshot().encodeToData().bytes()


def png_url(width=20, height=10):
    return "data:image/png;base64," + \
        base64.b64encode(png(width, height)).decode()


def doc_url(html):
    return "data:text/html," + urllib.parse.quote(html)


def make_tab(html):
    tab = Tab(None, 500)
    tab.load(URL(doc_url(html)))
    return tab


def styled(html, css="", media=None):
    tree = ex15.HTMLParser(html).parse()
    for node in tree_to_list(tree, []):
        if isinstance(node, Element):
            node.is_focused = node.is_hovered = node.focus_visible = False
    rules = CSSParser(BROWSER_CSS_15, media or {}).parse()
    if css:
        rules.extend(CSSParser(css, media or {}).parse())
    ex13.style(tree, sorted(rules, key=cascade_priority), None, None)
    return tree


def build(html, css="", media=None):
    doc = DocumentLayout(styled(html, css, media))
    doc.layout()
    cmds = []
    ex13.paint_tree(doc, cmds)
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


def layouts(doc, cls):
    return [o for o in tree_to_list(doc, []) if isinstance(o, cls)]


class ChapterFifteenBasics(unittest.TestCase):
    """15장 본문 — 이미지, iframe, 프레임, postMessage"""

    def test_image_is_decoded(self):
        self.assertIsNotNone(decode_image(png()))

    def test_image_element_loads(self):
        tab = make_tab('<img src="%s">' % png_url())
        img = find_el(tab.root_frame.nodes, "img")[0]
        self.assertEqual(img.image.width(), 20)

    def test_image_takes_its_natural_size(self):
        tab = make_tab('<img src="%s">' % png_url(40, 30))
        box = layouts(tab.document, ImageLayout)[0]
        self.assertEqual((box.width, box.height), (40, 30))

    def test_iframe_makes_a_child_frame(self):
        inner = doc_url("<p>안쪽</p>")
        tab = make_tab('<iframe src="%s"></iframe>' % inner.replace('"', "%22"))
        self.assertEqual(len(tab.frames()), 2)

    def test_iframe_content_is_drawn(self):
        inner = doc_url("<p>안쪽 문서</p>")
        tab = make_tab('<p>바깥</p><iframe src="%s"></iframe>'
                       % inner.replace('"', "%22"))
        drawn = [c.text for c in tab.flat_display_list if hasattr(c, "text")]
        self.assertIn("바깥", drawn)
        self.assertIn("안쪽", drawn)

    def test_iframe_has_a_default_size(self):
        inner = doc_url("<p>안쪽</p>")
        tab = make_tab('<iframe src="%s"></iframe>' % inner.replace('"', "%22"))
        box = layouts(tab.document, IframeLayout)[0]
        self.assertEqual((box.width, box.height),
                         (IFRAME_WIDTH_PX, IFRAME_HEIGHT_PX))

    def test_post_message_reaches_the_parent(self):
        inner = doc_url('<script>postMessage("안녕", "*")</script>')
        tab = make_tab('<iframe src="%s"></iframe>'
                       "<script>window_got = '';"
                       'window.addEventListener("message", function(e){'
                       "window_got = e.data});</script>"
                       % inner.replace('"', "%22"))
        child = tab.frames()[1]
        child.js.interp.evaljs('postMessage("안녕", "*")')
        self.assertEqual(tab.root_frame.js.interp.evaljs("window_got"), "안녕")


class Exercise151(unittest.TestCase):
    """15-1 canvas 요소"""

    def test_canvas_has_a_default_size(self):
        doc, _ = build("<canvas></canvas>")
        box = layouts(doc, CanvasLayout)[0]
        self.assertEqual((box.width, box.height), (300, 150))

    def test_attributes_set_the_size(self):
        doc, _ = build('<canvas width="100" height="50"></canvas>')
        box = layouts(doc, CanvasLayout)[0]
        self.assertEqual((box.width, box.height), (100, 50))

    def test_get_context_returns_a_context(self):
        tab = make_tab('<canvas id="c"></canvas>'
                       '<script>window_ok = !!c.getContext("2d")</script>')
        self.assertTrue(tab.root_frame.js.interp.evaljs("window_ok"))

    def test_unknown_context_is_null(self):
        tab = make_tab('<canvas id="c"></canvas>'
                       '<script>window_ok = c.getContext("webgl")</script>')
        self.assertIsNone(tab.root_frame.js.interp.evaljs("window_ok"))

    def test_fill_rect_is_drawn(self):
        tab = make_tab('<canvas id="c" width="100" height="50"></canvas>'
                       '<script>var x = c.getContext("2d");'
                       'x.fillStyle = "red"; x.fillRect(5,5,20,20);</script>')
        reds = [c for c in tab.flat_display_list
                if isinstance(c, DrawRect) and c.color == "red"]
        self.assertEqual(len(reds), 1)

    def test_fill_rect_is_placed_inside_the_canvas(self):
        tab = make_tab('<canvas id="c" width="100" height="50"></canvas>'
                       '<script>var x = c.getContext("2d");'
                       'x.fillStyle = "red"; x.fillRect(5,5,20,20);</script>')
        box = layouts(tab.document, CanvasLayout)[0]
        red = next(c for c in tab.flat_display_list
                   if isinstance(c, DrawRect) and c.color == "red")
        self.assertAlmostEqual(red.rect.left, box.x + 5)
        self.assertAlmostEqual(red.rect.top, box.y + 5)

    def test_fill_text_is_drawn(self):
        tab = make_tab('<canvas id="c"></canvas>'
                       '<script>var x = c.getContext("2d");'
                       'x.fillText("그림글자", 10, 20);</script>')
        self.assertIn("그림글자", [c.text for c in tab.flat_display_list
                                if hasattr(c, "text")])

    def test_clear_removes_everything(self):
        tab = make_tab('<canvas id="c"></canvas>'
                       '<script>var x = c.getContext("2d");'
                       'x.fillStyle = "red"; x.fillRect(0,0,10,10);'
                       "x.clearRect(0,0,10,10);</script>")
        reds = [c for c in tab.flat_display_list
                if isinstance(c, DrawRect) and c.color == "red"]
        self.assertEqual(reds, [])


class Exercise152(unittest.TestCase):
    """15-2 배경 이미지"""

    def test_url_value_is_parsed(self):
        self.assertEqual(parse_url_value("url(cat.png)"), "cat.png")
        self.assertEqual(parse_url_value('url("cat.png")'), "cat.png")
        self.assertIsNone(parse_url_value("none"))

    def test_background_image_is_loaded(self):
        tab = make_tab('<div style="background-image: url(%s)">글</div>'
                       % png_url())
        div = find_el(tab.root_frame.nodes, "div")[0]
        self.assertIsNotNone(div.background_image)

    def test_background_image_is_drawn(self):
        tab = make_tab('<div style="background-image: url(%s)">글</div>'
                       % png_url())
        self.assertTrue([c for c in tab.flat_display_list
                         if isinstance(c, DrawImage)])

    def test_background_image_covers_the_box(self):
        tab = make_tab('<div style="background-image: url(%s)">글</div>'
                       % png_url())
        box = next(o for o in tree_to_list(tab.document, [])
                   if isinstance(o, BlockLayout) and o.element("div"))
        image = next(c for c in tab.flat_display_list
                     if isinstance(c, DrawImage))
        self.assertAlmostEqual(image.rect.left, box.x)
        self.assertAlmostEqual(image.rect.right, box.x + box.width)

    def test_background_image_is_under_the_text(self):
        tab = make_tab('<div style="background-image: url(%s)">글</div>'
                       % png_url())
        items = tab.flat_display_list
        image_i = next(i for i, c in enumerate(items)
                       if isinstance(c, DrawImage))
        text_i = next(i for i, c in enumerate(items) if hasattr(c, "text"))
        self.assertLess(image_i, text_i)

    def test_no_background_image_no_command(self):
        tab = make_tab("<div>글</div>")
        self.assertEqual([c for c in tab.flat_display_list
                          if isinstance(c, DrawImage)], [])


class Exercise153(unittest.TestCase):
    """15-3 object-fit"""

    BOX = Rect(0, 0, 100, 100)

    def test_fill_stretches(self):
        out = object_fit_rect(self.BOX, 20, 10, "fill")
        self.assertEqual((out.right - out.left, out.bottom - out.top),
                         (100, 100))

    def test_contain_keeps_the_ratio(self):
        out = object_fit_rect(self.BOX, 20, 10, "contain")
        self.assertAlmostEqual((out.right - out.left) / (out.bottom - out.top),
                               2.0)

    def test_contain_fits_inside(self):
        out = object_fit_rect(self.BOX, 20, 10, "contain")
        self.assertLessEqual(out.right - out.left, 100)
        self.assertLessEqual(out.bottom - out.top, 100)

    def test_cover_fills_the_box(self):
        out = object_fit_rect(self.BOX, 20, 10, "cover")
        self.assertGreaterEqual(out.right - out.left, 100)
        self.assertGreaterEqual(out.bottom - out.top, 100)

    def test_cover_is_centered(self):
        out = object_fit_rect(self.BOX, 20, 10, "cover")
        self.assertAlmostEqual((out.left + out.right) / 2, 50)

    def test_none_keeps_the_natural_size(self):
        out = object_fit_rect(self.BOX, 20, 10, "none")
        self.assertEqual((out.right - out.left, out.bottom - out.top),
                         (20, 10))

    def test_scale_down_never_grows(self):
        out = object_fit_rect(self.BOX, 20, 10, "scale-down")
        self.assertEqual((out.right - out.left, out.bottom - out.top),
                         (20, 10))

    def test_it_reaches_the_draw_command(self):
        tab = make_tab('<img src="%s" width="100" height="100" '
                       'style="object-fit: contain">' % png_url(20, 10))
        cmd = next(c for c in tab.flat_display_list
                   if isinstance(c, DrawImage))
        self.assertAlmostEqual((cmd.rect.right - cmd.rect.left)
                               / (cmd.rect.bottom - cmd.rect.top), 2.0)


class Exercise154(unittest.TestCase):
    """15-4 지연 로딩"""

    def test_lazy_is_detected(self):
        tree = styled('<img src="x.png" loading="lazy">')
        self.assertTrue(is_lazy(find_el(tree, "img")[0]))

    def test_default_is_eager(self):
        tree = styled('<img src="x.png">')
        self.assertFalse(is_lazy(find_el(tree, "img")[0]))

    def test_lazy_image_is_not_loaded(self):
        tab = make_tab('<img src="%s" loading="lazy">' % png_url())
        img = find_el(tab.root_frame.nodes, "img")[0]
        self.assertIsNone(img.image)
        self.assertTrue(img.image_pending)

    def test_eager_image_is_loaded(self):
        tab = make_tab('<img src="%s">' % png_url())
        self.assertIsNotNone(find_el(tab.root_frame.nodes, "img")[0].image)

    def test_forcing_loads_it(self):
        tab = make_tab('<img src="%s" loading="lazy">' % png_url())
        img = find_el(tab.root_frame.nodes, "img")[0]
        tab.root_frame.load_image(img, force=True)
        self.assertIsNotNone(img.image)

    def test_lazy_image_still_lays_out(self):
        doc, _ = build('<img src="x.png" loading="lazy" '
                       'width="50" height="40">')
        box = layouts(doc, ImageLayout)[0]
        self.assertEqual((box.width, box.height), (50, 40))


class Exercise155(unittest.TestCase):
    """15-5 iframe 종횡비"""

    def test_ratio_with_a_slash(self):
        self.assertAlmostEqual(parse_aspect_ratio("16 / 9"), 16 / 9)

    def test_ratio_as_a_number(self):
        self.assertAlmostEqual(parse_aspect_ratio("1.5"), 1.5)

    def test_bad_ratio_is_none(self):
        self.assertIsNone(parse_aspect_ratio("이상함"))
        self.assertIsNone(parse_aspect_ratio("1 / 0"))

    def test_width_gives_height(self):
        self.assertEqual(size_from_ratio(200, None, 2.0, 0, 0), (200, 100))

    def test_height_gives_width(self):
        self.assertEqual(size_from_ratio(None, 100, 2.0, 0, 0), (200, 100))

    def test_both_given_wins(self):
        self.assertEqual(size_from_ratio(10, 10, 2.0, 0, 0), (10, 10))

    def test_iframe_uses_the_ratio(self):
        inner = doc_url("<p>안쪽</p>")
        doc, _ = build('<iframe src="x" width="200" '
                       'style="aspect-ratio: 2"></iframe>')
        box = layouts(doc, IframeLayout)[0]
        self.assertEqual((box.width, box.height), (200, 100))

    def test_image_uses_the_ratio_before_loading(self):
        doc, _ = build('<img src="x.png" loading="lazy" width="200" '
                       'style="aspect-ratio: 4">')
        box = layouts(doc, ImageLayout)[0]
        self.assertEqual((box.width, box.height), (200, 50))


class Exercise156(unittest.TestCase):
    """15-6 이미지 자리 표시자"""

    def test_unknown_size_takes_no_space(self):
        doc, _ = build('<img src="없는.png" loading="lazy">')
        box = layouts(doc, ImageLayout)[0]
        self.assertEqual((box.width, box.height), (0, 0))

    def test_given_size_is_reserved(self):
        doc, _ = build('<img src="없는.png" loading="lazy" '
                       'width="60" height="40">')
        box = layouts(doc, ImageLayout)[0]
        self.assertEqual((box.width, box.height), (60, 40))

    def test_broken_image_without_alt_is_hidden(self):
        tree = styled('<img src="없는.png">')
        self.assertTrue(should_hide_broken(find_el(tree, "img")[0]))

    def test_broken_image_with_alt_is_shown(self):
        tree = styled('<img src="없는.png" alt="고양이">')
        self.assertFalse(should_hide_broken(find_el(tree, "img")[0]))

    def test_hidden_broken_image_paints_nothing(self):
        tab = make_tab('<img src="about:blank" width="50" height="50">')
        self.assertEqual([c for c in tab.flat_display_list
                          if isinstance(c, DrawRect)
                          and c.color == IMAGE_PLACEHOLDER_COLOR], [])

    def test_alt_image_paints_a_placeholder(self):
        tab = make_tab('<img src="about:blank" alt="고양이" '
                       'width="50" height="50">')
        self.assertTrue([c for c in tab.flat_display_list
                         if isinstance(c, DrawRect)
                         and c.color == IMAGE_PLACEHOLDER_COLOR])

    def test_alt_text_is_drawn(self):
        tab = make_tab('<img src="about:blank" alt="고양이" '
                       'width="80" height="50">')
        self.assertIn("고양이", [c.text for c in tab.flat_display_list
                              if hasattr(c, "text")])


class Exercise157(unittest.TestCase):
    """15-7 미디어 쿼리"""

    CSS = "@media (max-width: 400px) { p { color: red; } }"

    def test_matches_by_width(self):
        self.assertTrue(media_matches("max-width", "400px", {"width": 300}))

    def test_wide_frame_does_not_match(self):
        tree = styled("<p>글</p>", self.CSS, {"width": 900})
        self.assertEqual(find_el(tree, "p")[0].style["color"], "black")

    def test_frame_reports_its_own_width(self):
        inner = doc_url("<style>" + self.CSS + "</style><p>글</p>")
        tab = make_tab('<iframe src="%s"></iframe>'
                       % inner.replace('"', "%22"))
        child = tab.frames()[1]
        self.assertEqual(child.media()["width"], child.width)

    def test_narrow_iframe_triggers_the_query(self):
        inner = doc_url("<style>" + self.CSS + "</style><p>글</p>")
        tab = make_tab('<iframe src="%s"></iframe>'
                       % inner.replace('"', "%22"))
        child = tab.frames()[1]
        p = find_el(child.nodes, "p")[0]
        self.assertEqual(p.style["color"], "red",
                         "기본 iframe 너비 300px 는 400px 보다 좁습니다")

    def test_parent_can_widen_the_iframe(self):
        inner = doc_url("<style>" + self.CSS + "</style><p>글</p>")
        tab = make_tab('<iframe width="900" src="%s"></iframe>'
                       % inner.replace('"', "%22"))
        child = tab.frames()[1]
        child.restyle()
        self.assertEqual(find_el(child.nodes, "p")[0].style["color"], "black")

    def test_outer_frame_is_wide(self):
        tab = make_tab("<p>글</p>")
        self.assertEqual(tab.root_frame.media()["width"], ex11.WIDTH)


class Exercise158(unittest.TestCase):
    """15-8 postMessage 의 대상 출처"""

    def test_star_matches_anything(self):
        self.assertTrue(origin_matches("*", "http://a.example:80"))
        self.assertTrue(origin_matches(None, "http://a.example:80"))

    def test_exact_origin_matches(self):
        self.assertTrue(origin_matches("http://a.example:80",
                                       "http://a.example:80"))

    def test_other_origin_does_not(self):
        self.assertFalse(origin_matches("http://b.example:80",
                                        "http://a.example:80"))

    def test_trailing_slash_is_ignored(self):
        self.assertTrue(origin_matches("http://a.example:80/",
                                       "http://a.example:80"))

    def test_message_arrives_with_a_matching_origin(self):
        inner = doc_url("<p>안쪽</p>")
        tab = make_tab('<iframe src="%s"></iframe>'
                       "<script>window_got = '';"
                       'window.addEventListener("message", function(e){'
                       "window_got = e.data});</script>"
                       % inner.replace('"', "%22"))
        child = tab.frames()[1]
        child.js.interp.evaljs('postMessage("맞음", "null")')
        self.assertEqual(tab.root_frame.js.interp.evaljs("window_got"), "맞음")

    def test_message_is_dropped_for_another_origin(self):
        inner = doc_url("<p>안쪽</p>")
        tab = make_tab('<iframe src="%s"></iframe>'
                       "<script>window_got = '';"
                       'window.addEventListener("message", function(e){'
                       "window_got = e.data});</script>"
                       % inner.replace('"', "%22"))
        child = tab.frames()[1]
        child.js.interp.evaljs('postMessage("틀림", "http://b.example:80")')
        self.assertEqual(tab.root_frame.js.interp.evaljs("window_got"), "")

    def test_event_carries_the_sender_origin(self):
        inner = doc_url("<p>안쪽</p>")
        tab = make_tab('<iframe src="%s"></iframe>'
                       "<script>window_origin = null;"
                       'window.addEventListener("message", function(e){'
                       "window_origin = e.origin});</script>"
                       % inner.replace('"', "%22"))
        tab.frames()[1].js.interp.evaljs('postMessage("x", "*")')
        self.assertEqual(tab.root_frame.js.interp.evaljs("window_origin"),
                         "null")


class Exercise159(unittest.TestCase):
    """15-9 다중 프레임 포커스"""

    def two_frames(self):
        inner = doc_url('<input name="b"><input name="c">')
        return make_tab('<input name="a"><iframe src="%s"></iframe>'
                        % inner.replace('"', "%22"))

    def test_order_spans_frames(self):
        tab = self.two_frames()
        order = frame_tab_order(tab.root_frame)
        self.assertEqual(len(order), 3)

    def test_first_tab_lands_in_the_outer_frame(self):
        tab = self.two_frames()
        node = tab.advance_tab()
        self.assertEqual(node.attributes["name"], "a")

    def test_tabbing_moves_into_the_iframe(self):
        tab = self.two_frames()
        tab.advance_tab()
        node = tab.advance_tab()
        self.assertEqual(node.attributes["name"], "b")
        self.assertIs(tab.focused_frame, tab.frames()[1])

    def test_tabbing_wraps_back_to_the_start(self):
        tab = self.two_frames()
        for _ in range(3):
            tab.advance_tab()
        node = tab.advance_tab()
        self.assertEqual(node.attributes["name"], "a")

    def test_only_one_element_is_focused(self):
        tab = self.two_frames()
        for _ in range(2):
            tab.advance_tab()
        focused = [n for frame in tab.frames()
                   for n in tree_to_list(frame.nodes, [])
                   if isinstance(n, Element) and n.is_focused]
        self.assertEqual(len(focused), 1)

    def test_next_focus_helper(self):
        self.assertEqual(next_focus(["가", "나"], "가"), "나")
        self.assertEqual(next_focus(["가", "나"], "나"), "가")
        self.assertIsNone(next_focus([], None))


class Exercise1510(unittest.TestCase):
    """15-10 iframe 방문 기록"""

    def test_each_frame_has_its_own_history(self):
        inner = doc_url("<p>안쪽</p>")
        tab = make_tab('<iframe src="%s"></iframe>'
                       % inner.replace('"', "%22"))
        self.assertIsNot(tab.root_frame.history, tab.frames()[1].history)

    def test_iframe_navigation_is_recorded(self):
        inner = doc_url("<p>하나</p>")
        tab = make_tab('<iframe src="%s"></iframe>'
                       % inner.replace('"', "%22"))
        child = tab.frames()[1]
        child.load(URL(doc_url("<p>둘</p>")))
        self.assertTrue(child.history.can_back())

    def test_back_goes_back_in_the_iframe(self):
        inner = doc_url("<p>하나</p>")
        tab = make_tab('<iframe src="%s"></iframe>'
                       % inner.replace('"', "%22"))
        child = tab.frames()[1]
        child.load(URL(doc_url("<p>둘</p>")))
        tab.go_back()
        drawn = " ".join(c.text for c in flatten(child.display_list)
                         if hasattr(c, "text"))
        self.assertIn("하나", drawn)

    def test_most_recent_navigation_wins(self):
        inner = doc_url("<p>안쪽 하나</p>")
        tab = make_tab('<iframe src="%s"></iframe>'
                       % inner.replace('"', "%22"))
        child = tab.frames()[1]
        tab.root_frame.load(
            URL(doc_url('<p>바깥 둘</p><iframe src="%s"></iframe>'
                        % inner.replace('"', "%22"))))
        newest = tab.last_navigated_frame()
        self.assertIs(newest, tab.root_frame)

    def test_iframe_back_is_chosen_when_it_moved_last(self):
        inner = doc_url("<p>하나</p>")
        tab = make_tab('<iframe src="%s"></iframe>'
                       % inner.replace('"', "%22"))
        child = tab.frames()[1]
        child.load(URL(doc_url("<p>둘</p>")))
        self.assertIs(tab.last_navigated_frame(), child)


class Exercise1511(unittest.TestCase):
    """15-11 스크립트가 추가하거나 제거한 iframe"""

    def test_added_iframe_is_loaded(self):
        inner = doc_url("<p>새 프레임</p>").replace('"', "%22")
        tab = make_tab('<div id="d"></div>')
        tab.root_frame.js.interp.evaljs(
            "d.innerHTML = '<iframe src=\"%s\"></iframe>';0;" % inner)
        self.assertEqual(len(tab.frames()), 2)

    def test_added_iframe_content_is_drawn(self):
        inner = doc_url("<p>새 프레임</p>").replace('"', "%22")
        tab = make_tab('<div id="d"></div>')
        tab.root_frame.js.interp.evaljs(
            "d.innerHTML = '<iframe src=\"%s\"></iframe>';0;" % inner)
        tab.render()
        drawn = [c.text for c in tab.flat_display_list if hasattr(c, "text")]
        self.assertIn("새", drawn)

    def test_removed_iframe_is_unloaded(self):
        inner = doc_url("<p>사라질 것</p>")
        tab = make_tab('<div id="d"><iframe src="%s"></iframe></div>'
                       % inner.replace('"', "%22"))
        self.assertEqual(len(tab.frames()), 2)
        tab.root_frame.js.interp.evaljs("d.innerHTML = '';0;")
        self.assertEqual(len(tab.frames()), 1)

    def test_removed_frame_js_is_discarded(self):
        inner = doc_url("<p>사라질 것</p>")
        tab = make_tab('<div id="d"><iframe src="%s"></iframe></div>'
                       % inner.replace('"', "%22"))
        child = tab.frames()[1]
        tab.root_frame.js.interp.evaljs("d.innerHTML = '';0;")
        self.assertTrue(child.js.discarded)

    def test_added_image_is_loaded(self):
        tab = make_tab('<div id="d"></div>')
        tab.root_frame.js.interp.evaljs(
            "d.innerHTML = '<img src=\"%s\">';0;" % png_url())
        img = find_el(tab.root_frame.nodes, "img")[0]
        self.assertIsNotNone(img.image)


class Exercise1512(unittest.TestCase):
    """15-12 X-Frame-Options"""

    def test_no_header_is_allowed(self):
        self.assertTrue(frame_allowed({}, "http://a:80", "http://b:80"))

    def test_deny_blocks_everything(self):
        self.assertFalse(frame_allowed({"x-frame-options": "DENY"},
                                       "http://a:80", "http://a:80"))

    def test_sameorigin_allows_the_same_origin(self):
        self.assertTrue(frame_allowed({"x-frame-options": "SAMEORIGIN"},
                                      "http://a:80", "http://a:80"))

    def test_sameorigin_blocks_others(self):
        self.assertFalse(frame_allowed({"x-frame-options": "SAMEORIGIN"},
                                       "http://a:80", "http://b:80"))

    def test_case_is_ignored(self):
        self.assertFalse(frame_allowed({"x-frame-options": "deny"},
                                       "http://a:80", "http://a:80"))

    def test_blocked_frame_shows_a_message(self):
        inner_url = URL(doc_url("<p>비밀</p>"))
        tab = Tab(None, 500)
        tab.load(URL(doc_url("<p>바깥</p>")))
        child = Frame(tab, tab.root_frame, None)
        inner_url.response_headers = {"x-frame-options": "DENY"}
        real_request = inner_url.request

        def request(*a, **k):
            out = real_request(*a, **k)
            inner_url.response_headers = {"x-frame-options": "DENY"}
            return out
        inner_url.request = request
        child.load(inner_url)
        self.assertTrue(child.blocked)
        drawn = " ".join(c.text for c in flatten(child.display_list)
                         if hasattr(c, "text"))
        self.assertNotIn("비밀", drawn)


class CarriedForward(unittest.TestCase):
    """1~14장 연습문제가 그대로 도는지"""

    def test_chapter14_focus_ring(self):
        tree = styled('<a href="/x">링크</a>')
        a = find_el(tree, "a")[0]
        a.style["outline"] = "2px solid black"
        self.assertEqual(len(ex14.paint_outline(a, [], [Rect(0, 0, 10, 10)])), 2)

    def test_chapter14_zoom_property(self):
        tree = styled('<div style="zoom: 2"><p>글</p></div>')
        self.assertAlmostEqual(ex14.effective_zoom(find_el(tree, "p")[0]), 2.0)

    def test_chapter13_z_index(self):
        _, cmds = build('<div id="a">가</div><div id="b">나</div>',
                        "#a { position: relative; z-index: 5; } "
                        "#b { position: relative; z-index: 1; }")
        self.assertEqual([c.text for c in of_type(cmds, DrawText)],
                         ["나", "가"])

    def test_chapter11_border_radius(self):
        _, cmds = build("<div>글</div>",
                        "div { background-color: red; border-radius: 10px; }")
        self.assertTrue(of_type(cmds, ex11.DrawRRect))

    def test_chapter10_password(self):
        _, cmds = build('<input name="p" type="password" value="abc">')
        self.assertIn("***", [c.text for c in of_type(cmds, DrawText)])

    def test_chapter9_dom(self):
        tab = make_tab('<div id="d"><p>가</p>글자<b>나</b></div>')
        self.assertEqual(tab.root_frame.js.interp.evaljs("d.children.length"),
                         2)

    def test_chapter5_bullets(self):
        _, cmds = build("<ul><li>하나</li><li>둘</li></ul>")
        self.assertEqual(len([c for c in of_type(cmds, DrawRect)
                              if c.color == "black"]), 2)

    def test_chapter3_smallcaps(self):
        _, cmds = build("<abbr>abc</abbr>")
        self.assertIn("ABC", "".join(c.text for c in of_type(cmds, DrawText)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
