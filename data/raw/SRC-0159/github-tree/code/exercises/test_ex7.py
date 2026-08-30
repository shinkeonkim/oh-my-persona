"""7장 연습문제 검증.

    python3 test_ex7.py

네트워크는 쓰지 않는다. data: URL 과 가짜 탭으로 확인한다.
"""

import tkinter
import unittest
import urllib.parse

import ex7
from ex7 import (URL, Tab, Chrome, Browser, History, AddressBar, Rect,
                 DrawText, DrawRect, DocumentLayout, BlockLayout, LineLayout,
                 TextLayout, HTMLParser, Element, Text, paint_tree,
                 tree_to_list, style, cascade_priority, CSSParser,
                 DEFAULT_STYLE_SHEET, address_to_url, looks_like_url,
                 bookmarks_page, toggle_bookmark, is_bookmarked, base_str,
                 VISITED, BOOKMARKS, VISITED_COLOR, DISABLED_COLOR,
                 BOOKMARK_ON, SEARCH_URL, HEIGHT, VSTEP)

_root = None


def setUpModule():
    global _root
    _root = tkinter.Tk()
    _root.withdraw()


def tearDownModule():
    if _root is not None:
        _root.destroy()


def data_url(html):
    return URL("data:text/html," + urllib.parse.quote(html))


def styled(html, css=""):
    tree = HTMLParser(html).parse()
    rules = DEFAULT_STYLE_SHEET.copy()
    if css:
        rules.extend(CSSParser(css).parse())
    style(tree, sorted(rules, key=cascade_priority))
    return tree


def build(html, css=""):
    tree = styled(html, css)
    doc = DocumentLayout(tree)
    doc.layout()
    cmds = []
    paint_tree(doc, cmds)
    return doc, cmds


def make_tab(html, url=None):
    """네트워크 없이 탭 하나를 띄운다."""
    tab = Tab(HEIGHT - 100)
    tab.load(url or data_url(html))
    return tab


def texts(cmds):
    return [c for c in cmds if isinstance(c, DrawText)]


def find_text(cmds, word):
    return next(c for c in texts(cmds) if c.text == word)


def find_el(node, tag, out=None):
    out = [] if out is None else out
    if isinstance(node, Element):
        if node.tag == tag:
            out.append(node)
        for c in node.children:
            find_el(c, tag, out)
    return out


class Exercise71(unittest.TestCase):
    """7-1 백스페이스"""

    def test_deletes_last_character(self):
        bar = AddressBar("abc")
        bar.backspace()
        self.assertEqual(bar.text, "ab")

    def test_empty_is_safe(self):
        bar = AddressBar("")
        bar.backspace()
        self.assertEqual(bar.text, "")

    def test_repeated(self):
        bar = AddressBar("abc")
        for _ in range(5):
            bar.backspace()
        self.assertEqual(bar.text, "")

    def test_only_when_focused(self):
        browser = FakeBrowser()
        chrome = Chrome(browser)
        chrome.address.set_text("abc")
        chrome.backspace()                 # 포커스 없음
        self.assertEqual(chrome.address.text, "abc")
        chrome.focus = "address bar"
        chrome.backspace()
        self.assertEqual(chrome.address.text, "ab")


class FakeBrowser:
    """Tk 창 없이 Chrome 만 시험하기 위한 최소한의 껍데기."""

    def __init__(self, tabs=None, active=None):
        self.tabs = tabs or []
        self.active_tab = active or (self.tabs[0] if self.tabs else None)

    def new_tab(self, url, background=False):
        tab = Tab(HEIGHT - 100)
        tab.load(url)
        self.tabs.append(tab)
        if not background:
            self.active_tab = tab
        return tab

    def draw(self):
        pass


class Exercise72(unittest.TestCase):
    """7-2 가운데 클릭"""

    HTML = '<a href="data:text/html,%EB%91%98">하나</a>'

    def test_link_at_finds_the_url(self):
        tab = make_tab(self.HTML)
        cmd = find_text(tab.display_list, "하나")
        self.assertIsNotNone(tab.link_at(cmd.rect.left + 1, cmd.rect.top + 1))

    def test_middle_click_opens_background_tab(self):
        browser = FakeBrowser()
        first = browser.new_tab(data_url(self.HTML))
        cmd = find_text(first.display_list, "하나")
        url = first.link_at(cmd.rect.left + 1, cmd.rect.top + 1)
        browser.new_tab(url, background=True)
        self.assertEqual(len(browser.tabs), 2)

    def test_background_tab_does_not_steal_focus(self):
        browser = FakeBrowser()
        first = browser.new_tab(data_url(self.HTML))
        browser.new_tab(data_url("<p>둘</p>"), background=True)
        self.assertIs(browser.active_tab, first)

    def test_click_outside_a_link_is_none(self):
        tab = make_tab("<p>글자만</p>")
        self.assertIsNone(tab.link_at(5, 5))


class Exercise73(unittest.TestCase):
    """7-3 창 제목"""

    def test_title_from_title_tag(self):
        tab = make_tab("<html><head><title>제목입니다</title></head>"
                       "<body>본문</body></html>")
        self.assertEqual(tab.title(), "제목입니다")

    def test_falls_back_to_url(self):
        tab = make_tab("<p>제목 없음</p>")
        self.assertEqual(tab.title(), str(tab.url))

    def test_whitespace_only_title_falls_back(self):
        tab = make_tab("<title>   </title><p>글</p>")
        self.assertEqual(tab.title(), str(tab.url))

    def test_title_not_drawn_on_page(self):
        tab = make_tab("<head><title>제목입니다</title></head><body>본문</body>")
        self.assertNotIn("제목입니다", [c.text for c in texts(tab.display_list)])


class Exercise74(unittest.TestCase):
    """7-4 앞으로 가기"""

    def test_forward_undoes_back(self):
        h = History()
        h.visit("a")
        h.visit("b")
        self.assertEqual(h.back(), "a")
        self.assertEqual(h.forward(), "b")

    def test_forward_does_nothing_without_a_back(self):
        h = History()
        h.visit("a")
        h.visit("b")
        self.assertIsNone(h.forward())
        self.assertEqual(h.current(), "b")

    def test_new_visit_clears_the_future(self):
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
        self.assertIsNone(h.back())

    def test_buttons_are_gray_when_dead(self):
        browser = FakeBrowser()
        browser.new_tab(data_url("<p>가</p>"))
        chrome = Chrome(browser)
        cmds = chrome.paint()
        back = next(c for c in texts(cmds) if c.text == "<")
        fwd = next(c for c in texts(cmds) if c.text == ">")
        self.assertEqual(back.color, DISABLED_COLOR)
        self.assertEqual(fwd.color, DISABLED_COLOR)

    def test_back_button_black_after_two_pages(self):
        browser = FakeBrowser()
        tab = browser.new_tab(data_url("<p>가</p>"))
        tab.load(data_url("<p>나</p>"))
        chrome = Chrome(browser)
        back = next(c for c in texts(chrome.paint()) if c.text == "<")
        self.assertEqual(back.color, "black")

    def test_tab_forward_reloads_the_page(self):
        tab = make_tab("<p>가</p>")
        tab.load(data_url("<p>나</p>"))
        tab.go_back()
        self.assertIn("가", [c.text for c in texts(tab.display_list)])
        tab.go_forward()
        self.assertIn("나", [c.text for c in texts(tab.display_list)])


class Exercise75(unittest.TestCase):
    """7-5 프래그먼트"""

    # 목표가 화면 맨 위까지 올라올 수 있도록 뒤에도 넉넉히 채운다
    HTML = ('<p>위</p>' + '<p>채우기</p>' * 60 +
            '<h2 id="target">여기</h2>' + '<p>아래</p>' * 60)

    def test_url_splits_off_the_fragment(self):
        url = URL("https://example.com/a#sec")
        self.assertEqual(url.fragment, "sec")
        self.assertEqual(url.path, "/a")

    def test_str_keeps_the_fragment(self):
        self.assertTrue(str(URL("https://example.com/a#sec")).endswith("#sec"))

    def test_relative_hash_keeps_the_page(self):
        url = URL("https://example.com/a")
        out = url.resolve("#sec")
        self.assertEqual(out.path, "/a")
        self.assertEqual(out.fragment, "sec")
        self.assertTrue(out.same_page(url))

    def test_loading_scrolls_to_the_element(self):
        url = data_url(self.HTML)
        url.fragment = "target"
        tab = Tab(HEIGHT - 100)
        tab.load(url)
        self.assertGreater(tab.scroll, 0)

    def test_scroll_puts_the_element_near_the_top(self):
        tab = make_tab(self.HTML)
        obj = next(o for o in tree_to_list(tab.document, [])
                   if isinstance(getattr(o, "node", None), Element)
                   and o.node.attributes.get("id") == "target")
        tab.scroll_to("target")
        self.assertAlmostEqual(tab.scroll, obj.y - VSTEP, delta=1)

    def test_unknown_fragment_is_ignored(self):
        tab = make_tab(self.HTML)
        self.assertFalse(tab.scroll_to("없는id"))

    def test_same_page_link_does_not_reload(self):
        tab = make_tab('<a href="#target">가기</a>' + self.HTML)
        before = tab.nodes
        cmd = find_text(tab.display_list, "가기")
        tab.click(cmd.rect.left + 1, cmd.rect.top + 1)
        self.assertIs(tab.nodes, before, "같은 페이지면 다시 읽지 않습니다")
        self.assertGreater(tab.scroll, 0)


class Exercise76(unittest.TestCase):
    """7-6 검색"""

    def test_plain_words_become_a_search(self):
        url = address_to_url("웹 브라우저 만들기")
        self.assertEqual(url.host, "google.com")
        self.assertTrue(url.path.startswith("/search"))
        self.assertIn("+", url.path)

    def test_spaces_become_plus(self):
        self.assertEqual(str(address_to_url("a b c")),
                         str(URL(SEARCH_URL.format("a+b+c"))))

    def test_full_url_is_kept(self):
        url = address_to_url("https://example.com/a")
        self.assertEqual(url.host, "example.com")

    def test_bare_host_gets_https(self):
        url = address_to_url("example.com")
        self.assertEqual(url.scheme, "https")
        self.assertEqual(url.host, "example.com")

    def test_about_is_a_url(self):
        self.assertTrue(looks_like_url("about:bookmarks"))
        self.assertEqual(address_to_url("about:bookmarks").scheme, "about")

    def test_single_word_is_a_search(self):
        self.assertFalse(looks_like_url("파이썬"))
        self.assertIn("search", str(address_to_url("파이썬")))


class Exercise77(unittest.TestCase):
    """7-7 방문한 링크"""

    def setUp(self):
        self._saved = set(VISITED)
        VISITED.clear()

    def tearDown(self):
        VISITED.clear()
        VISITED.update(self._saved)

    def test_unvisited_link_is_blue(self):
        tab = make_tab('<a href="https://example.com/">링크</a>')
        cmd = find_text(tab.display_list, "링크")
        self.assertEqual(cmd.color, "blue")

    def test_visited_link_is_purple(self):
        VISITED.add("https://example.com:443/")
        tab = make_tab('<a href="https://example.com/">링크</a>')
        cmd = find_text(tab.display_list, "링크")
        self.assertEqual(cmd.color, VISITED_COLOR)

    def test_visited_class_is_added(self):
        VISITED.add("https://example.com:443/")
        tab = make_tab('<a href="https://example.com/">링크</a>')
        a = find_el(tab.nodes, "a")[0]
        self.assertIn("visited", a.attributes.get("class", "").split())

    def test_existing_classes_survive(self):
        VISITED.add("https://example.com:443/")
        tab = make_tab('<a class="big" href="https://example.com/">링크</a>')
        a = find_el(tab.nodes, "a")[0]
        self.assertIn("big", a.attributes["class"].split())
        self.assertIn("visited", a.attributes["class"].split())

    def test_loading_records_the_visit(self):
        tab = make_tab("<p>글</p>")
        self.assertIn(base_str(tab.url), VISITED)


class Exercise78(unittest.TestCase):
    """7-8 북마크"""

    def setUp(self):
        self._saved = list(BOOKMARKS)
        del BOOKMARKS[:]

    def tearDown(self):
        del BOOKMARKS[:]
        BOOKMARKS.extend(self._saved)

    def test_toggle_on_and_off(self):
        url = URL("https://example.com/")
        self.assertTrue(toggle_bookmark(url))
        self.assertTrue(is_bookmarked(url))
        self.assertFalse(toggle_bookmark(url))
        self.assertFalse(is_bookmarked(url))

    def test_about_bookmarks_lists_them(self):
        BOOKMARKS.append("https://example.com/")
        self.assertIn("https://example.com/", bookmarks_page())

    def test_empty_page_is_valid_html(self):
        tab = Tab(HEIGHT - 100)
        tab.load(URL("about:bookmarks"))
        self.assertIn("Bookmarks", [c.text for c in texts(tab.display_list)])

    def test_bookmarked_page_has_yellow_button(self):
        browser = FakeBrowser()
        tab = browser.new_tab(data_url("<p>가</p>"))
        chrome = Chrome(browser)
        plain = [c for c in chrome.paint()
                 if isinstance(c, DrawRect) and c.color == BOOKMARK_ON]
        self.assertEqual(plain, [])
        toggle_bookmark(tab.url)
        marked = [c for c in chrome.paint()
                  if isinstance(c, DrawRect) and c.color == BOOKMARK_ON]
        self.assertEqual(len(marked), 1)

    def test_bookmarks_page_links_are_clickable(self):
        BOOKMARKS.append("https://example.com/")
        tab = Tab(HEIGHT - 100)
        tab.load(URL("about:bookmarks"))
        cmd = find_text(tab.display_list, "https://example.com/")
        url = tab.link_at(cmd.rect.left + 1, cmd.rect.top + 1)
        self.assertIsNotNone(url)
        self.assertEqual(url.host, "example.com")


class Exercise79(unittest.TestCase):
    """7-9 커서"""

    def test_cursor_starts_at_the_end(self):
        self.assertEqual(AddressBar("abc").cursor, 3)

    def test_arrows_move_it(self):
        bar = AddressBar("abc")
        bar.left()
        bar.left()
        self.assertEqual(bar.cursor, 1)
        bar.right()
        self.assertEqual(bar.cursor, 2)

    def test_cursor_stays_in_range(self):
        bar = AddressBar("ab")
        for _ in range(5):
            bar.left()
        self.assertEqual(bar.cursor, 0)
        for _ in range(9):
            bar.right()
        self.assertEqual(bar.cursor, 2)

    def test_insert_at_the_cursor(self):
        bar = AddressBar("ac")
        bar.left()
        bar.insert("b")
        self.assertEqual(bar.text, "abc")
        self.assertEqual(bar.cursor, 2)

    def test_backspace_deletes_before_the_cursor(self):
        bar = AddressBar("abc")
        bar.left()
        bar.backspace()
        self.assertEqual(bar.text, "ac")
        self.assertEqual(bar.cursor, 1)

    def test_backspace_at_the_start_does_nothing(self):
        bar = AddressBar("abc")
        bar.home()
        bar.backspace()
        self.assertEqual(bar.text, "abc")

    def test_cursor_is_drawn(self):
        browser = FakeBrowser()
        browser.new_tab(data_url("<p>가</p>"))
        chrome = Chrome(browser)
        chrome.focus = "address bar"
        chrome.address.set_text("abc")
        lines = [c for c in chrome.paint()
                 if isinstance(c, ex7.DrawLine) and c.color == "red"]
        self.assertEqual(len(lines), 1)

    def test_cursor_moves_with_the_text(self):
        browser = FakeBrowser()
        browser.new_tab(data_url("<p>가</p>"))
        chrome = Chrome(browser)
        chrome.focus = "address bar"
        chrome.address.set_text("abc")
        far = next(c for c in chrome.paint()
                   if isinstance(c, ex7.DrawLine) and c.color == "red")
        chrome.address.home()
        near = next(c for c in chrome.paint()
                    if isinstance(c, ex7.DrawLine) and c.color == "red")
        self.assertLess(near.rect.left, far.rect.left)


class Exercise710(unittest.TestCase):
    """7-10 여러 창"""

    def setUp(self):
        self._saved = list(ex7.WINDOWS)
        del ex7.WINDOWS[:]

    def tearDown(self):
        for w in list(ex7.WINDOWS):
            w.window.destroy()
        del ex7.WINDOWS[:]
        ex7.WINDOWS.extend(self._saved)

    def test_new_window_is_registered(self):
        first = Browser(root=_root)
        self.assertEqual(len(ex7.WINDOWS), 1)
        first.handle_new_window(None)
        self.assertEqual(len(ex7.WINDOWS), 2)

    def test_tabs_belong_to_their_window(self):
        a = Browser(root=_root)
        b = Browser(root=_root)
        a.new_tab(data_url("<p>가</p>"))
        b.new_tab(data_url("<p>나</p>"))
        b.new_tab(data_url("<p>다</p>"))
        self.assertEqual(len(a.tabs), 1)
        self.assertEqual(len(b.tabs), 2)

    def test_closing_removes_the_window(self):
        a = Browser(root=_root)
        Browser(root=_root)
        a.close()
        self.assertEqual(len(ex7.WINDOWS), 1)

    def test_each_window_has_its_own_chrome(self):
        a = Browser(root=_root)
        b = Browser(root=_root)
        self.assertIsNot(a.chrome, b.chrome)
        self.assertIs(a.chrome.browser, a)


class Exercise711(unittest.TestCase):
    """7-11 디스플레이 리스트를 통한 클릭"""

    def test_draw_commands_know_their_node(self):
        _, cmds = build("<p>글자</p>")
        cmd = find_text(cmds, "글자")
        self.assertIsInstance(cmd.node, Text)

    def test_click_finds_the_link(self):
        tab = make_tab('<p>앞 <a href="https://example.com/">링크</a> 뒤</p>')
        cmd = find_text(tab.display_list, "링크")
        url = tab.link_at(cmd.rect.left + 1, cmd.rect.top + 1)
        self.assertEqual(url.host, "example.com")

    def test_click_beside_the_link_misses(self):
        tab = make_tab('<p>앞 <a href="https://example.com/">링크</a> 뒤</p>')
        cmd = find_text(tab.display_list, "앞")
        self.assertIsNone(tab.link_at(cmd.rect.left + 1, cmd.rect.top + 1))

    def test_topmost_command_wins(self):
        tab = make_tab('<a href="https://example.com/">링크</a>')
        cmd = find_text(tab.display_list, "링크")
        # 배경 사각형이 먼저, 글자가 나중 -> 뒤에서부터 찾으면 글자가 잡힌다
        self.assertIsNotNone(tab.link_at(cmd.rect.left + 1, cmd.rect.top + 1))

    def test_scroll_is_accounted_for(self):
        html = "<p>채우기</p>" * 60 + '<a href="https://example.com/">링크</a>'
        tab = make_tab(html)
        cmd = find_text(tab.display_list, "링크")
        tab.scroll = 200
        self.assertEqual(
            tab.link_at(cmd.rect.left + 1, cmd.rect.top + 1 - 200).host,
            "example.com")


class CarriedForward(unittest.TestCase):
    """1~6장 연습문제가 새 레이아웃 구조에서도 도는지"""

    def test_chapter6_class_selector(self):
        tree = styled('<p class="main">글</p>', ".main { color: red; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "red")

    def test_chapter6_important(self):
        tree = styled('<p class="a">글</p>',
                      "p { color: red !important; } .a { color: blue; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "red")

    def test_chapter6_has_selector(self):
        tree = styled("<div><p>글</p></div>", "div:has(p) { color: red; }")
        self.assertEqual(find_el(tree, "div")[0].style["color"], "red")

    def test_chapter6_width(self):
        doc, _ = build("<div>글</div>", "div { width: 120px; }")
        div = next(o for o in tree_to_list(doc, [])
                   if isinstance(o, BlockLayout) and o.element("div"))
        self.assertEqual(div.width, 120)

    def test_chapter5_toc_label(self):
        _, cmds = build('<nav id="toc"><ul><li>1장</li></ul></nav>')
        self.assertIn(ex7.TOC_LABEL, [c.text for c in texts(cmds)])

    def test_chapter5_bullets(self):
        _, cmds = build("<ul><li>하나</li><li>둘</li></ul>")
        black = [c for c in cmds
                 if isinstance(c, DrawRect) and c.color == "black"]
        self.assertEqual(len(black), 2)

    def test_chapter5_run_in_heading(self):
        _, cmds = build("<div><h6>제목.</h6><p>이어지는 본문</p></div>")
        self.assertEqual(find_text(cmds, "제목.").rect.top,
                         find_text(cmds, "이어지는").rect.top)

    def test_chapter4_comment(self):
        _, cmds = build("가<!-- 숨김 -->나")
        self.assertNotIn("숨김", " ".join(c.text for c in texts(cmds)))

    def test_chapter3_pre_preserves_spaces(self):
        _, cmds = build("<pre>a    b</pre>")
        self.assertIn("a    b", [c.text for c in texts(cmds)])

    def test_chapter3_smallcaps(self):
        _, cmds = build("<abbr>abc</abbr>")
        self.assertIn("ABC", "".join(c.text for c in texts(cmds)))

    def test_chapter3_superscript_is_smaller(self):
        _, cmds = build("<p>보통 <sup>위</sup></p>")
        self.assertLess(find_text(cmds, "위").font.metrics("linespace"),
                        find_text(cmds, "보통").font.metrics("linespace"))

    def test_chapter3_centered_title(self):
        _, cmds = build('<h1 class="title">가운데</h1>')
        left = find_text(cmds, "가운데").rect.left
        self.assertGreater(left, ex7.HSTEP + 10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
