"""10장 연습문제 검증.

    python3 test_ex10.py

브라우저 쪽은 data: URL 과 가짜 응답으로, 서버 쪽은 do_request 를 직접 부른다.
실제 소켓은 쓰지 않는다.
"""

import time
import tkinter
import unittest
import urllib.parse

import ex10
import server10ex
from ex10 import (URL, Tab, Browser, HTMLChrome, JSContext, InputLayout,
                  DocumentLayout, BlockLayout, HTMLParser, Element, Text,
                  DrawText, DrawRect, DrawLine, paint_tree, tree_to_list,
                  style, cascade_priority, CSSParser, DEFAULT_STYLE_SHEET,
                  COOKIE_JAR, CertificateError, LOCK, PASSWORD_CHAR,
                  parse_cookie, cookie_expiry, store_cookie, live_cookies,
                  cookie_header, parse_csp, display_value, is_hidden, HEIGHT)
from server10ex import (SESSIONS, do_request, expire_sessions, get_session,
                        touch_session, form_decode)

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


def make_tab(html, url=None):
    tab = Tab(HEIGHT - 100)
    tab.load(data_url(html))
    if url:
        tab.url = URL(url)
    return tab


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


def find_el(node, tag, out=None):
    out = [] if out is None else out
    if isinstance(node, Element):
        if node.tag == tag:
            out.append(node)
        for c in node.children:
            find_el(c, tag, out)
    return out


def inputs(doc):
    return [o for o in tree_to_list(doc, []) if isinstance(o, InputLayout)]


def texts(cmds):
    return [c for c in cmds if isinstance(c, DrawText)]


class CookieBase(unittest.TestCase):
    def setUp(self):
        self._saved = dict(COOKIE_JAR)
        COOKIE_JAR.clear()

    def tearDown(self):
        COOKIE_JAR.clear()
        COOKIE_JAR.update(self._saved)


class Exercise101(unittest.TestCase):
    """10-1 새로운 입력"""

    def test_hidden_input_takes_no_space(self):
        doc, _ = build('<input name="a" type="hidden" value="v">')
        box = inputs(doc)[0]
        self.assertEqual(box.width, 0)
        self.assertEqual(box.height, 0)

    def test_hidden_input_draws_nothing(self):
        _, cmds = build('<input name="a" type="hidden" value="비밀">')
        self.assertEqual(texts(cmds), [])

    def test_hidden_input_is_still_submitted(self):
        tab = make_tab('<form action="/a" method="post">'
                       '<input name="a" type="hidden" value="v"></form>',
                       url="http://localhost:8000/")
        form = find_el(tab.nodes, "form")[0]
        self.assertEqual(ex10.form_encode(tab.form_pairs(form)), "a=v")

    def test_password_is_starred(self):
        node = Element("input", {"type": "password", "value": "비밀"}, None)
        self.assertEqual(display_value(node), PASSWORD_CHAR * 2)

    def test_password_value_is_unchanged(self):
        tab = make_tab('<form action="/a" method="post">'
                       '<input name="p" type="password" value="비밀"></form>',
                       url="http://localhost:8000/")
        form = find_el(tab.nodes, "form")[0]
        self.assertIn("p=%EB%B9%84%EB%B0%80",
                      ex10.form_encode(tab.form_pairs(form)))

    def test_password_draws_stars_not_text(self):
        _, cmds = build('<input name="p" type="password" value="abc">')
        drawn = [c.text for c in texts(cmds)]
        self.assertIn("***", drawn)
        self.assertNotIn("abc", drawn)

    def test_plain_input_is_unaffected(self):
        node = Element("input", {"value": "보임"}, None)
        self.assertEqual(display_value(node), "보임")
        self.assertFalse(is_hidden(node))


class Exercise102(unittest.TestCase):
    """10-2 인증서 오류"""

    def test_bad_certificate_becomes_a_warning_page(self):
        tab = Tab(HEIGHT - 100)
        url = URL("https://expired.example/")

        def boom(*a, **k):
            raise CertificateError("certificate has expired")
        url.request = boom
        tab.load(url)
        drawn = " ".join(c.text for c in tab.display_list
                         if hasattr(c, "text"))
        self.assertIn("믿을", drawn)
        self.assertTrue(tab.insecure)

    def test_warning_page_names_the_site(self):
        tab = Tab(HEIGHT - 100)
        url = URL("https://expired.example/")
        url.request = lambda *a, **k: (_ for _ in ()).throw(
            CertificateError("expired"))
        tab.load(url)
        drawn = " ".join(c.text for c in tab.display_list
                         if hasattr(c, "text"))
        self.assertIn("expired.example", drawn)

    def test_http_is_not_secure(self):
        self.assertFalse(URL("http://example.com/").is_secure())

    def test_https_is_secure(self):
        self.assertTrue(URL("https://example.com/").is_secure())

    def test_lock_is_drawn_for_https(self):
        browser = Browser(root=_root)
        try:
            tab = browser.new_tab(data_url("<p>가</p>"))
            tab.url = URL("https://example.com/")
            browser.chrome.render()
            drawn = [c.text for c in browser.chrome.display_list
                     if hasattr(c, "text")]
            self.assertIn(LOCK, drawn)
        finally:
            browser.close()

    def test_no_lock_for_http(self):
        browser = Browser(root=_root)
        try:
            tab = browser.new_tab(data_url("<p>가</p>"))
            tab.url = URL("http://example.com/")
            browser.chrome.render()
            drawn = [c.text for c in browser.chrome.display_list
                     if hasattr(c, "text")]
            self.assertNotIn(LOCK, drawn)
        finally:
            browser.close()


class Exercise103(CookieBase):
    """10-3 스크립트 접근"""

    def test_read_returns_the_cookies(self):
        store_cookie("example.com", "a=1")
        store_cookie("example.com", "b=2")
        tab = make_tab("<p>가</p>", url="http://example.com/")
        self.assertEqual(sorted(tab.js.cookie_get().split("; ")),
                         ["a=1", "b=2"])

    def test_write_sets_a_cookie(self):
        tab = make_tab("<p>가</p>", url="http://example.com/")
        tab.js.interp.evaljs("document.cookie = 'x=9'")
        self.assertIn("x", COOKIE_JAR["example.com"])

    def test_written_cookie_reads_back(self):
        tab = make_tab("<p>가</p>", url="http://example.com/")
        tab.js.interp.evaljs("document.cookie = 'x=9'")
        self.assertEqual(tab.js.interp.evaljs("document.cookie"), "x=9")

    def test_httponly_is_hidden_from_scripts(self):
        store_cookie("example.com", "secret=1; HttpOnly")
        store_cookie("example.com", "plain=2")
        tab = make_tab("<p>가</p>", url="http://example.com/")
        self.assertEqual(tab.js.cookie_get(), "plain=2")

    def test_httponly_is_still_sent_to_the_server(self):
        store_cookie("example.com", "secret=1; HttpOnly")
        self.assertIn("secret=1", cookie_header("example.com"))

    def test_write_with_params(self):
        tab = make_tab("<p>가</p>", url="http://example.com/")
        tab.js.interp.evaljs("document.cookie = 'x=9; SameSite=None'")
        _, params = COOKIE_JAR["example.com"]["x"]
        self.assertEqual(params["samesite"], "None")


class Exercise104(CookieBase):
    """10-4 쿠키 만료"""

    def test_max_age_wins_over_expires(self):
        params = {"max-age": "10",
                  "expires": "Thu, 01 Jan 1970 00:00:00 GMT"}
        self.assertAlmostEqual(cookie_expiry(params, now=100), 110)

    def test_expires_is_parsed(self):
        params = {"expires": "Thu, 01 Jan 1970 00:00:10 GMT"}
        self.assertAlmostEqual(cookie_expiry(params, now=0), 10)

    def test_session_cookie_has_no_expiry(self):
        self.assertIsNone(cookie_expiry({}))

    def test_expired_cookie_is_not_sent(self):
        store_cookie("example.com", "a=1; Max-Age=10", now=0)
        self.assertIsNone(cookie_header("example.com", now=100))

    def test_live_cookie_is_sent(self):
        store_cookie("example.com", "a=1; Max-Age=100", now=0)
        self.assertEqual(cookie_header("example.com", now=50), "a=1")

    def test_expired_cookie_is_dropped_from_the_jar(self):
        store_cookie("example.com", "a=1; Max-Age=10", now=0)
        live_cookies("example.com", now=100)
        self.assertNotIn("a", COOKIE_JAR.get("example.com", {}))

    def test_resetting_with_a_later_date_extends(self):
        store_cookie("example.com", "a=1; Max-Age=10", now=0)
        store_cookie("example.com", "a=2; Max-Age=100", now=0)
        self.assertEqual(cookie_header("example.com", now=50), "a=2")

    def test_server_sessions_expire(self):
        SESSIONS.clear()
        get_session("tok", now=0)
        SESSIONS["tok"]["expires"] = 5
        expire_sessions(now=10)
        self.assertNotIn("tok", SESSIONS)

    def test_touching_a_session_extends_it(self):
        SESSIONS.clear()
        get_session("tok", now=0)
        before = SESSIONS["tok"]["expires"]
        touch_session("tok", now=100)
        self.assertGreater(SESSIONS["tok"]["expires"], before)

    def test_expired_session_loses_its_data(self):
        SESSIONS.clear()
        get_session("tok", now=0)["user"] = "crashoverride"
        SESSIONS["tok"]["expires"] = 5
        self.assertNotIn("user", get_session("tok", now=10))


class Exercise105(CookieBase):
    """10-5 CORS"""

    class FakeURL(URL):
        """네트워크 대신 정해진 응답을 돌려준다."""

        def __init__(self, url, allow=None):
            super().__init__(url)
            self.allow = allow
            self.sent = {}

        def request(self, referrer=None, payload=None, redirects_left=10,
                    origin=None, referrer_policy=None, top_level=True):
            self.sent = {"origin": origin, "referrer": referrer,
                         "top_level": top_level}
            self.response_headers = {}
            if self.allow is not None:
                self.response_headers["access-control-allow-origin"] = self.allow
            return "응답"

    def tab_with(self, target):
        tab = make_tab("<p>가</p>", url="http://a.example:80/")
        tab.url.resolve = lambda u: target
        return tab

    def test_same_origin_needs_no_header(self):
        target = self.FakeURL("http://a.example/x")
        tab = self.tab_with(target)
        self.assertEqual(tab.js.XMLHttpRequest_send("GET", "/x", ""), "응답")
        self.assertIsNone(target.sent["origin"])

    def test_cross_origin_sends_the_origin_header(self):
        target = self.FakeURL("http://b.example/x", allow="http://a.example:80")
        tab = self.tab_with(target)
        tab.js.XMLHttpRequest_send("GET", "http://b.example/x", "")
        self.assertEqual(target.sent["origin"], "http://a.example:80")

    def test_cross_origin_without_permission_fails(self):
        target = self.FakeURL("http://b.example/x")
        tab = self.tab_with(target)
        with self.assertRaises(Exception):
            tab.js.XMLHttpRequest_send("GET", "http://b.example/x", "")

    def test_wildcard_is_accepted(self):
        target = self.FakeURL("http://b.example/x", allow="*")
        tab = self.tab_with(target)
        self.assertEqual(
            tab.js.XMLHttpRequest_send("GET", "http://b.example/x", ""), "응답")

    def test_wrong_origin_is_refused(self):
        target = self.FakeURL("http://b.example/x", allow="http://c.example")
        tab = self.tab_with(target)
        with self.assertRaises(Exception):
            tab.js.XMLHttpRequest_send("GET", "http://b.example/x", "")

    def test_cross_origin_is_not_top_level(self):
        """교차 출처 요청에는 SameSite=Lax 쿠키가 딸려 가면 안 됩니다."""
        target = self.FakeURL("http://b.example/x", allow="*")
        tab = self.tab_with(target)
        tab.js.XMLHttpRequest_send("GET", "http://b.example/x", "")
        self.assertFalse(target.sent["top_level"])

    def test_server_echoes_the_origin(self):
        _, _, extra = do_request({}, "GET", "/cors",
                                 {"origin": "http://a.example"}, None)
        self.assertEqual(extra["Access-Control-Allow-Origin"],
                         "http://a.example")

    def test_other_paths_do_not_opt_in(self):
        _, _, extra = do_request({}, "GET", "/nocors",
                                 {"origin": "http://a.example"}, None)
        self.assertNotIn("Access-Control-Allow-Origin", extra)


class Exercise106(unittest.TestCase):
    """10-6 Referer"""

    def test_sends_the_referrer_by_default(self):
        url = URL("http://b.example/x")
        self.assertEqual(url.referrer_value(URL("http://a.example/from"), None),
                         "http://a.example:80/from")

    def test_no_referrer_policy_sends_nothing(self):
        url = URL("http://b.example/x")
        self.assertIsNone(
            url.referrer_value(URL("http://a.example/from"), "no-referrer"))

    def test_same_origin_policy_within_the_site(self):
        url = URL("http://a.example/x")
        self.assertIsNotNone(
            url.referrer_value(URL("http://a.example/from"), "same-origin"))

    def test_same_origin_policy_across_sites(self):
        url = URL("http://b.example/x")
        self.assertIsNone(
            url.referrer_value(URL("http://a.example/from"), "same-origin"))

    def test_downgrade_is_not_reported(self):
        url = URL("http://b.example/x")
        self.assertIsNone(url.referrer_value(
            URL("https://a.example/from"), "no-referrer-when-downgrade"))

    def test_upgrade_is_reported(self):
        url = URL("https://b.example/x")
        self.assertIsNotNone(url.referrer_value(
            URL("http://a.example/from"), "no-referrer-when-downgrade"))

    def test_no_referrer_at_all_is_fine(self):
        self.assertIsNone(URL("http://b.example/x").referrer_value(None, None))

    def test_header_appears_in_the_request(self):
        url = URL("http://b.example/x")
        raw = url._bytes(None, URL("http://a.example/from"), None, None, True)
        self.assertIn(b"Referer: http://a.example:80/from", raw)

    def test_unknown_policy_falls_back_to_the_default(self):
        tab = make_tab("<p>가</p>")
        tab.url.response_headers = {"referrer-policy": "이상한값"}
        self.assertIsNone(tab.referrer_policy)


class ChapterTenBasics(CookieBase):
    """10장 본문 기능 — 쿠키, 동일 출처, CSP"""

    def test_cookie_header_is_parsed(self):
        key, value, params = parse_cookie("token=abc; SameSite=Lax; HttpOnly")
        self.assertEqual((key, value), ("token", "abc"))
        self.assertEqual(params["samesite"], "Lax")
        self.assertIn("httponly", params)

    def test_cookies_go_out_in_the_request(self):
        store_cookie("b.example", "a=1")
        raw = URL("http://b.example/x")._bytes(None, None, None, None, True)
        self.assertIn(b"Cookie: a=1", raw)

    def test_samesite_lax_is_held_back(self):
        store_cookie("b.example", "a=1; SameSite=Lax")
        self.assertIsNone(cookie_header("b.example", top_level=False))

    def test_samesite_none_goes_along(self):
        store_cookie("b.example", "a=1; SameSite=None")
        self.assertEqual(cookie_header("b.example", top_level=False), "a=1")

    def test_csp_is_parsed(self):
        self.assertEqual(parse_csp("default-src http://a http://b"),
                         ["http://a", "http://b"])

    def test_no_csp_allows_everything(self):
        tab = make_tab("<p>가</p>")
        self.assertIsNone(tab.allowed_origins)
        self.assertTrue(tab.allowed_request(URL("http://anywhere.example/")))

    def test_csp_blocks_other_origins(self):
        tab = make_tab("<p>가</p>")
        tab.allowed_origins = ["http://a.example:80"]
        self.assertTrue(tab.allowed_request(URL("http://a.example/x")))
        self.assertFalse(tab.allowed_request(URL("http://b.example/x")))

    def test_form_decode_still_works(self):
        self.assertEqual(form_decode("q=a+b"), {"q": "a b"})


class CarriedForward(unittest.TestCase):
    """1~9장 연습문제가 그대로 도는지"""

    def test_chapter9_children(self):
        tab = make_tab('<div id="d"><p>가</p>글자<b>나</b></div>')
        self.assertEqual(tab.js.interp.evaljs("d.children.length"), 2)

    def test_chapter9_serialization(self):
        tab = make_tab('<div id="d"><b>나</b></div>')
        self.assertEqual(tab.js.interp.evaljs("d.innerHTML"), "<b>나</b>")

    def test_chapter8_checkbox(self):
        tab = make_tab('<form action="/a" method="post">'
                       '<input name="b" type="checkbox" checked></form>',
                       url="http://localhost:8000/")
        form = find_el(tab.nodes, "form")[0]
        self.assertEqual(ex10.form_encode(tab.form_pairs(form)), "b=on")

    def test_chapter8_rich_button(self):
        _, cmds = build("<button><b>굵게</b></button>")
        self.assertIn("굵게", [c.text for c in texts(cmds)])

    def test_chapter6_id_and_class_selectors(self):
        tab = make_tab('<p class="main" id="p">글</p>')
        self.assertEqual(
            tab.js.interp.evaljs("document.querySelectorAll('p.main#p').length"),
            1)

    def test_chapter5_bullets(self):
        _, cmds = build("<ul><li>하나</li></ul>")
        black = [c for c in cmds
                 if isinstance(c, DrawRect) and c.color == "black"]
        self.assertEqual(len(black), 1)

    def test_chapter3_smallcaps(self):
        _, cmds = build("<abbr>abc</abbr>")
        self.assertIn("ABC", "".join(c.text for c in texts(cmds)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
