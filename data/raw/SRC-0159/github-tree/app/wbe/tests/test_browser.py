"""탭, 프레임, 크롬, 브라우저 — 사용자가 하는 일들."""

import time
import unittest

from wbe.a11y import (AccessibilityThread, MacSaySpeaker, RecordingSpeaker,
                      build_accessibility_tree, default_speaker,
                      frame_tab_order, is_focusable, next_focus)
from wbe.browser import Browser
from wbe.chrome import LOCK
from wbe.dom.nodes import Element, tree_to_list
from wbe.frame import Frame, History
from wbe.net import cookies as cookiejar
from wbe.net.url import URL, form_encode
from wbe.paint.commands import DrawRect, DrawText
from wbe.scheduling import (FrameScheduler, FrameTimeEstimator, MeasureTime,
                            REFRESH_RATE_SEC, RasterDrawThread, STARVATION_LIMIT,
                            Task, TaskQueue, TaskRunner, PRIORITY_INPUT,
                            PRIORITY_RENDER, PRIORITY_TIMER, parallel_fetch)
from wbe.tab import (BOOKMARKS, FlingAnimation, ScrollAnimation, Tab,
                     ZOOM_STEP, MAX_ZOOM, MIN_ZOOM, address_to_url,
                     is_bookmarked, looks_like_url, toggle_bookmark)
from wbe.tests.helpers import (by_id, data_url, doc_url, drawn, find_el,
                               make_tab, png_url)


class TestTabBasics(unittest.TestCase):
    def test_loads_and_draws(self):
        tab = make_tab("<h1>제목</h1><p>본문</p>")
        self.assertIn("제목", drawn(tab))
        self.assertIn("본문", drawn(tab))

    def test_title_from_title_tag(self):
        tab = make_tab("<head><title>제목입니다</title></head><body>본문</body>")
        self.assertEqual(tab.title(), "제목입니다")

    def test_title_falls_back_to_url(self):
        tab = make_tab("<p>제목 없음</p>")
        self.assertEqual(tab.title(), str(tab.url))

    def test_view_source_highlights(self):
        tab = Tab(None, 500)
        url = URL("view-source:" + doc_url("<p>글</p>"))
        tab.load(url)
        self.assertIn("<p>", drawn(tab))

    def test_scroll_is_clamped(self):
        tab = make_tab("<p>줄</p>" * 200)
        tab.scroll_by(-1000)
        self.assertEqual(tab.scroll, 0)
        tab.scroll_by(1000000)
        self.assertLessEqual(tab.scroll, tab.root_frame.max_scroll())

    def test_resize_changes_wrapping(self):
        tab = make_tab("<p>" + "낱말 " * 60 + "</p>")
        wide = len({c.rect.top for c in tab.flat_display_list
                    if hasattr(c, "text")})
        tab.resize(300, 500)
        narrow = len({c.rect.top for c in tab.flat_display_list
                      if hasattr(c, "text")})
        self.assertGreater(narrow, wide)

    def test_resize_triggers_media_query(self):
        tab = make_tab("<style>@media (max-width: 400px) "
                       "{ p { color: red; } }</style><p>글</p>")
        self.assertEqual(find_el(tab.nodes, "p")[0].style["color"], "black")
        tab.resize(300, 500)
        self.assertEqual(find_el(tab.nodes, "p")[0].style["color"], "red")

    def test_zoom_limits(self):
        tab = make_tab("<p>글</p>")
        for _ in range(50):
            tab.zoom_by(ZOOM_STEP)
        self.assertLessEqual(tab.zoom, MAX_ZOOM)
        for _ in range(50):
            tab.zoom_by(1 / ZOOM_STEP)
        self.assertGreaterEqual(tab.zoom, MIN_ZOOM)

    def test_zoom_changes_media_width(self):
        tab = make_tab("<p>글</p>")
        wide = tab.root_frame.media()["width"]
        tab.zoom = 4.0
        self.assertLess(tab.root_frame.media()["width"], wide)

    def test_dark_mode(self):
        tab = make_tab('<a href="/x">링크</a>')
        self.assertEqual(find_el(tab.nodes, "a")[0].style["color"], "blue")
        tab.toggle_dark_mode()
        self.assertEqual(find_el(tab.nodes, "a")[0].style["color"],
                         "lightblue")

    def test_forced_colors(self):
        tab = make_tab('<p style="color:#777777">글</p>')
        tab.toggle_forced_colors()
        self.assertEqual(find_el(tab.nodes, "p")[0].style["color"], "#ffffff")


class TestInteraction(unittest.TestCase):
    def click_word(self, tab, word):
        cmd = next(c for c in tab.flat_display_list
                   if getattr(c, "text", None) == word)
        return tab.click(cmd.rect.left + 1, cmd.rect.top + 1 - tab.scroll)

    def test_click_focuses_a_div(self):
        tab = make_tab('<div id="d" tabindex="0">누를 것</div>')
        self.click_word(tab, "누를")
        div = by_id(tab.nodes, "d")
        self.assertTrue(div.is_focused)

    def test_click_focus_is_not_visible(self):
        """클릭으로 얻은 포커스는 링을 보여 주지 않는다."""
        tab = make_tab('<div id="d" tabindex="0">누를 것</div>')
        self.click_word(tab, "누를")
        self.assertFalse(by_id(tab.nodes, "d").focus_visible)

    def test_tab_focus_is_visible(self):
        tab = make_tab('<div id="d" tabindex="0">누를 것</div>')
        node = tab.advance_tab()
        self.assertTrue(node.focus_visible)

    def test_checkbox_toggles(self):
        tab = make_tab('<form action="/a"><input id="c" name="c" '
                       'type="checkbox"></form>')
        from wbe.layout.embed import InputLayout
        from wbe.tests.helpers import layouts
        box = layouts(tab.document, InputLayout)[0]
        tab.click(box.x + 2, box.y + 2 - tab.scroll)
        self.assertIn("checked", by_id(tab.nodes, "c").attributes)
        box = layouts(tab.document, InputLayout)[0]
        tab.click(box.x + 2, box.y + 2 - tab.scroll)
        self.assertNotIn("checked", by_id(tab.nodes, "c").attributes)

    def test_click_handler_prevent_default(self):
        tab = make_tab('<a id="a" href="https://example.com/" '
                       'style="display:block">링크</a>'
                       "<script>a.addEventListener('click',function(e){"
                       "e.preventDefault()});</script>")
        self.assertIsNone(self.click_word(tab, "링크"))

    def test_keypress_into_input(self):
        tab = make_tab('<form action="/a"><input id="i" name="q"></form>')
        tab.root_frame.focus_element(by_id(tab.nodes, "i"))
        for c in "abc":
            tab.keypress(c)
        self.assertEqual(by_id(tab.nodes, "i").attributes["value"], "abc")

    def test_backspace_in_input(self):
        tab = make_tab('<form action="/a"><input id="i" name="q" '
                       'value="abc"></form>')
        tab.root_frame.focus_element(by_id(tab.nodes, "i"))
        tab.backspace()
        self.assertEqual(by_id(tab.nodes, "i").attributes["value"], "ab")

    def test_hover_changes_style(self):
        tab = make_tab("<style>div:hover { background-color: red; }"
                       "div { display: block; background-color: blue; }"
                       "</style><div id='d'>글자</div>")
        cmd = next(c for c in tab.flat_display_list
                   if getattr(c, "text", None) == "글자")
        self.assertTrue(tab.hover(cmd.rect.left + 1,
                                  cmd.rect.top + 1 - tab.scroll))
        self.assertEqual(by_id(tab.nodes, "d").style["background-color"],
                         "red")

    def test_hover_same_node_is_noop(self):
        tab = make_tab("<div id='d'>글자</div>")
        cmd = next(c for c in tab.flat_display_list
                   if getattr(c, "text", None) == "글자")
        x, y = cmd.rect.left + 1, cmd.rect.top + 1 - tab.scroll
        self.assertTrue(tab.hover(x, y))
        self.assertFalse(tab.hover(x, y))

    def test_scrollable_element_found(self):
        tab = make_tab('<div style="overflow:scroll;height:50px">'
                       + "<p>줄</p>" * 20 + "</div>")
        from wbe.layout.boxes import BlockLayout
        from wbe.tests.helpers import layouts
        div = find_el(tab.nodes, "div")[0]
        box = next(o for o in layouts(tab.document, BlockLayout)
                   if o.node is div)
        self.assertIs(tab.scrollable_at(box.x + 5, box.y + 5), div)

    def test_scrolling_a_box_does_not_move_the_page(self):
        tab = make_tab('<div style="overflow:scroll;height:50px">'
                       + "<p>줄</p>" * 20 + "</div>")
        div = find_el(tab.nodes, "div")[0]
        tab.scroll_by(30, target=div)
        self.assertGreater(getattr(div, "scroll_offset", 0), 0)
        self.assertEqual(tab.scroll, 0)


class TestForms(unittest.TestCase):
    HTML = ('<form action="/submit" method="post">'
            '<input name="q" value="hi">'
            '<input name="p" type="password" value="비밀">'
            '<input name="h" type="hidden" value="v">'
            '<input name="c" type="checkbox" value="yes">'
            "<button>보내기</button></form>")

    def tab(self):
        tab = make_tab(self.HTML)
        tab.root_frame.url = URL("http://localhost:8000/page")
        return tab

    def test_pairs(self):
        tab = self.tab()
        form = find_el(tab.nodes, "form")[0]
        self.assertEqual(form_encode(tab.root_frame.form_pairs(form)),
                         "q=hi&p=%EB%B9%84%EB%B0%80&h=v")

    def test_checked_box_is_included(self):
        tab = self.tab()
        find_el(tab.nodes, "input")[3].attributes["checked"] = ""
        form = find_el(tab.nodes, "form")[0]
        self.assertIn("c=yes",
                      form_encode(tab.root_frame.form_pairs(form)))

    def test_post_has_a_body(self):
        tab = self.tab()
        sent = []
        tab.root_frame.load = lambda url, payload=None, record=True: \
            sent.append((str(url), payload))
        tab.root_frame.submit_form(find_el(tab.nodes, "button")[0])
        self.assertEqual(sent[0][1], "q=hi&p=%EB%B9%84%EB%B0%80&h=v")

    def test_get_has_no_body(self):
        tab = make_tab('<form action="/search" method="get">'
                       '<input name="q" value="웹 브라우저">'
                       "<button>찾기</button></form>")
        tab.root_frame.url = URL("http://localhost:8000/page")
        sent = []
        tab.root_frame.load = lambda url, payload=None, record=True: \
            sent.append((str(url), payload))
        tab.root_frame.submit_form(find_el(tab.nodes, "button")[0])
        self.assertIsNone(sent[0][1])
        self.assertIn("?q=", sent[0][0])
        self.assertIn("+", sent[0][0])

    def test_enter_submits(self):
        tab = self.tab()
        sent = []
        tab.root_frame.load = lambda url, payload=None, record=True: \
            sent.append(payload)
        tab.root_frame.focus_element(find_el(tab.nodes, "input")[0])
        tab.enter()
        self.assertEqual(len(sent), 1)

    def test_submit_event_can_cancel(self):
        tab = make_tab('<form id="f" action="/a" method="post">'
                       '<input name="q" value="1"><button>보내기</button>'
                       "</form><script>f.addEventListener('submit',"
                       "function(e){e.preventDefault()});</script>")
        tab.root_frame.url = URL("http://localhost:8000/page")
        sent = []
        tab.root_frame.load = lambda *a, **k: sent.append(a)
        tab.root_frame.submit_form(find_el(tab.nodes, "button")[0])
        self.assertEqual(sent, [])


class TestHistory(unittest.TestCase):
    def test_forward_undoes_back(self):
        h = History()
        h.visit("a")
        h.visit("b")
        self.assertEqual(h.back().url, "a")
        self.assertEqual(h.forward().url, "b")

    def test_no_forward_without_back(self):
        h = History()
        h.visit("a")
        h.visit("b")
        self.assertIsNone(h.forward())

    def test_new_visit_clears_future(self):
        h = History()
        h.visit("a")
        h.visit("b")
        h.back()
        h.visit("c")
        self.assertFalse(h.can_forward())

    def test_back_stops_at_the_first_page(self):
        h = History()
        h.visit("a")
        self.assertFalse(h.can_back())

    def test_post_is_recorded(self):
        h = History()
        h.visit("a")
        h.visit("b", "POST", "q=1")
        self.assertTrue(h.current().is_post())

    def test_tab_back_reloads(self):
        tab = make_tab("<p>가</p>")
        tab.root_frame.load(data_url("<p>나</p>"))
        tab.render()
        tab.go_back()
        self.assertIn("가", drawn(tab))

    def test_back_to_post_asks_first(self):
        tab = make_tab("<p>가</p>")
        tab.root_frame.history.visit(data_url("<p>나</p>"), "POST", "q=1")
        tab.root_frame.history.visit(data_url("<p>다</p>"))
        self.assertIsNone(tab.go_back())

    def test_back_to_post_with_confirmation(self):
        tab = make_tab("<p>가</p>")
        tab.root_frame.history.visit(data_url("<p>나</p>"), "POST", "q=1")
        tab.root_frame.history.visit(data_url("<p>다</p>"))
        posted = []
        tab.root_frame.load = lambda url, payload=None, record=True: \
            posted.append(payload)
        tab.go_back(confirm_resubmit=lambda e: True)
        self.assertEqual(posted, ["q=1"])


class TestFragments(unittest.TestCase):
    HTML = ('<p>위</p>' + '<p>채우기</p>' * 60
            + '<h2 id="target">여기</h2>' + '<p>아래</p>' * 60)

    def test_loading_scrolls(self):
        url = data_url(self.HTML)
        url.fragment = "target"
        tab = Tab(None, 500)
        tab.load(url)
        self.assertGreater(tab.scroll, 0)

    def test_unknown_fragment_ignored(self):
        tab = make_tab(self.HTML)
        self.assertFalse(tab.root_frame.scroll_to("없는id"))

    def test_same_page_link_does_not_reload(self):
        tab = make_tab('<a href="#target">가기</a>' + self.HTML)
        before = tab.nodes
        cmd = next(c for c in tab.flat_display_list
                   if getattr(c, "text", None) == "가기")
        tab.click(cmd.rect.left + 1, cmd.rect.top + 1 - tab.scroll)
        self.assertIs(tab.nodes, before)
        self.assertGreater(tab.scroll, 0)


class TestBookmarksAndSearch(unittest.TestCase):
    def setUp(self):
        self.saved = list(BOOKMARKS)
        del BOOKMARKS[:]

    def tearDown(self):
        del BOOKMARKS[:]
        BOOKMARKS.extend(self.saved)

    def test_toggle(self):
        url = URL("https://example.com/")
        self.assertTrue(toggle_bookmark(url))
        self.assertTrue(is_bookmarked(url))
        self.assertFalse(toggle_bookmark(url))

    def test_about_bookmarks_lists(self):
        BOOKMARKS.append("https://example.com/")
        tab = Tab(None, 500)
        tab.load(URL("about:bookmarks"))
        self.assertIn("Bookmarks", drawn(tab))
        self.assertIn("https://example.com/", drawn(tab))

    def test_search_for_words(self):
        url = address_to_url("웹 브라우저 만들기")
        self.assertEqual(url.host, "google.com")
        self.assertIn("+", url.path)

    def test_bare_host_gets_https(self):
        self.assertEqual(address_to_url("example.com").scheme, "https")

    def test_looks_like_url(self):
        self.assertTrue(looks_like_url("about:blank"))
        self.assertFalse(looks_like_url("파이썬"))


class TestFrames(unittest.TestCase):
    def iframe_tab(self, inner_html="<p>안쪽</p>", attrs=""):
        inner = doc_url(inner_html).replace('"', "%22")
        return make_tab('<p>바깥</p><iframe %s src="%s"></iframe>'
                        % (attrs, inner))

    def test_child_frame_is_created(self):
        tab = self.iframe_tab()
        self.assertEqual(len(tab.frames()), 2)

    def test_content_is_drawn(self):
        tab = self.iframe_tab()
        self.assertIn("바깥", drawn(tab))
        self.assertIn("안쪽", drawn(tab))

    def test_each_frame_has_its_own_history(self):
        tab = self.iframe_tab()
        self.assertIsNot(tab.root_frame.history, tab.frames()[1].history)

    def test_iframe_media_query_uses_its_width(self):
        css = "@media (max-width: 400px) { p { color: red; } }"
        tab = self.iframe_tab("<style>" + css + "</style><p>글</p>")
        child = tab.frames()[1]
        self.assertEqual(find_el(child.nodes, "p")[0].style["color"], "red")

    def test_wide_iframe_does_not_match(self):
        css = "@media (max-width: 400px) { p { color: red; } }"
        tab = self.iframe_tab("<style>" + css + "</style><p>글</p>",
                              attrs='width="900"')
        child = tab.frames()[1]
        self.assertEqual(find_el(child.nodes, "p")[0].style["color"], "black")

    def test_post_message(self):
        tab = self.iframe_tab()
        tab.root_frame.js.interp.evaljs(
            "window_got=''; window.addEventListener('message',"
            "function(e){window_got = e.data});")
        tab.frames()[1].js.interp.evaljs("postMessage('안녕', '*')")
        self.assertEqual(tab.root_frame.js.interp.evaljs("window_got"), "안녕")

    def test_post_message_wrong_origin_dropped(self):
        tab = self.iframe_tab()
        tab.root_frame.js.interp.evaljs(
            "window_got=''; window.addEventListener('message',"
            "function(e){window_got = e.data});")
        tab.frames()[1].js.interp.evaljs(
            "postMessage('틀림', 'http://b.example:80')")
        self.assertEqual(tab.root_frame.js.interp.evaljs("window_got"), "")

    def test_tab_order_spans_frames(self):
        inner = doc_url('<input name="b"><input name="c">').replace('"', "%22")
        tab = make_tab('<input name="a"><iframe src="%s"></iframe>' % inner)
        self.assertEqual(len(frame_tab_order(tab.root_frame)), 3)

    def test_tabbing_moves_into_the_iframe(self):
        inner = doc_url('<input name="b">').replace('"', "%22")
        tab = make_tab('<input name="a"><iframe src="%s"></iframe>' % inner)
        tab.advance_tab()
        node = tab.advance_tab()
        self.assertEqual(node.attributes["name"], "b")

    def test_only_one_element_focused(self):
        inner = doc_url('<input name="b">').replace('"', "%22")
        tab = make_tab('<input name="a"><iframe src="%s"></iframe>' % inner)
        tab.advance_tab()
        tab.advance_tab()
        focused = [n for frame in tab.frames()
                   for n in tree_to_list(frame.nodes)
                   if isinstance(n, Element) and n.is_focused]
        self.assertEqual(len(focused), 1)

    def test_script_added_iframe_loads(self):
        inner = doc_url("<p>새 프레임</p>").replace('"', "%22")
        tab = make_tab('<div id="d"></div>')
        tab.js.interp.evaljs(
            "d.innerHTML = '<iframe src=\"%s\"></iframe>';0;" % inner)
        self.assertEqual(len(tab.frames()), 2)

    def test_script_removed_iframe_unloads(self):
        inner = doc_url("<p>사라짐</p>").replace('"', "%22")
        tab = make_tab('<div id="d"><iframe src="%s"></iframe></div>' % inner)
        self.assertEqual(len(tab.frames()), 2)
        tab.js.interp.evaljs("d.innerHTML = '';0;")
        self.assertEqual(len(tab.frames()), 1)

    def test_x_frame_options_blocks(self):
        tab = make_tab("<p>바깥</p>")
        inner_url = data_url("<p>비밀</p>")
        real = inner_url.request

        def request(*a, **k):
            out = real(*a, **k)
            inner_url.response_headers = {"x-frame-options": "DENY"}
            return out
        inner_url.request = request
        child = Frame(tab, tab.root_frame, None)
        child.load(inner_url)
        self.assertTrue(child.blocked)
        words = [c.text for c in child.display_list if hasattr(c, "text")]
        self.assertNotIn("비밀", words)


class TestImages(unittest.TestCase):
    def test_image_loads_and_sizes(self):
        tab = make_tab('<img src="%s">' % png_url(40, 30))
        img = find_el(tab.nodes, "img")[0]
        self.assertEqual((img.image.width(), img.image.height()), (40, 30))

    def test_lazy_image_is_not_loaded(self):
        tab = make_tab('<img src="%s" loading="lazy">' % png_url())
        self.assertIsNone(find_el(tab.nodes, "img")[0].image)

    def test_forcing_loads_it(self):
        tab = make_tab('<img src="%s" loading="lazy">' % png_url())
        img = find_el(tab.nodes, "img")[0]
        tab.root_frame.load_image(img, force=True)
        self.assertIsNotNone(img.image)

    def test_background_image(self):
        tab = make_tab('<div style="background-image: url(%s)">글</div>'
                       % png_url())
        div = find_el(tab.nodes, "div")[0]
        self.assertIsNotNone(div.background_image)

    def test_background_image_is_under_the_text(self):
        from wbe.paint.commands import DrawImage
        tab = make_tab('<div style="background-image: url(%s)">글</div>'
                       % png_url())
        items = tab.flat_display_list
        image_i = next(i for i, c in enumerate(items)
                       if isinstance(c, DrawImage))
        text_i = next(i for i, c in enumerate(items)
                      if isinstance(c, DrawText))
        self.assertLess(image_i, text_i)


class TestAccessibility(unittest.TestCase):
    HTML = '<h1>제목</h1><p>본문</p><a href="/x">링크</a>'

    def test_roles(self):
        tab = make_tab(self.HTML)
        roles = [n.role for n in tab.accessibility_nodes()]
        self.assertIn("heading", roles)
        self.assertIn("link", roles)

    def test_speak_document_covers_everything(self):
        tab = make_tab(self.HTML)
        tab.speaker.spoken.clear()
        tab.speak_document()
        joined = " ".join(tab.speaker.spoken)
        for word in ("제목", "본문", "링크"):
            self.assertIn(word, joined)

    def test_password_is_not_read_aloud(self):
        tab = make_tab('<input name="pw" type="password" value="비밀">')
        node = next(n for n in tab.accessibility_nodes()
                    if n.role == "textbox")
        self.assertNotIn("비밀", node.text())
        self.assertIn("*", node.text())

    def test_advance_moves_and_speaks(self):
        tab = make_tab(self.HTML)
        tab.speaker.spoken.clear()
        first = tab.advance_accessibility()
        second = tab.advance_accessibility()
        self.assertIsNot(first, second)
        self.assertEqual(len(tab.speaker.spoken), 2)

    def test_reading_highlight_is_painted(self):
        from wbe.a11y import READING_HIGHLIGHT
        tab = make_tab(self.HTML)
        for _ in range(2):
            tab.advance_accessibility()
        self.assertTrue([c for c in tab.flat_display_list
                         if isinstance(c, DrawRect)
                         and c.color == READING_HIGHLIGHT])

    def test_tabindex_makes_a_div_focusable(self):
        tab = make_tab('<div tabindex="0">글</div>')
        self.assertTrue(is_focusable(find_el(tab.nodes, "div")[0]))

    def test_negative_tabindex_is_not(self):
        tab = make_tab('<div tabindex="-1">글</div>')
        self.assertFalse(is_focusable(find_el(tab.nodes, "div")[0]))

    def test_tab_order_follows_tabindex(self):
        tab = make_tab('<a href="/a" tabindex="2">가</a>'
                       '<a href="/b" tabindex="1">나</a>')
        first = tab.advance_tab()
        self.assertEqual(first.attributes["tabindex"], "1")

    def test_next_focus_wraps(self):
        self.assertEqual(next_focus(["가", "나"], "나"), "가")
        self.assertIsNone(next_focus([], None))

    def test_speaker_backends_share_an_interface(self):
        for cls in (RecordingSpeaker, MacSaySpeaker):
            self.assertTrue(hasattr(cls, "speak"))
            self.assertTrue(hasattr(cls, "stop"))

    def test_default_speaker_is_a_speaker(self):
        from wbe.a11y import Speaker
        self.assertIsInstance(default_speaker(), Speaker)

    def test_thread_does_not_block(self):
        class Slow(RecordingSpeaker):
            def speak(self, text):
                time.sleep(0.15)
                super().speak(text)
        a11y = AccessibilityThread(Slow())
        a11y.start_thread()
        start = time.time()
        a11y.speak("안녕")
        elapsed = time.time() - start
        a11y.wait(3)
        a11y.set_needs_quit()
        self.assertLess(elapsed, 0.1)

    def test_queue_order(self):
        speaker = RecordingSpeaker()
        a11y = AccessibilityThread(speaker)
        for word in ("하나", "둘", "셋"):
            a11y.speak(word)
        while a11y.run_one():
            pass
        self.assertEqual(speaker.spoken, ["하나", "둘", "셋"])


class TestScheduling(unittest.TestCase):
    def test_task_name_from_function(self):
        def my_job():
            pass
        self.assertEqual(Task(my_job).name, "my_job")

    def test_trace_event_recorded(self):
        measure = MeasureTime()

        def my_job():
            pass
        Task(my_job, measure=measure).run()
        self.assertIn("Task:my_job", measure.names())

    def test_trace_recorded_even_on_error(self):
        measure = MeasureTime()

        def boom():
            raise ValueError("일부러")
        with self.assertRaises(ValueError):
            Task(boom, measure=measure).run()
        self.assertIn("Task:boom", measure.names())

    def test_render_goes_first(self):
        q = TaskQueue()
        q.add(Task(lambda: None, priority=PRIORITY_TIMER, name="타이머"))
        q.add(Task(lambda: None, priority=PRIORITY_RENDER, name="렌더"))
        self.assertEqual(q.next_task().name, "렌더")

    def test_same_priority_keeps_order(self):
        q = TaskQueue()
        for i in range(3):
            q.add(Task(lambda: None, priority=PRIORITY_INPUT, name=str(i)))
        self.assertEqual([q.next_task().name for _ in range(3)],
                         ["0", "1", "2"])

    def test_timers_are_not_starved(self):
        q = TaskQueue()
        q.add(Task(lambda: None, priority=PRIORITY_TIMER, name="타이머"))
        for _ in range(STARVATION_LIMIT):
            q.add(Task(lambda: None, priority=PRIORITY_RENDER, name="렌더"))
        for _ in range(STARVATION_LIMIT):
            q.next_task()
        self.assertEqual(q.next_task().name, "타이머")

    def test_runner_drains_in_priority_order(self):
        runner = TaskRunner()
        order = []
        runner.schedule_task(Task(lambda: order.append("타이머"),
                                  priority=PRIORITY_TIMER))
        runner.schedule_task(Task(lambda: order.append("렌더"),
                                  priority=PRIORITY_RENDER))
        runner.run_tasks()
        self.assertEqual(order[0], "렌더")

    def test_parallel_fetch_keeps_order(self):
        delays = [0.05, 0.01, 0.03]

        def fetch(i):
            time.sleep(delays[i])
            return "결과%d" % i
        out, _ = parallel_fetch([0, 1, 2], fetch)
        self.assertEqual(out, ["결과0", "결과1", "결과2"])

    def test_parallel_fetch_overlaps(self):
        def fetch(_):
            time.sleep(0.1)
            return "x"
        start = time.time()
        parallel_fetch(list(range(4)), fetch)
        self.assertLess(time.time() - start, 0.35)

    def test_parallel_fetch_survives_failure(self):
        def fetch(i):
            if i == 1:
                raise RuntimeError("실패")
            return "결과%d" % i
        out, errors = parallel_fetch([0, 1, 2], fetch)
        self.assertIsNone(out[1])
        self.assertIsNotNone(errors[1])

    def test_frames_do_not_drift(self):
        s = FrameScheduler()
        s.start(0.0)
        self.assertAlmostEqual(s.delay_until_next(0.020),
                               REFRESH_RATE_SEC - 0.020, places=4)

    def test_missed_deadline_snaps(self):
        s = FrameScheduler()
        s.start(0.0)
        delay = s.delay_until_next(0.100)
        self.assertGreater(delay, 0)
        self.assertLessEqual(delay, REFRESH_RATE_SEC + 1e-6)

    def test_estimator_floor(self):
        est = FrameTimeEstimator()
        for _ in range(5):
            est.record(0.001)
        self.assertEqual(est.estimate(), REFRESH_RATE_SEC)

    def test_estimator_rises(self):
        est = FrameTimeEstimator()
        for _ in range(5):
            est.record(0.100)
        self.assertAlmostEqual(est.estimate(), 0.100, places=4)

    def test_slow_page_is_consistently_slow(self):
        est = FrameTimeEstimator()
        s = FrameScheduler(est)
        now, gaps, last = 0.0, [], None
        for _ in range(8):
            now += s.delay_until_next(now)
            if last is not None:
                gaps.append(now - last)
            last = now
            s.frame_started(now)
            now += 0.080
            s.frame_finished(now)
        self.assertLess(max(gaps[-3:]) - min(gaps[-3:]), 0.02)

    def test_raster_thread_runs_elsewhere(self):
        import threading
        rt = RasterDrawThread()
        rt.start_thread()
        seen = []
        rt.submit(lambda: seen.append(threading.current_thread().name))
        rt.wait(2)
        rt.set_needs_quit()
        self.assertEqual(seen[0], "래스터 스레드")


class TestScrollAnimation(unittest.TestCase):
    def test_reaches_the_target(self):
        anim = ScrollAnimation(0, 100, 5)
        last = 0
        while not anim.done():
            last = anim.animate()
        self.assertAlmostEqual(last, 100, places=3)

    def test_is_gradual(self):
        anim = ScrollAnimation(0, 100, 5)
        first = anim.animate()
        self.assertGreater(first, 0)
        self.assertLess(first, 100)

    def test_retarget(self):
        anim = ScrollAnimation(0, 100, 5)
        anim.animate()
        anim.retarget(200)
        while not anim.done():
            last = anim.animate()
        self.assertAlmostEqual(last, 200, places=3)

    def test_tab_smooth_scroll(self):
        tab = make_tab("<p>줄</p>" * 200)
        target = tab.smooth_scroll_by(100)
        self.assertEqual(tab.scroll, 0)
        tab.run_animation_frame()
        self.assertGreater(tab.scroll, 0)
        self.assertLess(tab.scroll, target)

    def test_fling_slows_down(self):
        anim = FlingAnimation(0, 60, 10000)
        steps = []
        while not anim.done():
            steps.append(anim.animate())
        gaps = [b - a for a, b in zip(steps, steps[1:])]
        self.assertLess(gaps[-1], gaps[0])

    def test_fling_stops_at_the_edges(self):
        anim = FlingAnimation(50, -60, 10000)
        while not anim.done():
            anim.animate()
        self.assertEqual(anim.scroll, 0)


class TestChromeAndBrowser(unittest.TestCase):
    def browser(self):
        b = Browser(headless=True)
        return b

    def test_chrome_is_a_real_document(self):
        b = self.browser()
        try:
            self.assertGreater(b.chrome.bottom, 0)
            ids = {n.attributes.get("id")
                   for n in tree_to_list(b.chrome.nodes)
                   if isinstance(n, Element)}
            self.assertIn("newtab", ids)
            self.assertIn("address", ids)
        finally:
            b.handle_quit()

    def test_address_bar_editing(self):
        b = self.browser()
        try:
            b.chrome.focus = "address bar"
            for c in "abc":
                b.chrome.keypress(c)
            self.assertEqual(b.chrome.address.text, "abc")
            b.chrome.backspace()
            self.assertEqual(b.chrome.address.text, "ab")
            b.chrome.left()
            b.chrome.keypress("z")
            self.assertEqual(b.chrome.address.text, "azb")
        finally:
            b.handle_quit()

    def test_lock_for_https(self):
        b = self.browser()
        b.start_threads()
        try:
            b.new_tab(data_url("<p>가</p>"))
            for _ in range(60):
                if b.active_tab.url:
                    break
                time.sleep(0.05)
            b.active_tab.url = URL("https://example.com/")
            b.chrome.render()
            self.assertIn(LOCK, [c.text for c in b.chrome.flat_display_list
                                 if hasattr(c, "text")])
        finally:
            b.handle_quit()

    def test_end_to_end_render(self):
        b = self.browser()
        b.start_threads()
        try:
            b.new_tab(data_url("<h1>안녕</h1><p>세상</p>"))
            for _ in range(60):
                if b.active_tab_display_list:
                    break
                time.sleep(0.05)
            b.do_raster_and_draw()
            words = [c.text for c in
                     __import__("wbe.paint.commands", fromlist=["flatten"])
                     .flatten(b.active_tab_display_list)
                     if hasattr(c, "text")]
            self.assertIn("안녕", words)
            self.assertGreaterEqual(len(b.composited_layers), 1)
            img = b.root_surface.makeImageSnapshot().toarray()
            self.assertFalse((img == img[0][0]).all())
        finally:
            b.handle_quit()

    def test_resize(self):
        b = self.browser()
        try:
            b.handle_resize(400, 300)
            self.assertEqual((b.width, b.height), (400, 300))
            self.assertEqual(b.root_surface.width(), 400)
        finally:
            b.handle_quit()

    def test_touch_tap_becomes_a_click(self):
        b = self.browser()
        try:
            clicks = []
            b.handle_click = lambda x, y, new_tab=False: clicks.append((x, y))

            class F:
                fingerId, x, y, dy = 1, 0.5, 0.5, 0.0
            b.handle_finger_down(F())
            b.handle_finger_up(F())
            self.assertEqual(len(clicks), 1)
        finally:
            b.handle_quit()

    def test_touch_drag_is_not_a_tap(self):
        b = self.browser()
        try:
            clicks = []
            b.handle_click = lambda x, y, new_tab=False: clicks.append((x, y))

            class Down:
                fingerId, x, y, dy = 1, 0.5, 0.2, 0.0

            class Up:
                fingerId, x, y, dy = 1, 0.5, 0.8, 0.0
            b.handle_finger_down(Down())
            b.handle_finger_up(Up())
            self.assertEqual(clicks, [])
        finally:
            b.handle_quit()

    def test_two_finger_motion_scrolls(self):
        b = self.browser()
        try:
            scrolls = []
            b.handle_scroll = lambda delta, smooth=True: scrolls.append(delta)

            class F1:
                fingerId, x, y, dy = 1, 0.5, 0.5, 0.0

            class F2:
                fingerId, x, y, dy = 2, 0.6, 0.5, 0.0

            class Move:
                fingerId, x, y, dy = 1, 0.5, 0.4, -0.1
            b.handle_finger_down(F1())
            b.handle_finger_down(F2())
            b.handle_finger_motion(Move())
            self.assertEqual(len(scrolls), 1)
            self.assertGreater(scrolls[0], 0)
        finally:
            b.handle_quit()


if __name__ == "__main__":
    unittest.main(verbosity=2)
