"""HTML 파서와 직렬화."""

import unittest

from wbe.dom.nodes import Element, Text, decode_entities, tree_to_list
from wbe.dom.parser import HTMLParser, SourceParser
from wbe.dom.serialize import serialize, serialize_children
from wbe.tests.helpers import find_el


def parse(html):
    return HTMLParser(html).parse()


def tags(tree):
    return [n.tag for n in tree_to_list(tree) if isinstance(n, Element)]


def all_text(tree):
    return " ".join(n.text for n in tree_to_list(tree)
                    if isinstance(n, Text))


class TestParser(unittest.TestCase):
    def test_implicit_html_body(self):
        self.assertEqual(tags(parse("글자")), ["html", "body"])

    def test_head_tags_go_to_head(self):
        tree = parse("<title>제목</title><p>본문</p>")
        title = find_el(tree, "title")[0]
        self.assertEqual(title.parent.tag, "head")

    def test_self_closing(self):
        tree = parse("<p>가<br>나</p>")
        self.assertEqual(len(find_el(tree, "br")), 1)

    def test_attributes(self):
        tree = parse('<div id="a" class="b c" hidden>글</div>')
        div = find_el(tree, "div")[0]
        self.assertEqual(div.attributes["id"], "a")
        self.assertEqual(div.attributes["class"], "b c")
        self.assertEqual(div.attributes["hidden"], "")

    def test_quoted_attribute_with_space_and_gt(self):
        tree = parse('<div title="a > b c">글</div>')
        self.assertEqual(find_el(tree, "div")[0].attributes["title"],
                         "a > b c")

    def test_comment_is_dropped(self):
        self.assertNotIn("숨김", all_text(parse("가<!-- 숨김 -->나")))

    def test_empty_comment(self):
        """`<!-->` 는 빈 주석이다. `<!--` 바로 뒤의 `>` 가 끝이다."""
        self.assertIn("나", all_text(parse("가<!-->나")))

    def test_unterminated_comment(self):
        self.assertNotIn("끝없음", all_text(parse("가<!-- 끝없음")))

    def test_script_content_is_text(self):
        tree = parse("<script>if (a<b) { }</script>")
        self.assertIn("a<b", all_text(tree))

    def test_script_close_is_case_insensitive(self):
        tree = parse("<script>x</SCRIPT><p>뒤</p>")
        self.assertIn("뒤", all_text(tree))

    def test_paragraph_auto_closes(self):
        tree = parse("<p>가<p>나")
        ps = find_el(tree, "p")
        self.assertEqual(len(ps), 2)
        self.assertIs(ps[0].parent, ps[1].parent)

    def test_li_auto_closes(self):
        tree = parse("<ul><li>가<li>나</ul>")
        lis = find_el(tree, "li")
        self.assertEqual(len(lis), 2)
        self.assertIs(lis[0].parent, lis[1].parent)

    def test_nested_list_keeps_nesting(self):
        tree = parse("<ul><li>가<ul><li>안</li></ul></li></ul>")
        self.assertEqual(len(find_el(tree, "ul")), 2)

    def test_mis_nested_formatting(self):
        tree = parse("<b>굵게<i>둘다</b>기울임만</i>")
        self.assertEqual(len(find_el(tree, "i")), 2)

    def test_well_nested_is_untouched(self):
        tree = parse("<b><i>글</i></b>")
        self.assertEqual(len(find_el(tree, "i")), 1)

    def test_entities_become_characters(self):
        """트리에는 원문이 아니라 문자를 담는다."""
        self.assertIn("<", all_text(parse("<p>a &lt; b</p>")))
        self.assertNotIn("&lt;", all_text(parse("<p>a &lt; b</p>")))

    def test_decode_entities(self):
        self.assertEqual(decode_entities("&amp;lt;"), "&lt;")

    def test_whitespace_only_text_skipped(self):
        tree = parse("<p>   </p>")
        self.assertEqual(all_text(tree), "")


class TestSourceParser(unittest.TestCase):
    def test_wraps_in_pre(self):
        tree = SourceParser("<p>글</p>").parse()
        self.assertEqual(len(find_el(tree, "pre")), 1)

    def test_tags_are_shown(self):
        tree = SourceParser("<p>글</p>").parse()
        self.assertIn("<p>", all_text(tree))

    def test_content_is_bold(self):
        tree = SourceParser("<p>글</p>").parse()
        b = find_el(tree, "b")[0]
        self.assertEqual(b.children[0].text, "글")


class TestSerialize(unittest.TestCase):
    def test_round_trip(self):
        tree = parse("<html><body><p>가<b>나</b></p></body></html>")
        body = find_el(tree, "body")[0]
        self.assertEqual(serialize_children(body), "<p>가<b>나</b></p>")

    def test_attributes_are_current(self):
        tree = parse('<p title="처음">글</p>')
        p = find_el(tree, "p")[0]
        p.attributes["title"] = "나중"
        self.assertIn('title="나중"', serialize(p))

    def test_empty_attribute_has_no_value(self):
        tree = parse('<input name="q" checked>')
        self.assertIn(" checked", serialize(find_el(tree, "input")[0]))

    def test_self_closing_has_no_end_tag(self):
        tree = parse("<br>")
        self.assertNotIn("</br>", serialize(find_el(tree, "br")[0]))

    def test_special_characters_escaped(self):
        tree = parse("<p>a &lt; b</p>")
        self.assertIn("&lt;", serialize(find_el(tree, "p")[0]))

    def test_quotes_escaped(self):
        tree = parse("<p>글</p>")
        p = find_el(tree, "p")[0]
        p.attributes["title"] = 'a"b'
        self.assertIn("&quot;", serialize(p))


if __name__ == "__main__":
    unittest.main(verbosity=2)
