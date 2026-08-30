"""URL, 쿠키, 전송 보안."""

import unittest

from wbe.net import cookies as cookiejar
from wbe.net.security import (cors_allows, frame_allowed, parse_csp,
                              referrer_policy_of)
from wbe.net.url import (URL, form_decode, form_encode, parse_url,
                         percent_encode, resolve)


class TestURL(unittest.TestCase):
    def test_http_parts(self):
        url = URL("http://example.com/a/b")
        self.assertEqual((url.scheme, url.host, url.port, url.path),
                         ("http", "example.com", 80, "/a/b"))

    def test_https_default_port(self):
        self.assertEqual(URL("https://example.com/").port, 443)

    def test_explicit_port(self):
        self.assertEqual(URL("http://example.com:8080/").port, 8080)

    def test_file_scheme(self):
        self.assertEqual(URL("file:///etc/hosts").path, "/etc/hosts")

    def test_data_scheme(self):
        self.assertEqual(URL("data:text/html,<b>hi</b>").request(), "<b>hi</b>")

    def test_data_is_percent_decoded(self):
        self.assertEqual(URL("data:text/html,%3Cb%3E").request(), "<b>")

    def test_about_blank_is_empty(self):
        self.assertEqual(URL("about:blank").request(), "")

    def test_view_source_wraps(self):
        url = URL("view-source:https://example.com/")
        self.assertTrue(url.view_source)
        self.assertEqual(url.scheme, "https")

    def test_fragment_is_split_off(self):
        url = URL("https://example.com/a#sec")
        self.assertEqual((url.path, url.fragment), ("/a", "sec"))

    def test_str_keeps_the_fragment(self):
        self.assertTrue(str(URL("https://e.com/a#s")).endswith("#s"))

    def test_bad_url_falls_back(self):
        self.assertEqual(parse_url("!!!").scheme, "about")

    def test_origin(self):
        self.assertEqual(URL("http://a.example/x").origin(),
                         "http://a.example:80")

    def test_opaque_origin_for_data(self):
        self.assertEqual(URL("data:text/html,x").origin(), "null")

    def test_is_secure(self):
        self.assertTrue(URL("https://e.com/").is_secure())
        self.assertFalse(URL("http://e.com/").is_secure())


class TestResolve(unittest.TestCase):
    BASE = URL("http://example.com/dir/page.html")

    def test_absolute_path(self):
        self.assertEqual(self.BASE.resolve("/x").path, "/x")

    def test_relative_path(self):
        self.assertEqual(self.BASE.resolve("y").path, "/dir/y")

    def test_parent_path(self):
        self.assertEqual(self.BASE.resolve("../y").path, "/y")

    def test_absolute_url(self):
        self.assertEqual(self.BASE.resolve("http://b.example/z").host,
                         "b.example")

    def test_fragment_only(self):
        out = self.BASE.resolve("#top")
        self.assertEqual(out.path, "/dir/page.html")
        self.assertTrue(out.same_page(self.BASE))

    def test_data_url_survives_resolution(self):
        """str() 을 거치면 data: 내용이 사라진다. 원문으로 다시 만들어야 한다."""
        target = "data:image/png;base64,AAAA"
        self.assertEqual(resolve(self.BASE, target).data, "AAAA")

    def test_with_query(self):
        self.assertEqual(URL("http://e.com/s").with_query("q=1").path,
                         "/s?q=1")

    def test_with_query_replaces(self):
        self.assertEqual(URL("http://e.com/s?old=1").with_query("q=1").path,
                         "/s?q=1")


class TestFormEncoding(unittest.TestCase):
    def test_space_becomes_plus(self):
        self.assertEqual(percent_encode("a b"), "a+b")

    def test_special_chars(self):
        self.assertEqual(percent_encode("a&b=c"), "a%26b%3Dc")

    def test_non_ascii_is_encoded(self):
        """chr(byte) 가 주는 라틴-1 글자도 isalnum() 이라 그냥 두면 겹친다."""
        self.assertEqual(percent_encode("파"), "%ED%8C%8C")

    def test_round_trip(self):
        body = form_encode([("guest", "파스타"), ("q", "a b")])
        self.assertEqual(form_decode(body), {"guest": "파스타", "q": "a b"})


class TestCookies(unittest.TestCase):
    def setUp(self):
        cookiejar.clear()

    def tearDown(self):
        cookiejar.clear()

    def test_parse(self):
        key, value, params = cookiejar.parse_cookie(
            "token=abc; SameSite=Lax; HttpOnly")
        self.assertEqual((key, value), ("token", "abc"))
        self.assertEqual(params["samesite"], "Lax")
        self.assertIn("httponly", params)

    def test_header(self):
        cookiejar.store_cookie("e.com", "a=1")
        cookiejar.store_cookie("e.com", "b=2")
        self.assertEqual(sorted(cookiejar.cookie_header("e.com").split("; ")),
                         ["a=1", "b=2"])

    def test_samesite_lax_held_back_cross_site(self):
        cookiejar.store_cookie("e.com", "a=1; SameSite=Lax")
        self.assertIsNone(cookiejar.cookie_header("e.com", top_level=False))

    def test_samesite_none_goes_along(self):
        cookiejar.store_cookie("e.com", "a=1; SameSite=None")
        self.assertEqual(cookiejar.cookie_header("e.com", top_level=False),
                         "a=1")

    def test_httponly_hidden_from_scripts(self):
        cookiejar.store_cookie("e.com", "s=1; HttpOnly")
        cookiejar.store_cookie("e.com", "p=2")
        self.assertEqual(cookiejar.cookie_header("e.com", script_visible=True),
                         "p=2")

    def test_httponly_still_sent_to_server(self):
        cookiejar.store_cookie("e.com", "s=1; HttpOnly")
        self.assertIn("s=1", cookiejar.cookie_header("e.com"))

    def test_max_age_beats_expires(self):
        params = {"max-age": "10",
                  "expires": "Thu, 01 Jan 1970 00:00:00 GMT"}
        self.assertAlmostEqual(cookiejar.cookie_expiry(params, now=100), 110)

    def test_expired_is_dropped(self):
        cookiejar.store_cookie("e.com", "a=1; Max-Age=10", now=0)
        self.assertIsNone(cookiejar.cookie_header("e.com", now=100))
        self.assertNotIn("a", cookiejar.COOKIE_JAR.get("e.com", {}))

    def test_reset_with_later_date_extends(self):
        cookiejar.store_cookie("e.com", "a=1; Max-Age=10", now=0)
        cookiejar.store_cookie("e.com", "a=2; Max-Age=100", now=0)
        self.assertEqual(cookiejar.cookie_header("e.com", now=50), "a=2")


class TestSecurity(unittest.TestCase):
    def test_csp_parsed(self):
        self.assertEqual(parse_csp("default-src http://a http://b"),
                         ["http://a", "http://b"])

    def test_no_csp(self):
        self.assertIsNone(parse_csp(""))

    def test_frame_options_deny(self):
        self.assertFalse(frame_allowed({"x-frame-options": "DENY"},
                                       "http://a:80", "http://a:80"))

    def test_frame_options_sameorigin(self):
        self.assertTrue(frame_allowed({"x-frame-options": "SAMEORIGIN"},
                                      "http://a:80", "http://a:80"))
        self.assertFalse(frame_allowed({"x-frame-options": "SAMEORIGIN"},
                                       "http://a:80", "http://b:80"))

    def test_no_header_allows(self):
        self.assertTrue(frame_allowed({}, "http://a:80", "http://b:80"))

    def test_cors(self):
        self.assertTrue(cors_allows(
            {"access-control-allow-origin": "*"}, "http://a:80"))
        self.assertTrue(cors_allows(
            {"access-control-allow-origin": "http://a:80"}, "http://a:80"))
        self.assertFalse(cors_allows({}, "http://a:80"))

    def test_referrer_policy(self):
        self.assertEqual(referrer_policy_of({"referrer-policy": "no-referrer"}),
                         "no-referrer")
        self.assertIsNone(referrer_policy_of({"referrer-policy": "이상함"}))


class TestReferer(unittest.TestCase):
    def test_default_sends_it(self):
        self.assertEqual(
            URL("http://b.example/x").referrer_value(
                URL("http://a.example/from"), None),
            "http://a.example:80/from")

    def test_no_referrer(self):
        self.assertIsNone(URL("http://b.example/x").referrer_value(
            URL("http://a.example/f"), "no-referrer"))

    def test_same_origin_across_sites(self):
        self.assertIsNone(URL("http://b.example/x").referrer_value(
            URL("http://a.example/f"), "same-origin"))

    def test_downgrade_not_reported(self):
        self.assertIsNone(URL("http://b.example/x").referrer_value(
            URL("https://a.example/f"), "no-referrer-when-downgrade"))

    def test_header_appears(self):
        raw = URL("http://b.example/x")._request_bytes(
            None, URL("http://a.example/f"), None, None, True)
        self.assertIn(b"Referer: http://a.example:80/f", raw)

    def test_post_has_content_type(self):
        raw = URL("http://b.example/x")._request_bytes(
            "a=1", None, None, None, True)
        self.assertIn(b"POST /x HTTP/1.1", raw)
        self.assertIn(b"Content-Length: 3", raw)


if __name__ == "__main__":
    unittest.main(verbosity=2)
