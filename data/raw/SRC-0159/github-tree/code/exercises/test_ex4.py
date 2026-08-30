"""4장 연습문제 검증.

    python3 test_ex4.py
"""

import tkinter
import unittest

import ex4
from ex4 import HTMLParser, SourceParser, Element, Text, Layout, tag_name

_root = None


def setUpModule():
    global _root
    _root = tkinter.Tk()
    _root.withdraw()


def tearDownModule():
    if _root is not None:
        _root.destroy()


def parse(html):
    return HTMLParser(html).parse()


def find(node, tag):
    """트리에서 그 태그를 가진 요소를 모두 찾는다."""
    out = []
    if isinstance(node, Element):
        if node.tag == tag:
            out.append(node)
        for c in node.children:
            out += find(c, tag)
    return out


def all_text(node):
    if isinstance(node, Text):
        return node.text
    return "".join(all_text(c) for c in node.children)


def shape(node):
    """트리를 (태그, [자식...]) 로 단순화한다."""
    if isinstance(node, Text):
        return node.text
    return (node.tag, [shape(c) for c in node.children])


class Exercise41(unittest.TestCase):
    """4-1 주석"""

    def test_comment_removed(self):
        self.assertEqual(all_text(parse("가<!-- 숨김 -->나")), "가나")

    def test_comment_makes_no_element(self):
        tree = parse("<div><!-- x --></div>")
        self.assertEqual(find(tree, "div")[0].children, [])

    def test_angle_brackets_inside_comment(self):
        self.assertEqual(all_text(parse("가<!-- <b>굵게</b> -->나")), "가나")
        self.assertEqual(find(parse("가<!-- <b>x</b> -->나"), "b"), [])

    def test_empty_comment(self):
        """`<!-->` 는 빈 주석이다 — 본문이 던진 질문의 답."""
        self.assertEqual(all_text(parse("가<!-->나")), "가나")

    def test_unterminated_comment_eats_rest(self):
        self.assertEqual(all_text(parse("가<!-- 안 닫힘")), "가")

    def test_double_dash_inside(self):
        self.assertEqual(all_text(parse("가<!-- a -- b -->나")), "가나")


class Exercise42(unittest.TestCase):
    """4-2 문단"""

    def test_paragraphs_become_siblings(self):
        tree = parse("<p>hello<p>world</p>")
        ps = find(tree, "p")
        self.assertEqual(len(ps), 2)
        self.assertEqual(ps[0].parent, ps[1].parent, "형제여야 합니다")

    def test_paragraph_not_nested(self):
        ps = find(parse("<p>a<p>b</p>"), "p")
        self.assertNotIn(ps[1], ps[0].children)

    def test_paragraph_text_split(self):
        ps = find(parse("<p>hello<p>world</p>"), "p")
        self.assertEqual(all_text(ps[0]).strip(), "hello")
        self.assertEqual(all_text(ps[1]).strip(), "world")

    def test_list_items_become_siblings(self):
        lis = find(parse("<ul><li>a<li>b</ul>"), "li")
        self.assertEqual(len(lis), 2)
        self.assertEqual(lis[0].parent, lis[1].parent)

    def test_nested_list_still_nests(self):
        tree = parse("<ul><li>겉<ul><li>속</ul></ul>")
        outer = find(tree, "ul")[0]
        inner = find(tree, "ul")[1]
        self.assertEqual(len(find(tree, "ul")), 2)
        # 속 목록은 바깥 <li> 안에 있어야 한다
        self.assertIn(inner.parent.tag, ("li", "ul"))
        self.assertEqual(all_text(inner).strip(), "속")


class Exercise43(unittest.TestCase):
    """4-3 스크립트"""

    def test_less_than_inside_script(self):
        tree = parse("<script>if (a < b) x();</script>")
        self.assertIn("a < b", all_text(tree))

    def test_no_elements_from_script_body(self):
        tree = parse("<script>var s = '<b>';</script>")
        self.assertEqual(find(tree, "b"), [])

    def test_script_element_exists(self):
        self.assertEqual(len(find(parse("<script>x</script>"), "script")), 1)

    def test_content_after_script_parsed_normally(self):
        tree = parse("<script>a<b</script><b>굵게</b>")
        self.assertEqual(len(find(tree, "b")), 1)
        self.assertEqual(all_text(find(tree, "b")[0]), "굵게")

    def test_close_tag_is_case_insensitive(self):
        tree = parse("<script>x</SCRIPT><b>y</b>")
        self.assertEqual(len(find(tree, "b")), 1)


class Exercise44(unittest.TestCase):
    """4-4 따옴표 속성"""

    def test_space_in_value(self):
        tree = parse('<div class="a b c">x</div>')
        self.assertEqual(find(tree, "div")[0].attributes["class"], "a b c")

    def test_angle_bracket_in_value(self):
        tree = parse('<div title="a > b">x</div>')
        self.assertEqual(find(tree, "div")[0].attributes["title"], "a > b")
        self.assertEqual(all_text(tree), "x")

    def test_single_quotes(self):
        tree = parse("<div class='a b'>x</div>")
        self.assertEqual(find(tree, "div")[0].attributes["class"], "a b")

    def test_multiple_attributes(self):
        tree = parse('<div id="one" class="a b" data-x="y z">t</div>')
        attrs = find(tree, "div")[0].attributes
        self.assertEqual(attrs["id"], "one")
        self.assertEqual(attrs["class"], "a b")
        self.assertEqual(attrs["data-x"], "y z")

    def test_unquoted_still_works(self):
        tree = parse("<div id=one>x</div>")
        self.assertEqual(find(tree, "div")[0].attributes["id"], "one")

    def test_valueless_attribute(self):
        tree = parse("<input disabled>")
        self.assertEqual(find(tree, "input")[0].attributes["disabled"], "")


class Exercise45(unittest.TestCase):
    """4-5 구문 강조"""

    def setUp(self):
        self.tree = SourceParser("<b>안녕</b>").parse()

    def test_wrapped_in_pre(self):
        self.assertEqual(len(find(self.tree, "pre")), 1)

    def test_tags_shown_as_text(self):
        self.assertIn("<b>", all_text(self.tree))
        self.assertIn("</b>", all_text(self.tree))

    def test_content_is_bold(self):
        bolds = find(self.tree, "b")
        self.assertTrue(any(all_text(b) == "안녕" for b in bolds))

    def test_tag_text_not_bold(self):
        for b in find(self.tree, "b"):
            self.assertNotIn("<", all_text(b))

    def test_source_shows_everything(self):
        src = '<div class="a b">x</div>'
        self.assertIn('class="a b"', all_text(SourceParser(src).parse()))


class Exercise46(unittest.TestCase):
    """4-6 잘못 중첩된 서식 태그"""

    HTML = "<b>Bold <i>both</i></b><i> italic</i>"
    BAD = "<b>Bold <i>both</b> italic</i>"

    def test_all_text_survives(self):
        self.assertEqual(all_text(parse(self.BAD)).replace(" ", ""),
                         "Boldbothitalic")

    def test_b_closes_before_i(self):
        tree = parse(self.BAD)
        b = find(tree, "b")[0]
        self.assertNotIn("italic", all_text(b), "</b> 뒤 글자는 굵으면 안 됩니다")

    def test_i_reopened_after(self):
        tree = parse(self.BAD)
        italics = find(tree, "i")
        self.assertGreaterEqual(len(italics), 2, "</b> 뒤에 <i> 를 다시 열어야 합니다")
        self.assertIn("italic", "".join(all_text(i) for i in italics))

    def test_both_is_bold_and_italic(self):
        tree = parse(self.BAD)
        b = find(tree, "b")[0]
        self.assertIn("both", all_text(b))
        self.assertTrue(any("both" in all_text(i) for i in find(b, "i")))

    def test_correct_nesting_unchanged(self):
        good = parse(self.HTML)
        self.assertEqual(len(find(good, "b")), 1)
        self.assertEqual(len(find(good, "i")), 2)

    def test_stray_close_tag_ignored(self):
        self.assertEqual(all_text(parse("가</b>나")), "가나")


class LayoutCarriedForward(unittest.TestCase):
    """3장까지의 배치 기능이 트리에서도 그대로 도는지"""

    def place(self, html, width=800):
        return Layout(parse(html), width).display_list

    def test_bold_still_works(self):
        dl = self.place("<b>굵게</b>")
        self.assertEqual(dl[0][3].cget("weight"), "bold")

    def test_title_still_centered(self):
        dl = self.place('<h1 class="title">제목</h1>')
        self.assertGreater(dl[0][0], ex4.HSTEP)

    def test_pre_still_preserves_spaces(self):
        dl = self.place("<pre>a    b</pre>")
        self.assertIn("a    b", [t for _, _, t, _ in dl])

    def test_smallcaps_still_works(self):
        dl = self.place("<abbr>abc</abbr>")
        self.assertEqual("".join(t for _, _, t, _ in dl), "ABC")

    def test_superscript_still_smaller(self):
        dl = self.place("가<sup>나</sup>")
        self.assertLess(dl[1][3].cget("size"), dl[0][3].cget("size"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
