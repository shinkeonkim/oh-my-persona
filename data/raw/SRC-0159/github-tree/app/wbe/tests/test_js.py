"""자바스크립트 — DOM API, 이벤트, 타이머, 캔버스, 쿠키."""

import io
import unittest
from contextlib import redirect_stdout

from wbe.dom.nodes import Element, Text
from wbe.js.context import origin_matches
from wbe.net import cookies as cookiejar
from wbe.net.url import URL
from wbe.paint.commands import DrawRect
from wbe.tests.helpers import by_id, drawn, find_el, make_tab


def run(html, code=""):
    tab = make_tab(html)
    return tab, (tab.js.interp.evaljs(code) if code else None)


def logged(html, code=""):
    buf = io.StringIO()
    with redirect_stdout(buf):
        tab = make_tab(html)
        if code:
            tab.js.interp.evaljs(code)
    return tab, buf.getvalue()


class TestDOMAPI(unittest.TestCase):
    HTML = '<div id="d"><p>가</p>글자<b>나</b></div>'

    def test_query_selector_all(self):
        _, out = run(self.HTML, "document.querySelectorAll('p').length")
        self.assertEqual(out, 1)

    def test_id_selector(self):
        _, out = run(self.HTML, "document.querySelectorAll('#d').length")
        self.assertEqual(out, 1)

    def test_class_selector(self):
        _, out = run('<p class="a">글</p><p>다른</p>',
                     "document.querySelectorAll('.a').length")
        self.assertEqual(out, 1)

    def test_has_selector(self):
        _, out = run("<div><p>글</p></div><div><b>글</b></div>",
                     "document.querySelectorAll('div:has(p)').length")
        self.assertEqual(out, 1)

    def test_children_skips_text(self):
        _, out = run(self.HTML, "d.children.length")
        self.assertEqual(out, 2)

    def test_get_and_set_attribute(self):
        _, out = run(self.HTML,
                     "d.setAttribute('title','x'); d.getAttribute('title')")
        self.assertEqual(out, "x")

    def test_parent_node(self):
        _, out = run(self.HTML, "d.children[0].parentNode.handle === d.handle")
        self.assertTrue(out)

    def test_inner_html_get(self):
        _, out = run(self.HTML, "d.innerHTML")
        self.assertEqual(out, "<p>가</p>글자<b>나</b>")

    def test_inner_html_set(self):
        tab, _ = run(self.HTML, "d.innerHTML = '<i>새것</i>';0;")
        self.assertEqual(len(find_el(tab.nodes, "i")), 1)

    def test_outer_html(self):
        _, out = run("<p id='p'>글</p>", "p.outerHTML")
        self.assertEqual(out, '<p id="p">글</p>')

    def test_create_and_append(self):
        tab, _ = run(self.HTML,
                     "d.appendChild(document.createElement('span'));0;")
        self.assertEqual(len(find_el(tab.nodes, "span")), 1)

    def test_create_text_node(self):
        tab, out = run('<div id="d"></div>',
                       "d.appendChild(document.createTextNode('새 글자'));"
                       "d.innerHTML")
        self.assertEqual(out, "새 글자")

    def test_insert_before(self):
        _, out = run('<div id="d"><b>나</b></div>',
                     "d.insertBefore(document.createElement('i'), "
                     "d.children[0]); d.innerHTML")
        self.assertTrue(out.startswith("<i></i>"))

    def test_insert_before_null_appends(self):
        _, out = run('<div id="d"><b>나</b></div>',
                     "d.insertBefore(document.createElement('i'), null);"
                     "d.innerHTML")
        self.assertTrue(out.endswith("<i></i>"))

    def test_remove_child_returns_it(self):
        _, out = run(self.HTML, "d.removeChild(d.children[0]).outerHTML")
        self.assertEqual(out, "<p>가</p>")

    def test_removed_can_be_reattached(self):
        _, out = run(self.HTML + '<div id="e"></div>',
                     "e.appendChild(d.removeChild(d.children[0]));"
                     "e.innerHTML")
        self.assertEqual(out, "<p>가</p>")

    def test_move_between_parents(self):
        _, out = run('<div id="a"><b>나</b></div><div id="b"></div>',
                     "b.appendChild(a.children[0]);"
                     "a.innerHTML + '|' + b.innerHTML")
        self.assertEqual(out, "|<b>나</b>")

    def test_replace_children_empties(self):
        tab, _ = run(self.HTML, "d.replaceChildren();0;")
        self.assertEqual(by_id(tab.nodes, "d").children, [])

    def test_replace_children_moves(self):
        tab, _ = run('<div id="a"><p id="p">글</p></div><div id="b"></div>',
                     "b.replaceChildren(p);0;")
        self.assertEqual(by_id(tab.nodes, "a").children, [])
        self.assertEqual(len(by_id(tab.nodes, "b").children), 1)

    def test_replace_children_order(self):
        tab, _ = run('<div id="a"><p id="p">가</p><b id="q">나</b></div>'
                     '<div id="b"></div>', "b.replaceChildren(q, p);0;")
        self.assertEqual([c.tag for c in by_id(tab.nodes, "b").children],
                         ["b", "p"])

    def test_style_property(self):
        tab, _ = run("<p id='p'>글</p>",
                     "p.style.setProperty('color', 'red');0;")
        self.assertEqual(find_el(tab.nodes, "p")[0].style["color"], "red")


class TestIdGlobals(unittest.TestCase):
    def test_id_becomes_a_global(self):
        _, out = run('<div id="foo"><b>나</b></div>', "foo.innerHTML")
        self.assertEqual(out, "<b>나</b>")

    def test_new_ids_appear(self):
        _, out = run('<div id="d"></div>',
                     "d.innerHTML = '<p id=\"later\">늦게</p>';"
                     "later.outerHTML")
        self.assertIn("늦게", out)

    def test_removed_ids_disappear(self):
        _, out = run('<div id="d"><p id="gone">감</p></div>',
                     "d.innerHTML = ''; typeof gone")
        self.assertEqual(out, "undefined")

    def test_bad_identifiers_skipped(self):
        _, out = run('<div id="not-an-identifier">가</div>',
                     "typeof this['not-an-identifier']")
        self.assertEqual(out, "undefined")

    def test_reserved_words_not_clobbered(self):
        _, out = run('<div id="document">가</div>',
                     "typeof document.querySelectorAll")
        self.assertEqual(out, "function")


class TestEvents(unittest.TestCase):
    HTML = ('<div id="outer"><div id="inner"><p id="target">글자</p>'
            "</div></div>")

    def test_handler_runs(self):
        tab = make_tab(self.HTML + "<script>window_n=0;"
                       "target.addEventListener('click',"
                       "function(){window_n++});</script>")
        tab.js.dispatch_event("click", find_el(tab.nodes, "p")[0])
        self.assertEqual(tab.js.interp.evaljs("window_n"), 1)

    def test_bubbling_order(self):
        tab = make_tab(self.HTML + "<script>window_order=[];"
                       "['target','inner','outer'].forEach(function(id){"
                       "this[id].addEventListener('click',function(e){"
                       "window_order.push(id)})});</script>")
        tab.js.dispatch_event("click", find_el(tab.nodes, "p")[0])
        self.assertEqual(tab.js.interp.evaljs("window_order.join(',')"),
                         "target,inner,outer")

    def test_stop_propagation(self):
        tab = make_tab(self.HTML + "<script>window_order=[];"
                       "target.addEventListener('click',function(e){"
                       "window_order.push('t'); e.stopPropagation()});"
                       "outer.addEventListener('click',function(e){"
                       "window_order.push('o')});</script>")
        tab.js.dispatch_event("click", find_el(tab.nodes, "p")[0])
        self.assertEqual(tab.js.interp.evaljs("window_order.join(',')"), "t")

    def test_target_and_current_target(self):
        tab = make_tab(self.HTML + "<script>seen='';"
                       "outer.addEventListener('click',function(e){"
                       "seen = e.target.handle + '/' + e.currentTarget.handle"
                       "});</script>")
        tab.js.dispatch_event("click", find_el(tab.nodes, "p")[0])
        a, b = tab.js.interp.evaljs("seen").split("/")
        self.assertNotEqual(a, b)

    def test_prevent_default_reported(self):
        tab = make_tab('<p id="p">글</p><script>'
                       "p.addEventListener('click',function(e){"
                       "e.preventDefault()});</script>")
        self.assertTrue(tab.js.dispatch_event("click",
                                              find_el(tab.nodes, "p")[0]))

    def test_remove_event_listener(self):
        tab = make_tab('<p id="p">글</p><script>window_n=0;'
                       "var f = function(){window_n++};"
                       "p.addEventListener('click', f);"
                       "p.removeEventListener('click', f);</script>")
        tab.js.dispatch_event("click", find_el(tab.nodes, "p")[0])
        self.assertEqual(tab.js.interp.evaljs("window_n"), 0)

    def test_focus_method_and_event(self):
        tab = make_tab('<input id="i" name="q"><script>window_n=0;'
                       "i.addEventListener('focus',function(){window_n++});"
                       "i.focus();</script>")
        self.assertIs(tab.root_frame.tab_focus, find_el(tab.nodes, "input")[0])
        self.assertEqual(tab.js.interp.evaljs("window_n"), 1)

    def test_blur_event(self):
        tab = make_tab('<input id="a" name="a"><input id="b" name="b">'
                       "<script>window_n=0;"
                       "a.addEventListener('blur',function(){window_n++});"
                       "a.focus(); b.focus();</script>")
        self.assertEqual(tab.js.interp.evaljs("window_n"), 1)


class TestTimers(unittest.TestCase):
    def test_settimeout_runs_once(self):
        tab = make_tab("<p>가</p><script>window_n=0;"
                       "setTimeout(function(){window_n++}, 5);</script>")
        tab.js.dispatch_settimeout(0)
        tab.js.dispatch_settimeout(0)
        self.assertEqual(tab.js.interp.evaljs("window_n"), 1)

    def test_interval_repeats(self):
        tab = make_tab("<p>가</p><script>window_n=0;"
                       "window_h=setInterval(function(){window_n++},5);"
                       "</script>")
        handle = next(iter(tab.js.interval_handles))
        for _ in range(3):
            tab.js.dispatch_setinterval(handle, 5)
        self.assertEqual(tab.js.interp.evaljs("window_n"), 3)
        tab.js.interval_handles.clear()

    def test_clear_interval(self):
        tab = make_tab("<p>가</p><script>window_n=0;"
                       "window_h=setInterval(function(){window_n++},5);"
                       "</script>")
        handle = next(iter(tab.js.interval_handles))
        tab.js.dispatch_setinterval(handle, 5)
        tab.js.interp.evaljs("clearInterval(window_h)")
        tab.js.dispatch_setinterval(handle, 5)
        self.assertEqual(tab.js.interp.evaljs("window_n"), 1)

    def test_clear_from_inside_the_callback(self):
        tab = make_tab("<p>가</p><script>window_n=0;"
                       "window_h=setInterval(function(){window_n++;"
                       "if(window_n==2) clearInterval(window_h)},5);</script>")
        handle = next(iter(tab.js.interval_handles))
        for _ in range(5):
            tab.js.dispatch_setinterval(handle, 5)
        self.assertEqual(tab.js.interp.evaljs("window_n"), 2)

    def test_raf_runs_once(self):
        tab = make_tab("<p>가</p><script>window_n=0;"
                       "requestAnimationFrame(function(){window_n++});"
                       "</script>")
        tab.js.run_raf_handlers()
        tab.js.run_raf_handlers()
        self.assertEqual(tab.js.interp.evaljs("window_n"), 1)


class TestScriptErrors(unittest.TestCase):
    def test_function_ending_is_not_an_error(self):
        """x.onload = function(){} 로 끝나는 스크립트는 아주 흔하다."""
        _, out = logged("<p>가</p><script>window_f=function(){};</script>")
        self.assertNotIn("죽었습니다", out)

    def test_it_really_runs(self):
        tab = make_tab("<p>가</p><script>window_f=function(){};</script>")
        self.assertEqual(tab.js.interp.evaljs("typeof window_f"), "function")

    def test_real_errors_are_reported(self):
        _, out = logged("<p>가</p><script>이건(문법(오류</script>")
        self.assertIn("죽었습니다", out)


class TestCanvas(unittest.TestCase):
    def test_get_context(self):
        _, out = run('<canvas id="c"></canvas>',
                     'window_ok = !!c.getContext("2d"); window_ok')
        self.assertTrue(out)

    def test_unknown_context_is_null(self):
        _, out = run('<canvas id="c"></canvas>', 'c.getContext("webgl")')
        self.assertIsNone(out)

    def test_fill_rect_is_drawn(self):
        tab = make_tab('<canvas id="c" width="100" height="50"></canvas>'
                       '<script>var x=c.getContext("2d");'
                       'x.fillStyle="red"; x.fillRect(5,5,20,20);</script>')
        reds = [c for c in tab.flat_display_list
                if isinstance(c, DrawRect) and c.color == "red"]
        self.assertEqual(len(reds), 1)

    def test_fill_text(self):
        tab = make_tab('<canvas id="c"></canvas><script>'
                       'var x=c.getContext("2d"); x.fillText("그림글자",10,20);'
                       "</script>")
        self.assertIn("그림글자", drawn(tab))

    def test_clear(self):
        tab = make_tab('<canvas id="c"></canvas><script>'
                       'var x=c.getContext("2d"); x.fillStyle="red";'
                       "x.fillRect(0,0,10,10); x.clearRect(0,0,10,10);"
                       "</script>")
        self.assertEqual([c for c in tab.flat_display_list
                          if isinstance(c, DrawRect) and c.color == "red"], [])


class TestCookiesFromScript(unittest.TestCase):
    def setUp(self):
        cookiejar.clear()

    def tearDown(self):
        cookiejar.clear()

    def test_write_and_read(self):
        tab = make_tab("<p>가</p>")
        tab.root_frame.url = URL("http://example.com/")
        tab.js.interp.evaljs("document.cookie = 'x=9'")
        self.assertEqual(tab.js.interp.evaljs("document.cookie"), "x=9")

    def test_httponly_hidden(self):
        cookiejar.store_cookie("example.com", "secret=1; HttpOnly")
        cookiejar.store_cookie("example.com", "plain=2")
        tab = make_tab("<p>가</p>")
        tab.root_frame.url = URL("http://example.com/")
        self.assertEqual(tab.js.cookie_get(), "plain=2")


class TestPostMessageOrigin(unittest.TestCase):
    def test_star_matches_anything(self):
        self.assertTrue(origin_matches("*", "http://a:80"))
        self.assertTrue(origin_matches(None, "http://a:80"))

    def test_exact(self):
        self.assertTrue(origin_matches("http://a:80", "http://a:80"))
        self.assertFalse(origin_matches("http://b:80", "http://a:80"))

    def test_trailing_slash_ignored(self):
        self.assertTrue(origin_matches("http://a:80/", "http://a:80"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
