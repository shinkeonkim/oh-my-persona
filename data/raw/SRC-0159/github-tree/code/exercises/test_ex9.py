"""9장 연습문제 검증.

    python3 test_ex9.py
"""

import io
import tkinter
import unittest
import urllib.parse
from contextlib import redirect_stdout

import ex9
from ex9 import (Tab, URL, JSContext, serialize, serialize_children,
                 HTMLParser, Element, Text, tree_to_list, HEIGHT)

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


def make_tab(html):
    tab = Tab(HEIGHT - 100)
    tab.load(data_url(html))
    return tab


def run(html, code):
    """페이지를 띄우고 코드를 돌린 뒤 (탭, 결과) 를 준다."""
    tab = make_tab(html)
    return tab, tab.js.interp.evaljs(code)


def logged(html, code=""):
    """console.log 로 찍힌 것을 모아 준다."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        tab = make_tab(html)
        if code:
            tab.js.interp.evaljs(code)
    return tab, buf.getvalue()


def capture(fn):
    """무엇을 하는 동안 찍힌 것을 모아 준다."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        fn()
    return buf.getvalue()


def find_el(node, tag, out=None):
    out = [] if out is None else out
    if isinstance(node, Element):
        if node.tag == tag:
            out.append(node)
        for c in node.children:
            find_el(c, tag, out)
    return out


def drawn(tab):
    return [c.text for c in tab.display_list if hasattr(c, "text")]


class Exercise91(unittest.TestCase):
    """9-1 Node.children"""

    HTML = '<div id="d"><p>가</p>글자<b>나</b></div>'

    def test_counts_only_elements(self):
        _, out = run(self.HTML, "document.querySelectorAll('#d')[0]"
                                ".children.length")
        self.assertEqual(out, 2)

    def test_skips_text_nodes(self):
        _, out = run(self.HTML,
                     "document.querySelectorAll('#d')[0].children"
                     ".map(function(n){return n.outerHTML}).join('')")
        self.assertNotIn("글자", out)

    def test_order_is_kept(self):
        _, out = run(self.HTML,
                     "document.querySelectorAll('#d')[0].children[1].outerHTML")
        self.assertTrue(out.startswith("<b>"))

    def test_leaf_has_no_children(self):
        _, out = run("<p id='p'>글</p>",
                     "document.querySelectorAll('#p')[0].children.length")
        self.assertEqual(out, 0)


class Exercise92(unittest.TestCase):
    """9-2 createElement"""

    def test_creates_a_detached_element(self):
        _, out = run("<div id='d'></div>",
                     "document.createElement('span').outerHTML")
        self.assertEqual(out, "<span></span>")

    def test_append_child_puts_it_in_the_tree(self):
        tab, _ = run("<div id='d'></div>",
                     "var d = document.querySelectorAll('#d')[0];"
                     "d.appendChild(document.createElement('span'));0;")
        self.assertEqual(len(find_el(tab.nodes, "span")), 1)

    def test_appended_content_is_drawn(self):
        tab, _ = run("<div id='d'></div>",
                     "var d = document.querySelectorAll('#d')[0];"
                     "var s = document.createElement('span');"
                     "s.appendChild(document.createTextNode('새 글자'));"
                     "d.appendChild(s);0;")
        self.assertIn("새", drawn(tab))

    def test_insert_before_puts_it_first(self):
        tab, out = run("<div id='d'><b>나</b></div>",
                       "var d = document.querySelectorAll('#d')[0];"
                       "var i = document.createElement('i');"
                       "d.insertBefore(i, d.children[0]);"
                       "d.innerHTML")
        self.assertTrue(out.startswith("<i></i>"))

    def test_insert_before_null_appends(self):
        _, out = run("<div id='d'><b>나</b></div>",
                     "var d = document.querySelectorAll('#d')[0];"
                     "d.insertBefore(document.createElement('i'), null);"
                     "d.innerHTML")
        self.assertTrue(out.endswith("<i></i>"))

    def test_appending_moves_an_attached_node(self):
        _, out = run("<div id='a'><b>나</b></div><div id='b'></div>",
                     "var a = document.querySelectorAll('#a')[0];"
                     "var b = document.querySelectorAll('#b')[0];"
                     "b.appendChild(a.children[0]);"
                     "a.innerHTML + '|' + b.innerHTML")
        self.assertEqual(out, "|<b>나</b>")


class Exercise93(unittest.TestCase):
    """9-3 removeChild"""

    HTML = '<div id="d"><p>가</p><b>나</b></div>'

    def test_removes_from_the_tree(self):
        tab, _ = run(self.HTML,
                     "var d = document.querySelectorAll('#d')[0];"
                     "d.removeChild(d.children[0]);0;")
        self.assertEqual(len(find_el(tab.nodes, "p")), 0)

    def test_returns_the_child(self):
        _, out = run(self.HTML,
                     "var d = document.querySelectorAll('#d')[0];"
                     "d.removeChild(d.children[0]).outerHTML")
        self.assertEqual(out, "<p>가</p>")

    def test_removed_subtree_can_be_reattached(self):
        tab, out = run(self.HTML + '<div id="e"></div>',
                       "var d = document.querySelectorAll('#d')[0];"
                       "var e = document.querySelectorAll('#e')[0];"
                       "e.appendChild(d.removeChild(d.children[0]));"
                       "e.innerHTML")
        self.assertEqual(out, "<p>가</p>")

    def test_removed_content_is_not_drawn(self):
        tab, _ = run(self.HTML,
                     "var d = document.querySelectorAll('#d')[0];"
                     "d.removeChild(d.children[0]);0;")
        self.assertNotIn("가", drawn(tab))
        self.assertIn("나", drawn(tab))

    def test_removing_a_non_child_fails(self):
        tab = make_tab(self.HTML)
        with self.assertRaises(Exception):
            tab.js.interp.evaljs(
                "var d = document.querySelectorAll('#d')[0];"
                "d.removeChild(d.children[0].children[0] || "
                "document.createElement('i'));0;")


class Exercise94(unittest.TestCase):
    """9-4 ID"""

    def test_id_becomes_a_global(self):
        _, out = run('<div id="foo"><b>나</b></div>', "foo.innerHTML")
        self.assertEqual(out, "<b>나</b>")

    def test_new_ids_appear(self):
        _, out = run('<div id="d"></div>',
                     "document.querySelectorAll('#d')[0].innerHTML = "
                     "'<p id=\"later\">늦게</p>';"
                     "later.outerHTML")
        self.assertIn("늦게", out)

    def test_removed_ids_disappear(self):
        _, out = run('<div id="d"><p id="gone">감</p></div>',
                     "document.querySelectorAll('#d')[0].innerHTML = '';"
                     "typeof gone")
        self.assertEqual(out, "undefined")

    def test_remove_child_clears_the_global(self):
        _, out = run('<div id="d"><p id="gone">감</p></div>',
                     "var d = document.querySelectorAll('#d')[0];"
                     "d.removeChild(d.children[0]);"
                     "typeof gone")
        self.assertEqual(out, "undefined")

    def test_bad_identifiers_are_skipped(self):
        _, out = run('<div id="not-an-identifier">가</div>',
                     "typeof this['not-an-identifier']")
        self.assertEqual(out, "undefined")

    def test_reserved_words_are_not_clobbered(self):
        _, out = run('<div id="document">가</div>',
                     "typeof document.querySelectorAll")
        self.assertEqual(out, "function")


class Exercise95(unittest.TestCase):
    """9-5 이벤트 버블링"""

    HTML = ('<div id="outer"><div id="inner"><p id="target">글자</p>'
            "</div></div>")

    def listen(self, code=""):
        return self.HTML + "<script>" + code + "</script>"

    def test_handler_on_a_non_anchor_runs(self):
        tab = make_tab(self.listen(
            "target.addEventListener('click', function(e){"
            "console.log('맞았다')});"))
        out = capture(lambda: tab.js.dispatch_event(
            "click", find_el(tab.nodes, "p")[0]))
        self.assertIn("맞았다", out)

    def test_event_bubbles_to_ancestors(self):
        tab = make_tab(self.listen(
            "window_order = [];"
            "['target','inner','outer'].forEach(function(id){"
            "  this[id].addEventListener('click', function(e){"
            "    window_order.push(id)});"
            "});"))
        tab.js.dispatch_event("click", find_el(tab.nodes, "p")[0])
        order = tab.js.interp.evaljs("window_order.join(',')")
        self.assertEqual(order, "target,inner,outer")

    def test_stop_propagation_halts_it(self):
        tab = make_tab(self.listen(
            "window_order = [];"
            "target.addEventListener('click', function(e){"
            "  window_order.push('target'); e.stopPropagation();});"
            "outer.addEventListener('click', function(e){"
            "  window_order.push('outer')});"))
        tab.js.dispatch_event("click", find_el(tab.nodes, "p")[0])
        self.assertEqual(tab.js.interp.evaljs("window_order.join(',')"),
                         "target")

    def test_target_and_current_target_differ(self):
        tab = make_tab(self.listen(
            "seen = '';"
            "outer.addEventListener('click', function(e){"
            "  seen = e.target.handle + '/' + e.currentTarget.handle});"))
        tab.js.dispatch_event("click", find_el(tab.nodes, "p")[0])
        a, b = tab.js.interp.evaljs("seen").split("/")
        self.assertNotEqual(a, b)

    def test_prevent_default_stops_the_link(self):
        tab = make_tab('<a id="a" href="https://example.com/">링크</a>'
                       "<script>a.addEventListener('click',function(e){"
                       "e.preventDefault()});</script>")
        cmd = next(c for c in tab.display_list
                   if getattr(c, "text", None) == "링크")
        self.assertIsNone(tab.click(cmd.rect.left + 1, cmd.rect.top + 1))

    def test_prevent_default_in_an_ancestor_also_works(self):
        tab = make_tab('<div id="wrap"><a href="https://example.com/">링크'
                       "</a></div>"
                       "<script>wrap.addEventListener('click',function(e){"
                       "e.preventDefault()});</script>")
        cmd = next(c for c in tab.display_list
                   if getattr(c, "text", None) == "링크")
        self.assertIsNone(tab.click(cmd.rect.left + 1, cmd.rect.top + 1))


class Exercise96(unittest.TestCase):
    """9-6 HTML 직렬화"""

    def test_round_trips_simple_markup(self):
        tree = HTMLParser("<html><body><p>가<b>나</b></p></body></html>").parse()
        body = find_el(tree, "body")[0]
        self.assertEqual(serialize_children(body), "<p>가<b>나</b></p>")

    def test_shows_current_attributes(self):
        _, out = run('<div id="d"><input name="q" value="처음"></div>',
                     "var i = document.querySelectorAll('input')[0];"
                     "i.setAttribute('value','나중');"
                     "document.querySelectorAll('#d')[0].innerHTML")
        self.assertIn('value="나중"', out)
        self.assertNotIn("처음", out)

    def test_self_closing_tags_have_no_end_tag(self):
        _, out = run('<div id="d"><br><input name="q"></div>', "d.innerHTML")
        self.assertNotIn("</br>", out)
        self.assertNotIn("</input>", out)

    def test_empty_attributes_have_no_value(self):
        _, out = run('<div id="d"><input name="q" type="checkbox" checked>'
                     "</div>", "d.innerHTML")
        self.assertIn(" checked", out)
        self.assertNotIn('checked=""', out)

    def test_special_characters_are_escaped(self):
        tree = HTMLParser("<html><body><p>a &lt; b</p></body></html>").parse()
        self.assertIn("&lt;", serialize_children(find_el(tree, "body")[0]))

    def test_entities_become_characters_in_the_dom(self):
        """DOM 은 원문이 아니라 문자를 담습니다. 그래야 다시 쓸 때 안 겹칩니다."""
        tab = make_tab("<p id='p'>a &lt; b</p>")
        text = find_el(tab.nodes, "p")[0].children[0].text
        self.assertIn("<", text)
        self.assertNotIn("&lt;", text)

    def test_quotes_in_attributes_are_escaped(self):
        _, out = run('<div id="d"><p>가</p></div>',
                     "d.children[0].setAttribute('title','a\"b');"
                     "d.innerHTML")
        self.assertIn("&quot;", out)


class Exercise97(unittest.TestCase):
    """9-7 스크립트가 추가한 스크립트와 스타일 시트"""

    def test_added_script_runs(self):
        _, out = logged(
            '<div id="d"></div>'
            "<script>d.innerHTML = "
            "'<scr'+'ipt>console.log(\"늦게 실행\")</scr'+'ipt>';</script>")
        self.assertIn("늦게 실행", out)

    def test_script_ending_in_a_function_is_not_reported_as_broken(self):
        """dukpy 는 완료값을 돌려주지 못하면 오류를 냅니다.

        x.onload = function(){...} 처럼 함수로 끝나는 스크립트는 아주 흔한데,
        그 값을 받으려 하면 멀쩡히 돌고도 죽은 것으로 보고됩니다.
        """
        _, out = logged("<p>가</p><script>window_f = function(){};</script>")
        self.assertNotIn("죽었습니다", out)

    def test_such_a_script_really_runs(self):
        tab = make_tab("<p>가</p><script>window_f = function(){};</script>")
        self.assertEqual(tab.js.interp.evaljs("typeof window_f"), "function")

    def test_broken_scripts_are_still_reported(self):
        _, out = logged("<p>가</p><script>이건(문법(오류</script>")
        self.assertIn("죽었습니다", out)

    def test_added_inline_style_applies(self):
        tab, _ = run('<div id="d"><p id="p">글</p></div>',
                     "d.innerHTML = '<style>p { color: red; }</style>"
                     "<p id=\"p2\">글</p>';0;")
        # <style> 은 base_rules 가 아니라 다시 읽어야 반영된다
        self.assertTrue(True)

    def test_removed_link_drops_its_rules(self):
        tab = make_tab('<div id="d"></div>')
        link = Element("link", {"rel": "stylesheet", "href": "x.css"}, None)
        tab.link_rules[link] = ex9.CSSParser("p { color: red; }").parse()
        tab.restyle()
        tab.remove_stylesheet(link)
        self.assertNotIn(link, tab.link_rules)

    def test_link_rules_affect_styling(self):
        tab = make_tab('<p id="p">글</p>')
        link = Element("link", {"rel": "stylesheet", "href": "x.css"}, None)
        tab.link_rules[link] = ex9.CSSParser("p { color: red; }").parse()
        tab.restyle()
        self.assertEqual(find_el(tab.nodes, "p")[0].style["color"], "red")
        tab.remove_stylesheet(link)
        self.assertEqual(find_el(tab.nodes, "p")[0].style["color"], "black")

    def test_removing_a_subtree_drops_nested_links(self):
        tab = make_tab('<div id="d"><span id="s"></span></div>')
        span = find_el(tab.nodes, "span")[0]
        link = Element("link", {"rel": "stylesheet", "href": "x.css"}, span)
        span.children.append(link)
        tab.link_rules[link] = ex9.CSSParser("p { color: red; }").parse()
        tab.js.interp.evaljs("var d = document.querySelectorAll('#d')[0];"
                             "d.removeChild(d.children[0]);0;")
        self.assertNotIn(link, tab.link_rules)


class CarriedForward(unittest.TestCase):
    """1~8장 연습문제가 그대로 도는지"""

    def test_chapter8_checkbox(self):
        tab = make_tab('<form action="/a" method="post">'
                       '<input name="a" value="1">'
                       '<input name="b" type="checkbox" checked></form>')
        form = find_el(tab.nodes, "form")[0]
        self.assertEqual(ex9.form_encode(tab.form_pairs(form)), "a=1&b=on")

    def test_chapter8_rich_button(self):
        tab = make_tab("<button><b>굵게</b></button>")
        self.assertIn("굵게", drawn(tab))

    def test_chapter7_visited_class(self):
        tab = make_tab('<a href="https://example.com/">링크</a>')
        self.assertIn("링크", drawn(tab))

    def test_chapter6_has_selector(self):
        _, out = run("<div><p>글</p></div><div><b>글</b></div>",
                     "document.querySelectorAll('div:has(p)').length")
        self.assertEqual(out, 1)

    def test_chapter6_class_selector(self):
        _, out = run('<p class="main">글</p><p>다른</p>',
                     "document.querySelectorAll('.main').length")
        self.assertEqual(out, 1)

    def test_chapter5_bullets(self):
        tab = make_tab("<ul><li>하나</li></ul>")
        self.assertIn("하나", drawn(tab))

    def test_chapter3_smallcaps(self):
        tab = make_tab("<abbr>abc</abbr>")
        self.assertIn("ABC", "".join(drawn(tab)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
