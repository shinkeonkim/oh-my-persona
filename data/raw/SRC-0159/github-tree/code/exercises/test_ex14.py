"""14장 연습문제 검증.

    python3 test_ex14.py

말하기는 RecordingSpeaker 로 갈아 끼워 소리 없이 확인한다.
"""

import shutil
import threading
import time
import unittest
import urllib.parse

import ex11
import ex13
import ex14
from ex14 import (Tab, CSSParser, PseudoclassSelector, AccessibilityNode,
                  AccessibilityThread, RecordingSpeaker, PrintSpeaker,
                  MacSaySpeaker, default_speaker, build_accessibility_tree,
                  parse_outline, paint_outline, focus_rects, is_focusable,
                  get_tabindex, focusable_nodes, role_of, media_matches,
                  parse_zoom, effective_zoom, force_colors, dpx,
                  BROWSER_CSS_14, FORCED_COLORS, FOCUS_OUTER_COLOR,
                  FOCUS_INNER_COLOR, READING_HIGHLIGHT, ZOOM_STEP,
                  MIN_ZOOM, MAX_ZOOM)
from ex11 import (DrawText, DrawRect, DrawOutline, Rect, DocumentLayout,
                  flatten, WIDTH)
from ex10 import URL, HTMLParser, Element, Text, tree_to_list, \
    cascade_priority


def data_url(html):
    return URL("data:text/html," + urllib.parse.quote(html))


def make_tab(html, **kwargs):
    kwargs.setdefault("speaker", RecordingSpeaker())
    tab = Tab(None, 500, **kwargs)
    tab.load(data_url(html))
    return tab


def styled(html, css="", media=None):
    tree = HTMLParser(html).parse()
    for node in tree_to_list(tree, []):
        if isinstance(node, Element):
            node.is_focused = node.is_hovered = node.focus_visible = False
    rules = CSSParser(BROWSER_CSS_14, media or {}).parse()
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


class ChapterFourteenBasics(unittest.TestCase):
    """14장 본문 — 포커스, tabindex, 접근성 트리, 다크 모드"""

    def test_focus_pseudoclass_is_parsed(self):
        rules = CSSParser("a:focus { outline: 2px solid black; }").parse()
        self.assertIsInstance(rules[0][0], PseudoclassSelector)

    def test_focus_rule_only_applies_when_focused(self):
        tree = styled('<a href="/x">링크</a>')
        a = find_el(tree, "a")[0]
        self.assertEqual(a.style.get("outline"), None)

    def test_tabindex_makes_a_div_focusable(self):
        tree = styled('<div tabindex="0">글</div>')
        self.assertTrue(is_focusable(find_el(tree, "div")[0]))

    def test_negative_tabindex_is_not_focusable(self):
        tree = styled('<div tabindex="-1">글</div>')
        self.assertFalse(is_focusable(find_el(tree, "div")[0]))

    def test_tab_order_follows_tabindex(self):
        tree = styled('<a href="/a" tabindex="2">가</a>'
                      '<a href="/b" tabindex="1">나</a>')
        nodes = focusable_nodes(tree_to_list(tree, []))
        self.assertEqual(nodes[0].attributes["tabindex"], "1")

    def test_accessibility_tree_has_roles(self):
        tree = styled('<a href="/x">링크</a>')
        a11y = build_accessibility_tree(tree)
        roles = [n.role for n in a11y.flatten()]
        self.assertIn("link", roles)

    def test_dark_mode_media_query(self):
        light = styled('<a href="/x">링크</a>',
                       media={"prefers-color-scheme": "light"})
        dark = styled('<a href="/x">링크</a>',
                      media={"prefers-color-scheme": "dark"})
        self.assertEqual(find_el(light, "a")[0].style["color"], "blue")
        self.assertEqual(find_el(dark, "a")[0].style["color"], "lightblue")

    def test_dpx_scales(self):
        self.assertEqual(dpx(10, 2.0), 20)


class Exercise141(unittest.TestCase):
    """14-1 대비가 좋은 포커스 링"""

    def rings(self):
        tree = styled('<a href="/x">링크</a>')
        a = find_el(tree, "a")[0]
        a.style["outline"] = "2px solid black"
        cmds = []
        return paint_outline(a, cmds, [Rect(10, 10, 60, 30)])

    def test_two_outlines_are_drawn(self):
        self.assertEqual(len(self.rings()), 2)

    def test_outer_is_white_and_thicker(self):
        outer, inner = self.rings()
        self.assertEqual(outer.color, FOCUS_OUTER_COLOR)
        self.assertGreater(outer.thickness, inner.thickness)

    def test_inner_is_dark(self):
        self.assertEqual(self.rings()[1].color, "black")

    def test_outer_surrounds_the_inner(self):
        outer, inner = self.rings()
        self.assertLess(outer.rect.left, inner.rect.left)
        self.assertGreater(outer.rect.right, inner.rect.right)

    def test_no_outline_no_rings(self):
        tree = styled('<a href="/x">링크</a>')
        a = find_el(tree, "a")[0]
        self.assertEqual(paint_outline(a, [], [Rect(0, 0, 10, 10)]), [])

    def test_outline_is_parsed(self):
        self.assertEqual(parse_outline("2px solid black"), (2, "black"))
        self.assertEqual(parse_outline("none"), (None, None))


class Exercise142(unittest.TestCase):
    """14-2 focus 메서드와 이벤트"""

    def test_focus_method_moves_focus(self):
        tab = make_tab('<input id="i" name="q"><script>i.focus()</script>')
        self.assertIs(tab.tab_focus, find_el(tab.nodes, "input")[0])

    def test_focus_event_fires(self):
        tab = make_tab('<input id="i" name="q"><script>window_n = 0;'
                       'i.addEventListener("focus", function(){window_n++});'
                       "</script>")
        tab.js.interp.evaljs("i.focus()")
        self.assertEqual(tab.js.interp.evaljs("window_n"), 1)

    def test_blur_event_fires_when_focus_moves(self):
        tab = make_tab('<input id="a" name="a"><input id="b" name="b">'
                       "<script>window_n = 0;"
                       'a.addEventListener("blur", function(){window_n++});'
                       "</script>")
        tab.js.interp.evaljs("a.focus()")
        tab.js.interp.evaljs("b.focus()")
        self.assertEqual(tab.js.interp.evaljs("window_n"), 1)

    def test_blur_method_clears_focus(self):
        tab = make_tab('<input id="i" name="q"><script>i.focus()</script>')
        tab.js.interp.evaljs("i.blur()")
        self.assertIsNone(tab.tab_focus)

    def test_focus_event_bubbles(self):
        tab = make_tab('<div id="d"><input id="i" name="q"></div>'
                       "<script>window_n = 0;"
                       'd.addEventListener("focus", function(){window_n++});'
                       "</script>")
        tab.js.interp.evaljs("i.focus()")
        self.assertEqual(tab.js.interp.evaljs("window_n"), 1)


class Exercise143(unittest.TestCase):
    """14-3 읽는 동안 요소 강조하기"""

    HTML = '<h1>제목</h1><p>본문</p><a href="/x">링크</a>'

    def test_advance_moves_one_node_at_a_time(self):
        tab = make_tab(self.HTML)
        first = tab.advance_accessibility()
        second = tab.advance_accessibility()
        self.assertIsNot(first, second)

    def test_advance_speaks(self):
        tab = make_tab(self.HTML)
        tab.speaker.spoken.clear()
        tab.advance_accessibility()
        self.assertEqual(len(tab.speaker.spoken), 1)

    def test_advance_wraps_around(self):
        tab = make_tab("<p>하나</p>")
        seen = [tab.advance_accessibility() for _ in range(20)]
        self.assertIs(seen[0], seen[len(tab.accessibility_nodes())])

    def test_highlight_follows_the_focus(self):
        tab = make_tab(self.HTML)
        tab.advance_accessibility()
        tab.advance_accessibility()
        self.assertTrue(tab.reading_highlight())

    def test_highlight_is_painted(self):
        tab = make_tab(self.HTML)
        for _ in range(2):
            tab.advance_accessibility()
        tab.force_render()
        highlights = [c for c in tab.flat_display_list
                      if isinstance(c, DrawRect)
                      and c.color == READING_HIGHLIGHT]
        self.assertTrue(highlights)

    def test_no_highlight_before_reading(self):
        tab = make_tab(self.HTML)
        self.assertEqual(tab.reading_highlight(), [])


class Exercise144(unittest.TestCase):
    """14-4 너비 미디어 쿼리"""

    CSS = "@media (max-width: 400px) { p { color: red; } }"

    def test_matches_when_narrow(self):
        self.assertTrue(media_matches("max-width", "400px", {"width": 300}))

    def test_does_not_match_when_wide(self):
        self.assertFalse(media_matches("max-width", "400px", {"width": 900}))

    def test_rules_are_dropped_when_wide(self):
        tree = styled("<p>글</p>", self.CSS, {"width": 900})
        self.assertEqual(find_el(tree, "p")[0].style["color"], "black")

    def test_rules_apply_when_narrow(self):
        tree = styled("<p>글</p>", self.CSS, {"width": 300})
        self.assertEqual(find_el(tree, "p")[0].style["color"], "red")

    def test_zoom_changes_the_css_width(self):
        tab = make_tab("<p>글</p>")
        wide = tab.media()["width"]
        tab.zoom = 4.0
        self.assertLess(tab.media()["width"], wide)

    def test_zooming_in_can_trigger_the_query(self):
        tab = make_tab("<style>" + self.CSS + "</style><p>글</p>")
        self.assertEqual(find_el(tab.nodes, "p")[0].style["color"], "black")
        tab.zoom = 4.0                      # 800 / 4 = 200px < 400px
        tab.restyle()
        self.assertEqual(find_el(tab.nodes, "p")[0].style["color"], "red")

    def test_min_width_too(self):
        self.assertTrue(media_matches("min-width", "400px", {"width": 900}))


class Exercise145(unittest.TestCase):
    """14-5 혼합 인라인"""

    def test_inline_link_gets_one_rect_on_one_line(self):
        doc, _ = build('<p><a href="/x">a <b>bold</b> link</a></p>')
        tree = doc.node
        a = find_el(tree, "a")[0]
        rects = focus_rects(doc, a)
        self.assertEqual(len(rects), 1)

    def test_rect_covers_all_three_words(self):
        doc, cmds = build('<p><a href="/x">a <b>bold</b> link</a></p>')
        a = find_el(doc.node, "a")[0]
        rect = focus_rects(doc, a)[0]
        for word in ("a", "bold", "link"):
            cmd = next(c for c in of_type(cmds, DrawText) if c.text == word)
            self.assertGreaterEqual(cmd.rect.left, rect.left - 1)
            self.assertLessEqual(cmd.rect.right, rect.right + 1)

    def test_wrapped_inline_gets_several_rects(self):
        doc, _ = build('<p><a href="/x">' + "낱말 " * 60 + "</a></p>")
        a = find_el(doc.node, "a")[0]
        self.assertGreater(len(focus_rects(doc, a)), 1,
                           "여러 줄이면 사각형도 여러 개")

    def test_block_element_gets_its_own_box(self):
        doc, _ = build('<div tabindex="0">글</div>')
        div = find_el(doc.node, "div")[0]
        rects = focus_rects(doc, div)
        self.assertEqual(len(rects), 1)
        box = next(o for o in tree_to_list(doc, [])
                   if isinstance(o, ex11.BlockLayout) and o.element("div"))
        self.assertEqual(rects[0].left, box.x)

    def test_outline_is_painted_on_every_rect(self):
        doc, _ = build('<p><a href="/x">' + "낱말 " * 60 + "</a></p>")
        a = find_el(doc.node, "a")[0]
        a.style["outline"] = "2px solid black"
        rects = focus_rects(doc, a)
        cmds = paint_outline(a, [], rects)
        self.assertEqual(len(cmds), 2 * len(rects))


class Exercise146(unittest.TestCase):
    """14-6 스레드화된 접근성"""

    def test_speaking_runs_on_its_own_thread(self):
        seen = []

        class Watcher(RecordingSpeaker):
            def speak(self, text):
                seen.append(threading.current_thread().name)
        a11y = AccessibilityThread(Watcher())
        a11y.start_thread()
        a11y.speak("안녕")
        self.assertTrue(a11y.wait(2))
        a11y.set_needs_quit()
        self.assertEqual(seen[0], "접근성 스레드")

    def test_speak_returns_immediately(self):
        class Slow(RecordingSpeaker):
            def speak(self, text):
                time.sleep(0.2)
                super().speak(text)
        a11y = AccessibilityThread(Slow())
        a11y.start_thread()
        start = time.time()
        a11y.speak("안녕")
        elapsed = time.time() - start
        a11y.wait(2)
        a11y.set_needs_quit()
        self.assertLess(elapsed, 0.1, "브라우저 스레드를 막으면 안 됩니다")

    def test_queue_is_kept_in_order(self):
        speaker = RecordingSpeaker()
        a11y = AccessibilityThread(speaker)
        for word in ("하나", "둘", "셋"):
            a11y.speak(word)
        while a11y.run_one():
            pass
        self.assertEqual(speaker.spoken, ["하나", "둘", "셋"])

    def test_tab_can_speak_through_the_thread(self):
        speaker = RecordingSpeaker()
        a11y = AccessibilityThread(speaker)
        tab = make_tab("<p>본문</p>", speaker=a11y)
        tab.speak_document()
        while a11y.run_one():
            pass
        self.assertTrue(speaker.spoken)


class Exercise147(unittest.TestCase):
    """14-7 고대비 모드"""

    def test_media_query_matches(self):
        self.assertTrue(media_matches("forced-colors", "active",
                                      {"forced-colors": True}))
        self.assertFalse(media_matches("forced-colors", "active",
                                       {"forced-colors": False}))

    def test_text_becomes_high_contrast(self):
        tree = styled('<p style="color: #777777">글</p>')
        force_colors(tree_to_list(tree, []))
        self.assertEqual(find_el(tree, "p")[0].style["color"],
                         FORCED_COLORS["color"])

    def test_links_keep_a_distinct_color(self):
        tree = styled('<a href="/x">링크</a>')
        force_colors(tree_to_list(tree, []))
        self.assertEqual(find_el(tree, "a")[0].style["color"],
                         FORCED_COLORS["link"])

    def test_backgrounds_are_forced(self):
        tree = styled('<div style="background-color: #ffcccc">글</div>')
        force_colors(tree_to_list(tree, []))
        self.assertEqual(find_el(tree, "div")[0].style["background-color"],
                         FORCED_COLORS["background-color"])

    def test_transparent_backgrounds_stay_transparent(self):
        tree = styled("<div>글</div>")
        force_colors(tree_to_list(tree, []))
        self.assertEqual(
            find_el(tree, "div")[0].style.get("background-color",
                                              "transparent"), "transparent")

    def test_outlines_get_the_contrast_color(self):
        tree = styled('<a href="/x">링크</a>')
        a = find_el(tree, "a")[0]
        a.style["outline"] = "2px solid black"
        force_colors([a])
        self.assertIn(FORCED_COLORS["outline"], a.style["outline"])

    def test_tab_toggles_it(self):
        tab = make_tab('<p style="color:#777777">글</p>')
        tab.forced_colors = True
        tab.restyle()
        self.assertEqual(find_el(tab.nodes, "p")[0].style["color"],
                         FORCED_COLORS["color"])


class Exercise148(unittest.TestCase):
    """14-8 focus-visible"""

    # 이동하지 않는 포커스 대상이라 네트워크를 건드리지 않는다
    HTML = '<div id="d" tabindex="0">누를 것</div>'

    def test_tab_shows_the_ring(self):
        tab = make_tab(self.HTML)
        node = tab.advance_tab()
        self.assertTrue(node.focus_visible)

    def test_click_hides_the_ring(self):
        tab = make_tab(self.HTML)
        text = next(c for c in tab.flat_display_list
                    if getattr(c, "text", None) == "누를")
        tab.click(text.rect.left + 1, text.rect.top + 1 - tab.scroll)
        div = find_el(tab.nodes, "div")[0]
        self.assertTrue(div.is_focused)
        self.assertFalse(div.focus_visible)

    def test_selector_is_parsed(self):
        rules = CSSParser("a:focus-visible { outline: 2px solid black; }") \
            .parse()
        self.assertEqual(rules[0][0].pseudoclass, "focus-visible")

    def test_rule_applies_only_when_visible(self):
        tree = styled('<a href="/x">링크</a>',
                      "a:focus-visible { outline: 3px solid black; }")
        a = find_el(tree, "a")[0]
        a.is_focused, a.focus_visible = True, False
        self.assertFalse(PseudoclassSelector("focus-visible",
                                             ex14.TagSelector("a")).matches(a))
        a.focus_visible = True
        self.assertTrue(PseudoclassSelector("focus-visible",
                                            ex14.TagSelector("a")).matches(a))

    def test_plain_focus_still_matches_after_a_click(self):
        tree = styled('<a href="/x">링크</a>')
        a = find_el(tree, "a")[0]
        a.is_focused, a.focus_visible = True, False
        self.assertTrue(PseudoclassSelector("focus",
                                            ex14.TagSelector("a")).matches(a))


class Exercise149(unittest.TestCase):
    """14-9 OS 통합"""

    def test_mac_backend_is_detected(self):
        speaker = MacSaySpeaker()
        self.assertEqual(speaker.available(), shutil.which("say") is not None)

    def test_default_speaker_prefers_the_os(self):
        speaker = default_speaker()
        if shutil.which("say"):
            self.assertIsInstance(speaker, MacSaySpeaker)
        else:
            self.assertIsInstance(speaker, ex14.Speaker)

    def test_speakers_share_one_interface(self):
        for cls in (PrintSpeaker, RecordingSpeaker, MacSaySpeaker):
            self.assertTrue(hasattr(cls, "speak"))
            self.assertTrue(hasattr(cls, "stop"))

    def test_recording_speaker_is_a_drop_in(self):
        speaker = RecordingSpeaker()
        tab = make_tab("<p>본문</p>", speaker=speaker)
        tab.speak_document()
        self.assertTrue(speaker.spoken)

    @unittest.skipUnless(shutil.which("say"), "say 명령이 없습니다")
    def test_os_speaker_actually_launches(self):
        speaker = MacSaySpeaker()
        speaker.speak("")
        self.assertIsNotNone(speaker.process)
        speaker.stop()


class Exercise1410(unittest.TestCase):
    """14-10 zoom CSS 속성"""

    def test_percent_is_parsed(self):
        self.assertAlmostEqual(parse_zoom("150%"), 1.5)

    def test_number_is_parsed(self):
        self.assertAlmostEqual(parse_zoom("2"), 2.0)

    def test_missing_zoom_is_one(self):
        self.assertEqual(parse_zoom(None), 1.0)
        self.assertEqual(parse_zoom("이상함"), 1.0)

    def test_zoom_applies_to_the_subtree(self):
        tree = styled('<div style="zoom: 200%"><p>글</p></div>')
        p = find_el(tree, "p")[0]
        self.assertAlmostEqual(effective_zoom(p), 2.0)

    def test_nested_zooms_multiply(self):
        tree = styled('<div style="zoom: 2"><div style="zoom: 2">'
                      "<p>글</p></div></div>")
        self.assertAlmostEqual(effective_zoom(find_el(tree, "p")[0]), 4.0)

    def test_siblings_are_unaffected(self):
        tree = styled('<div style="zoom: 2"><p>가</p></div><p>나</p>')
        outside = find_el(tree, "p")[1]
        self.assertAlmostEqual(effective_zoom(outside), 1.0)

    def test_browser_zoom_multiplies_in(self):
        tab = make_tab('<div style="zoom: 2"><p>글</p></div>')
        tab.zoom = 1.5
        self.assertAlmostEqual(tab.node_zoom(find_el(tab.nodes, "p")[0]), 3.0)

    def test_browser_zoom_has_limits(self):
        tab = make_tab("<p>글</p>")
        for _ in range(50):
            tab.zoom_by(ZOOM_STEP)
        self.assertLessEqual(tab.zoom, MAX_ZOOM)
        for _ in range(50):
            tab.zoom_by(1 / ZOOM_STEP)
        self.assertGreaterEqual(tab.zoom, MIN_ZOOM)


class Exercise1411(unittest.TestCase):
    """14-11 소리 내어 말하기"""

    def test_pyttsx_backend_is_available(self):
        try:
            import pyttsx3          # noqa: F401
        except ImportError:
            self.skipTest("pyttsx3 가 없습니다")
        self.assertTrue(hasattr(ex14.PyttsxSpeaker, "speak"))

    def test_speaking_does_not_block_the_event_loop(self):
        """연습문제 14-6 과 함께: 말하기는 다른 스레드에서."""
        class Slow(RecordingSpeaker):
            def speak(self, text):
                time.sleep(0.15)
                super().speak(text)
        a11y = AccessibilityThread(Slow())
        a11y.start_thread()
        tab = make_tab("<p>가</p><p>나</p>", speaker=a11y)
        start = time.time()
        tab.speak_document()
        elapsed = time.time() - start
        a11y.wait(3)
        a11y.set_needs_quit()
        self.assertLess(elapsed, 0.1)

    def test_hovering_speaks_the_node(self):
        tab = make_tab('<a href="https://example.com/" '
                       'style="display:block">링크</a>')
        tab.speaker.spoken.clear()
        tab.build_accessibility()
        a = find_el(tab.nodes, "a")[0]
        tab.speak_node(a)
        self.assertIn("링크", " ".join(tab.speaker.spoken))

    def test_password_is_not_read_aloud(self):
        tab = make_tab('<input name="pw" type="password" value="비밀">')
        tab.build_accessibility()
        node = next(n for n in tab.accessibility_nodes()
                    if n.role == "textbox")
        self.assertNotIn("비밀", node.text())
        self.assertIn("*", node.text())

    def test_document_reading_covers_everything(self):
        tab = make_tab('<h1>제목</h1><p>본문</p><a href="/x">링크</a>')
        tab.speaker.spoken.clear()
        tab.speak_document()
        joined = " ".join(tab.speaker.spoken)
        for word in ("제목", "본문", "링크"):
            self.assertIn(word, joined)


class CarriedForward(unittest.TestCase):
    """1~13장 연습문제가 그대로 도는지"""

    def test_chapter13_keyframes(self):
        tab = make_tab("<style>@keyframes fade { from { opacity: 1; } "
                       "to { opacity: 0; } }</style>"
                       '<div style="animation: fade 2s">글</div>')
        self.assertIn("fade", tab.keyframes)

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

    def test_chapter10_password_stars(self):
        _, cmds = build('<input name="p" type="password" value="abc">')
        self.assertIn("***", [c.text for c in of_type(cmds, DrawText)])

    def test_chapter9_dom(self):
        tab = make_tab('<div id="d"><p>가</p>글자<b>나</b></div>')
        self.assertEqual(tab.js.interp.evaljs("d.children.length"), 2)

    def test_chapter6_important(self):
        tree = styled('<p class="a">글</p>',
                      "p { color: red !important; } .a { color: blue; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "red")

    def test_chapter5_bullets(self):
        _, cmds = build("<ul><li>하나</li><li>둘</li></ul>")
        self.assertEqual(len([c for c in of_type(cmds, DrawRect)
                              if c.color == "black"]), 2)

    def test_chapter3_smallcaps(self):
        _, cmds = build("<abbr>abc</abbr>")
        self.assertIn("ABC", "".join(c.text for c in of_type(cmds, DrawText)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
