"""8장 연습문제 검증.

    python3 test_ex8.py

브라우저 쪽은 data: URL 로, 서버 쪽은 do_request 를 직접 불러 확인한다.
실제 소켓은 8-6/8-7 의 한 테스트에서만 쓴다.
"""

import os
import tempfile
import tkinter
import unittest
import urllib.parse

import ex8
import server8ex
from ex8 import (URL, Tab, Browser, HTMLChrome, History, HistoryEntry,
                 DocumentLayout, BlockLayout, LineLayout, TextLayout,
                 InputLayout, ButtonLayout, HTMLParser, Element, Text,
                 DrawText, DrawRect, DrawOutline, DrawLine, paint_tree,
                 tree_to_list, style, cascade_priority, CSSParser,
                 DEFAULT_STYLE_SHEET, form_encode, percent_encode,
                 always_resubmit, never_resubmit, INPUT_WIDTH_PX,
                 CHECKBOX_SIZE, HEIGHT)
from server8ex import Board, do_request, form_decode

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
    for node in tree_to_list(tree, []):
        if isinstance(node, Element):
            node.is_focused = False
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


PAGE_URL = "http://localhost:8000/page"


def make_tab(html, url=PAGE_URL):
    """data: 로 내용을 넣되, 폼의 상대 주소를 풀 수 있게 주소는 http 로 둔다."""
    tab = Tab(HEIGHT - 100)
    tab.load(data_url(html))
    if url:
        tab.url = URL(url)
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


def layout_objects(doc, cls):
    return [o for o in tree_to_list(doc, []) if isinstance(o, cls)]


FORM = ('<form action="/submit" method="post">'
        '<input name="q" value="hi">'
        '<button>보내기</button></form>')


class Exercise81(unittest.TestCase):
    """8-1 Enter 키"""

    def setUp(self):
        self.tab = make_tab(FORM)
        self.sent = []
        self.tab.load = lambda url, payload=None, record=True: \
            self.sent.append((str(url), payload))

    def test_enter_in_an_input_submits(self):
        inp = find_el(self.tab.nodes, "input")[0]
        self.tab.focus_on(inp)
        self.tab.enter()
        self.assertEqual(len(self.sent), 1)

    def test_enter_sends_the_value(self):
        inp = find_el(self.tab.nodes, "input")[0]
        self.tab.focus_on(inp)
        self.tab.enter()
        self.assertEqual(self.sent[0][1], "q=hi")

    def test_enter_without_focus_does_nothing(self):
        self.tab.enter()
        self.assertEqual(self.sent, [])

    def test_enter_outside_a_form_does_nothing(self):
        tab = make_tab('<input name="q" value="hi">')
        tab.load = lambda *a, **k: self.sent.append(a)
        inp = find_el(tab.nodes, "input")[0]
        tab.focus_on(inp)
        self.assertIsNone(tab.enter())


class Exercise82(unittest.TestCase):
    """8-2 GET 폼"""

    HTML = ('<form action="/search" method="get">'
            '<input name="q" value="웹 브라우저">'
            '<button>찾기</button></form>')

    def test_with_query_appends(self):
        url = URL("https://example.com/search")
        self.assertEqual(url.with_query("q=hi").path, "/search?q=hi")

    def test_with_query_replaces_an_old_one(self):
        url = URL("https://example.com/search?old=1")
        self.assertEqual(url.with_query("q=hi").path, "/search?q=hi")

    def test_get_form_has_no_body(self):
        tab = make_tab(self.HTML)
        sent = []
        tab.load = lambda url, payload=None, record=True: \
            sent.append((str(url), payload))
        tab.submit_form(find_el(tab.nodes, "button")[0])
        self.assertEqual(len(sent), 1)
        self.assertIsNone(sent[0][1], "GET 제출에는 본문이 없습니다")

    def test_get_form_puts_data_in_the_url(self):
        tab = make_tab(self.HTML)
        sent = []
        tab.load = lambda url, payload=None, record=True: \
            sent.append(str(url))
        tab.submit_form(find_el(tab.nodes, "button")[0])
        self.assertIn("?q=", sent[0])
        self.assertIn("+", sent[0], "공백은 + 로 갑니다")

    def test_post_is_still_the_default(self):
        tab = make_tab(FORM)
        sent = []
        tab.load = lambda url, payload=None, record=True: sent.append(payload)
        tab.submit_form(find_el(tab.nodes, "button")[0])
        self.assertEqual(sent[0], "q=hi")


class Exercise83(unittest.TestCase):
    """8-3 블러"""

    def test_blur_clears_the_tab_focus(self):
        tab = make_tab(FORM)
        inp = find_el(tab.nodes, "input")[0]
        tab.focus_on(inp)
        self.assertTrue(inp.is_focused)
        tab.blur()
        self.assertIsNone(tab.focus)
        self.assertFalse(inp.is_focused)

    def test_focusing_another_input_blurs_the_first(self):
        tab = make_tab('<form action="/a"><input name="a"><input name="b">'
                       "</form>")
        a, b = find_el(tab.nodes, "input")
        tab.focus_on(a)
        tab.focus_on(b)
        self.assertFalse(a.is_focused)
        self.assertTrue(b.is_focused)

    def test_only_one_cursor_is_drawn(self):
        tab = make_tab('<form action="/a"><input name="a"><input name="b">'
                       "</form>")
        a, b = find_el(tab.nodes, "input")
        tab.focus_on(a)
        tab.render()
        cursors = [c for c in tab.display_list if isinstance(c, DrawLine)]
        self.assertEqual(len(cursors), 1)

    def test_clicking_the_chrome_blurs_the_page(self):
        browser = Browser(root=_root)
        try:
            tab = browser.new_tab(data_url(FORM))
            inp = find_el(tab.nodes, "input")[0]
            tab.focus_on(inp)
            browser.chrome.click(5, 5)      # 크롬 아무 데나
            tab.blur()
            self.assertIsNone(tab.focus)
        finally:
            browser.close()

    def test_page_and_chrome_do_not_both_hold_focus(self):
        browser = Browser(root=_root)
        try:
            tab = browser.new_tab(data_url(FORM))
            inp = find_el(tab.nodes, "input")[0]
            tab.focus_on(inp)
            browser.chrome.focus = "address bar"
            browser.chrome.blur()
            self.assertIsNone(browser.chrome.focus)
        finally:
            browser.close()


class Exercise84(unittest.TestCase):
    """8-4 체크박스"""

    HTML = ('<form action="/a" method="post">'
            '<input name="plain" value="v">'
            '<input name="sign" type="checkbox" value="yes">'
            '<input name="other" type="checkbox">'
            "</form>")

    def test_checkbox_is_a_square(self):
        doc, _ = build('<input name="a" type="checkbox">')
        box = layout_objects(doc, InputLayout)[0]
        self.assertEqual(box.width, CHECKBOX_SIZE)
        self.assertEqual(box.height, CHECKBOX_SIZE)

    def test_text_input_is_wider(self):
        doc, _ = build('<input name="a" value="x">')
        box = layout_objects(doc, InputLayout)[0]
        self.assertEqual(box.width, INPUT_WIDTH_PX)

    def test_unchecked_is_not_submitted(self):
        tab = make_tab(self.HTML)
        form = find_el(tab.nodes, "form")[0]
        self.assertEqual(form_encode(tab.form_pairs(form)), "plain=v")

    def test_checked_uses_its_value(self):
        tab = make_tab(self.HTML)
        find_el(tab.nodes, "input")[1].attributes["checked"] = ""
        form = find_el(tab.nodes, "form")[0]
        self.assertIn("sign=yes", form_encode(tab.form_pairs(form)))

    def test_value_defaults_to_on(self):
        tab = make_tab(self.HTML)
        find_el(tab.nodes, "input")[2].attributes["checked"] = ""
        form = find_el(tab.nodes, "form")[0]
        self.assertIn("other=on", form_encode(tab.form_pairs(form)))

    def test_clicking_toggles(self):
        tab = make_tab(self.HTML)
        box = layout_objects(tab.document, InputLayout)[1]
        tab.click(box.x + 2, box.y + 2)
        self.assertIn("checked", find_el(tab.nodes, "input")[1].attributes)
        box = layout_objects(tab.document, InputLayout)[1]
        tab.click(box.x + 2, box.y + 2)
        self.assertNotIn("checked", find_el(tab.nodes, "input")[1].attributes)

    def test_checked_box_is_filled(self):
        tab = make_tab('<input name="a" type="checkbox" checked>')
        box = layout_objects(tab.document, InputLayout)[0]
        fills = [c for c in box.paint()
                 if isinstance(c, DrawRect) and c.color == "black"]
        self.assertEqual(len(fills), 1)


class Exercise85(unittest.TestCase):
    """8-5 요청 재전송"""

    def test_history_remembers_the_method(self):
        h = History()
        h.visit(URL("https://a.example/"))
        h.visit(URL("https://b.example/"), "POST", "q=1")
        self.assertTrue(h.current().is_post())
        self.assertEqual(h.current().body, "q=1")

    def test_back_to_a_get_just_works(self):
        tab = make_tab("<p>가</p>")
        tab.load(data_url("<p>나</p>"))
        tab.go_back()
        self.assertIn("가", [c.text for c in texts(tab.display_list)])

    def post_history(self, tab):
        """가(GET) -> 나(POST) -> 다(GET). 나로 돌아가려면 다시 보내야 한다."""
        tab.history.visit(data_url("<p>나</p>"), "POST", "q=1")
        tab.history.visit(data_url("<p>다</p>"))

    def test_back_to_a_post_asks_first(self):
        tab = make_tab("<p>가</p>")
        self.post_history(tab)
        tab.confirm_resubmit = never_resubmit
        self.assertIsNone(tab.go_back(), "거절하면 이동하지 않습니다")

    def test_declining_leaves_history_alone(self):
        tab = make_tab("<p>가</p>")
        self.post_history(tab)
        before = len(tab.history.past)
        tab.confirm_resubmit = never_resubmit
        tab.go_back()
        self.assertEqual(len(tab.history.past), before)

    def test_accepting_resubmits(self):
        tab = make_tab("<p>가</p>")
        self.post_history(tab)
        posted = []
        tab.confirm_resubmit = always_resubmit
        tab.load = lambda url, payload=None, record=True: \
            posted.append(payload)
        tab.go_back()
        self.assertEqual(posted, ["q=1"])

    def test_get_entries_are_not_asked_about(self):
        tab = make_tab("<p>가</p>")
        tab.load(data_url("<p>나</p>"))
        tab.confirm_resubmit = never_resubmit
        self.assertIsNotNone(tab.go_back())


class Exercise86(unittest.TestCase):
    """8-6 게시판"""

    def setUp(self):
        self.tmp = tempfile.mktemp(suffix=".txt")
        self._saved = server8ex.BOARD
        server8ex.BOARD = Board(self.tmp)

    def tearDown(self):
        server8ex.BOARD = self._saved
        if os.path.exists(self.tmp):
            os.remove(self.tmp)

    def test_home_lists_topics(self):
        server8ex.BOARD.add_topic("cooking")
        server8ex.BOARD.add_topic("cars")
        _, page = do_request("GET", "/", {}, None)
        self.assertIn("cooking", page)
        self.assertIn("cars", page)

    def test_topics_have_their_own_urls(self):
        server8ex.BOARD.add_topic("cooking")
        status, page = do_request("GET", "/cooking", {}, None)
        self.assertEqual(status, "200 OK")
        self.assertIn("cooking", page)

    def test_unknown_topic_is_404(self):
        status, _ = do_request("GET", "/nope", {}, None)
        self.assertEqual(status, "404 Not Found")

    def test_entries_stay_in_their_topic(self):
        server8ex.BOARD.add_topic("cooking")
        server8ex.BOARD.add_topic("cars")
        do_request("POST", "/cooking", {}, "guest=pasta")
        _, cars = do_request("GET", "/cars", {}, None)
        _, cooking = do_request("GET", "/cooking", {}, None)
        self.assertIn("pasta", cooking)
        self.assertNotIn("pasta", cars)

    def test_home_form_creates_a_topic(self):
        do_request("POST", "/", {}, "topic=books")
        self.assertTrue(server8ex.BOARD.has("books"))

    def test_checkbox_reaches_the_server(self):
        server8ex.BOARD.add_topic("cooking")
        do_request("POST", "/cooking", {}, "guest=hi&sign=yes")
        self.assertIn("서명함", server8ex.BOARD.entries("cooking")[0])

    def test_bad_topic_names_are_refused(self):
        self.assertIsNone(server8ex.BOARD.add_topic("a/b"))
        self.assertIsNone(server8ex.BOARD.add_topic("  "))

    def test_form_decode_handles_plus(self):
        self.assertEqual(form_decode("q=a+b"), {"q": "a b"})


class Exercise87(unittest.TestCase):
    """8-7 영속성"""

    def setUp(self):
        self.tmp = tempfile.mktemp(suffix=".txt")

    def tearDown(self):
        if os.path.exists(self.tmp):
            os.remove(self.tmp)

    def test_entries_survive_a_restart(self):
        board = Board(self.tmp)
        board.add_topic("cooking")
        board.add_entry("cooking", "pasta")
        again = Board(self.tmp)
        self.assertEqual(again.entries("cooking"), ["pasta"])

    def test_empty_topics_survive(self):
        board = Board(self.tmp)
        board.add_topic("empty")
        self.assertIn("empty", Board(self.tmp).names())

    def test_missing_file_is_fine(self):
        self.assertEqual(Board(self.tmp).names(), [])

    def test_tabs_in_text_do_not_break_the_file(self):
        board = Board(self.tmp)
        board.add_topic("t")
        board.add_entry("t", "a\tb")
        again = Board(self.tmp)
        self.assertEqual(len(again.entries("t")), 1)

    def test_order_is_kept(self):
        board = Board(self.tmp)
        board.add_topic("t")
        for x in ("하나", "둘", "셋"):
            board.add_entry("t", x)
        self.assertEqual(Board(self.tmp).entries("t"), ["하나", "둘", "셋"])


class Exercise88(unittest.TestCase):
    """8-8 풍부한 버튼"""

    def test_button_lays_out_its_children(self):
        doc, _ = build("<button><b>굵게</b> 그리고 <i>기울임</i></button>")
        btn = layout_objects(doc, ButtonLayout)[0]
        self.assertGreater(btn.height, 0)

    def test_children_are_drawn(self):
        _, cmds = build("<button><b>굵게</b> 그리고 <i>기울임</i></button>")
        drawn = [c.text for c in texts(cmds)]
        for word in ("굵게", "그리고", "기울임"):
            self.assertIn(word, drawn)

    def test_children_stay_inside(self):
        doc, cmds = build("<button>" + "긴 내용 " * 30 + "</button>")
        btn = layout_objects(doc, ButtonLayout)[0]
        for cmd in texts(cmds):
            self.assertGreaterEqual(cmd.rect.left, btn.x - 1)
            self.assertLessEqual(cmd.rect.right, btn.x + btn.width + 1)
            self.assertGreaterEqual(cmd.rect.top, btn.y - 1)
            self.assertLessEqual(cmd.rect.bottom, btn.y + btn.height + 1)

    def test_long_content_makes_a_tall_button(self):
        doc_short, _ = build("<button>짧게</button>")
        doc_long, _ = build("<button>" + "긴 내용 " * 30 + "</button>")
        short = layout_objects(doc_short, ButtonLayout)[0]
        long_ = layout_objects(doc_long, ButtonLayout)[0]
        self.assertGreater(long_.height, short.height)

    def test_button_has_an_outline(self):
        _, cmds = build("<button>눌러</button>")
        self.assertTrue(any(isinstance(c, DrawOutline) for c in cmds))

    def test_clicking_a_child_submits_the_form(self):
        tab = make_tab('<form action="/a" method="post">'
                       '<input name="q" value="hi">'
                       "<button><b>보내기</b></button></form>")
        sent = []
        tab.load = lambda url, payload=None, record=True: sent.append(payload)
        cmd = find_text(tab.display_list, "보내기")
        tab.click(cmd.rect.left + 1, cmd.rect.top + 1)
        self.assertEqual(sent, ["q=hi"])

    def test_a_link_inside_a_button_wins(self):
        """가장 안쪽 요소가 이깁니다 — 실제 브라우저와 같습니다."""
        tab = make_tab('<form action="/a"><button>'
                       '<a href="https://example.com/">링크</a>'
                       "</button></form>")
        cmd = find_text(tab.display_list, "링크")
        node = tab.node_at(cmd.rect.left + 1, cmd.rect.top + 1)
        tags = []
        while node is not None:
            if isinstance(node, Element):
                tags.append(node.tag)
            node = node.parent
        self.assertLess(tags.index("a"), tags.index("button"))


class Exercise89(unittest.TestCase):
    """8-9 HTML 크롬"""

    class FakeBrowser:
        def __init__(self):
            self.tabs = []
            self.active_tab = None

        def new_tab(self, url, background=False):
            tab = Tab(HEIGHT - 100)
            tab.load(url)
            self.tabs.append(tab)
            self.active_tab = tab
            return tab

        def draw(self):
            pass

    def make(self):
        browser = self.FakeBrowser()
        browser.new_tab(data_url("<p>가</p>"))
        return browser, HTMLChrome(browser)

    def test_chrome_is_a_real_document(self):
        _, chrome = self.make()
        self.assertIsInstance(chrome.document, DocumentLayout)
        self.assertGreater(chrome.bottom, 0)

    def test_buttons_are_button_elements(self):
        _, chrome = self.make()
        ids = {b.attributes.get("id") for b in find_el(chrome.nodes, "button")}
        self.assertIn("newtab", ids)
        self.assertIn("back", ids)

    def test_address_bar_is_an_input(self):
        _, chrome = self.make()
        self.assertEqual(find_el(chrome.nodes, "input")[0].attributes["id"],
                         "address")

    def test_tab_names_are_links(self):
        browser, chrome = self.make()
        browser.new_tab(data_url("<p>나</p>"))
        chrome.render()
        hrefs = [a.attributes["href"] for a in find_el(chrome.nodes, "a")]
        self.assertEqual(hrefs, ["wbe:tab:0", "wbe:tab:1"])

    def test_clicking_a_tab_link_switches(self):
        browser, chrome = self.make()
        first = browser.active_tab
        browser.new_tab(data_url("<p>나</p>"))
        chrome.render()
        cmd = find_text(chrome.display_list, "Tab")
        chrome.click(cmd.rect.left + 1, cmd.rect.top + 1)
        self.assertIs(browser.active_tab, first)

    def test_clicking_the_address_focuses_it(self):
        _, chrome = self.make()
        inp = layout_objects(chrome.document, InputLayout)[0]
        chrome.click(inp.x + 2, inp.y + 2)
        self.assertEqual(chrome.focus, "address bar")

    def test_disabled_back_button_is_gray(self):
        _, chrome = self.make()
        back = next(b for b in find_el(chrome.nodes, "button")
                    if b.attributes.get("id") == "back")
        self.assertIn("disabled", back.attributes.get("class", ""))
        self.assertEqual(back.style["color"], "#999999")

    def test_typing_shows_up_in_the_chrome(self):
        _, chrome = self.make()
        inp = layout_objects(chrome.document, InputLayout)[0]
        chrome.click(inp.x + 2, inp.y + 2)
        for c in "abc":
            chrome.keypress(c)
        value = find_el(chrome.nodes, "input")[0].attributes["value"]
        self.assertEqual(value, "abc")


class CarriedForward(unittest.TestCase):
    """1~7장 연습문제가 그대로 도는지"""

    def test_chapter7_fragment(self):
        url = URL("https://example.com/a#sec")
        self.assertEqual(url.fragment, "sec")

    def test_chapter7_search(self):
        self.assertEqual(ex8.address_to_url("두 낱말").host, "google.com")

    def test_chapter6_class_selector(self):
        tree = styled('<p class="main">글</p>', ".main { color: red; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "red")

    def test_chapter5_bullets(self):
        _, cmds = build("<ul><li>하나</li><li>둘</li></ul>")
        black = [c for c in cmds
                 if isinstance(c, DrawRect) and c.color == "black"]
        self.assertEqual(len(black), 2)

    def test_chapter4_comment(self):
        _, cmds = build("가<!-- 숨김 -->나")
        self.assertNotIn("숨김", " ".join(c.text for c in texts(cmds)))

    def test_chapter3_smallcaps(self):
        _, cmds = build("<abbr>abc</abbr>")
        self.assertIn("ABC", "".join(c.text for c in texts(cmds)))

    def test_chapter1_percent_encoding(self):
        self.assertEqual(percent_encode("a b&c"), "a+b%26c")

    def test_non_ascii_is_percent_encoded(self):
        """chr(byte) 가 주는 라틴-1 글자도 isalnum() 이라 그냥 두면 이중 인코딩된다."""
        self.assertEqual(percent_encode("파"), "%ED%8C%8C")

    def test_non_ascii_survives_a_round_trip(self):
        body = form_encode([("guest", "파스타")])
        self.assertEqual(form_decode(body), {"guest": "파스타"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
