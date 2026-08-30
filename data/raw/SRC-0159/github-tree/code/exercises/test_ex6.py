"""6장 연습문제 검증.

    python3 test_ex6.py
"""

import tkinter
import unittest

import ex6
from ex6 import (CSSParser, DocumentLayout, BlockLayout, DrawRect, DrawText,
                 HTMLParser, Element, Text, style, cascade_priority,
                 paint_tree, tree_to_list, group_children, is_block,
                 expand_shorthand, parse_px, DEFAULT_STYLE_SHEET,
                 TagSelector, ClassSelector, DescendantSelector,
                 SelectorSequence, HasSelector, IMPORTANT_BONUS)

_root = None


def setUpModule():
    global _root
    _root = tkinter.Tk()
    _root.withdraw()


def tearDownModule():
    if _root is not None:
        _root.destroy()


def styled(html, css="", browser_css=True):
    """HTML 을 파싱하고 스타일을 입힌 트리를 돌려준다."""
    tree = HTMLParser(html).parse()
    rules = DEFAULT_STYLE_SHEET.copy() if browser_css else []
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


def find_el(node, tag, out=None):
    out = [] if out is None else out
    if isinstance(node, Element):
        if node.tag == tag:
            out.append(node)
        for c in node.children:
            find_el(c, tag, out)
    return out


def boxes(obj, out=None):
    out = [] if out is None else out
    for c in obj.children:
        out.append(c)
        boxes(c, out)
    return out


def texts(cmds):
    return [c for c in cmds if isinstance(c, DrawText)]


def find_text(cmds, word):
    return next(c for c in texts(cmds) if c.text == word)


class Exercise61(unittest.TestCase):
    """6-1 폰트"""

    def test_font_family_is_inherited(self):
        tree = styled("<div><p>글</p></div>", "div { font-family: Courier; }")
        p = find_el(tree, "p")[0]
        self.assertEqual(p.style["font-family"], "Courier")

    def test_code_is_monospace_by_default(self):
        tree = styled("<code>x</code>")
        self.assertEqual(find_el(tree, "code")[0].style["font-family"],
                         "monospace")

    def test_plain_text_has_no_family(self):
        tree = styled("<p>글</p>")
        self.assertEqual(find_el(tree, "p")[0].style["font-family"], "")

    def test_font_cache_keeps_families_apart(self):
        _, cmds = build("<p>보통</p><code>고정폭</code>")
        normal = find_text(cmds, "보통").font
        mono = find_text(cmds, "고정폭").font
        self.assertNotEqual(normal.cget("family"), mono.cget("family"),
                            "폰트 캐시가 family 를 무시하면 안 됩니다")

    def test_family_reaches_the_drawn_font(self):
        _, cmds = build("<p>글</p>", "p { font-family: Courier; }")
        self.assertEqual(find_text(cmds, "글").font.cget("family"), "Courier")


class Exercise62(unittest.TestCase):
    """6-2 너비/높이"""

    def test_parses_pixels(self):
        self.assertEqual(parse_px("120px"), 120.0)

    def test_auto_is_none(self):
        self.assertIsNone(parse_px("auto"))
        self.assertIsNone(parse_px(""))

    def test_width_applied(self):
        doc, _ = build("<div>글</div>", "div { width: 120px; }")
        div = next(b for b in boxes(doc) if b.element("div"))
        self.assertEqual(div.width, 120)

    def test_height_applied(self):
        doc, _ = build("<div>글</div>", "div { height: 300px; }")
        div = next(b for b in boxes(doc) if b.element("div"))
        self.assertEqual(div.height, 300)

    def test_auto_width_fills_parent(self):
        doc, _ = build("<div>글</div>", "div { width: auto; }")
        div = next(b for b in boxes(doc) if b.element("div"))
        html = next(b for b in boxes(doc) if b.element("html"))
        self.assertEqual(div.width, html.width)

    def test_narrow_width_wraps_earlier(self):
        _, wide = build("<div>" + "가나 " * 40 + "</div>")
        _, narrow = build("<div>" + "가나 " * 40 + "</div>",
                          "div { width: 100px; }")
        self.assertGreater(len({c.top for c in texts(narrow)}),
                           len({c.top for c in texts(wide)}))


class Exercise63(unittest.TestCase):
    """6-3 클래스 선택자"""

    def test_class_selector_matches(self):
        tree = styled('<p class="main">글</p>', ".main { color: red; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "red")

    def test_does_not_match_other_class(self):
        tree = styled('<p class="other">글</p>', ".main { color: red; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "black")

    def test_multiple_classes_on_one_element(self):
        tree = styled('<p class="a b">글</p>', ".b { color: red; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "red")

    def test_beats_tag_selector(self):
        tree = styled('<p class="main">글</p>',
                      ".main { color: red; } p { color: blue; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "red")

    def test_priority_is_higher_than_tag(self):
        self.assertGreater(ClassSelector("a").priority,
                           TagSelector("p").priority)


class Exercise64(unittest.TestCase):
    """6-4 display"""

    def test_block_tags_come_from_css(self):
        tree = styled("<div>글</div>")
        self.assertEqual(find_el(tree, "div")[0].style["display"], "block")

    def test_default_is_inline(self):
        tree = styled("<span>글</span>")
        self.assertEqual(tree.style.get("display"), "block")   # html
        self.assertEqual(find_el(tree, "span")[0].style.get("display",
                                                            "inline"), "inline")

    def test_css_can_make_a_span_block(self):
        tree = styled("<div><span>가</span><span>나</span></div>",
                      "span { display: block; }")
        span = find_el(tree, "span")[0]
        self.assertTrue(is_block(span))

    def test_display_block_splits_lines(self):
        _, cmds = build("<div><span>가</span><span>나</span></div>",
                        "span { display: block; }")
        self.assertNotEqual(find_text(cmds, "가").top,
                            find_text(cmds, "나").top)

    def test_display_inline_joins_lines(self):
        _, cmds = build("<div><p>가</p><p>나</p></div>",
                        "p { display: inline; }")
        self.assertEqual(find_text(cmds, "가").top, find_text(cmds, "나").top)


class Exercise65(unittest.TestCase):
    """6-5 단축 속성"""

    def test_expands_all_four(self):
        out = expand_shorthand("font", "italic bold 100% Times")
        self.assertEqual(out, {"font-style": "italic", "font-weight": "bold",
                               "font-size": "100%", "font-family": "Times"})

    def test_size_and_family_only(self):
        out = expand_shorthand("font", "12px Courier")
        self.assertEqual(out["font-size"], "12px")
        self.assertEqual(out["font-family"], "Courier")
        self.assertNotIn("font-style", out)

    def test_other_properties_untouched(self):
        self.assertEqual(expand_shorthand("color", "red"), {"color": "red"})

    def test_works_through_the_parser(self):
        tree = styled("<p>글</p>", "p { font: italic bold 100% Times; }")
        s = find_el(tree, "p")[0].style
        self.assertEqual(s["font-style"], "italic")
        self.assertEqual(s["font-weight"], "bold")
        self.assertEqual(s["font-family"], "Times")

    def test_later_longhand_wins(self):
        tree = styled("<p>글</p>",
                      "p { font: italic bold 100% Times; font-weight: normal; }")
        self.assertEqual(find_el(tree, "p")[0].style["font-weight"], "normal")


class Exercise66(unittest.TestCase):
    """6-6 인라인 스타일 시트"""

    def rules_from(self, html):
        tree = HTMLParser(html).parse()
        rules = []
        for n in tree_to_list(tree, []):
            if isinstance(n, Element) and n.tag == "style":
                text = "".join(c.text for c in n.children
                               if isinstance(c, Text))
                rules.extend(CSSParser(text).parse())
        return rules

    def test_style_tag_is_parsed(self):
        rules = self.rules_from("<style>p { color: red; }</style><p>글</p>")
        self.assertEqual(len(rules), 1)

    def test_style_tag_applies(self):
        html = "<style>p { color: red; }</style><p>글</p>"
        tree = HTMLParser(html).parse()
        rules = DEFAULT_STYLE_SHEET + self.rules_from(html)
        style(tree, sorted(rules, key=cascade_priority))
        self.assertEqual(find_el(tree, "p")[0].style["color"], "red")

    def test_style_content_is_not_drawn(self):
        _, cmds = build("<style>p { color: red; }</style><p>글</p>")
        self.assertNotIn("color:", " ".join(c.text for c in texts(cmds)))

    def test_style_content_kept_as_text(self):
        tree = HTMLParser("<style>p { color: red; }</style>").parse()
        el = find_el(tree, "style")[0]
        self.assertIn("color", el.children[0].text)


class Exercise67(unittest.TestCase):
    """6-7 빠른 자손 선택자"""

    def test_matches_direct_child(self):
        tree = styled("<div><p>글</p></div>", "div p { color: red; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "red")

    def test_matches_deep_descendant(self):
        tree = styled("<div><section><p>글</p></section></div>",
                      "div p { color: red; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "red")

    def test_requires_the_ancestor(self):
        tree = styled("<section><p>글</p></section>", "div p { color: red; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "black")

    def test_three_levels(self):
        tree = styled("<div><section><p><b>글</b></p></section></div>",
                      "div section b { color: red; }")
        self.assertEqual(find_el(tree, "b")[0].style["color"], "red")

    def test_order_matters(self):
        tree = styled("<div><section><p>글</p></section></div>",
                      "section div p { color: red; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "black")

    def test_walks_ancestors_only_once(self):
        """O(n + d): 조상 사슬을 선택자 개수만큼 되풀이해 훑지 않는다."""
        depth = 200
        html = "<div>" * depth + "<p>글</p>" + "</div>" * depth
        tree = HTMLParser(html).parse()
        p = find_el(tree, "p")[0]

        calls = [0]

        class Counting:
            def __init__(self, inner):
                self.inner = inner
                self.priority = inner.priority

            def matches(self, node):
                calls[0] += 1
                return self.inner.matches(node)

        sel = DescendantSelector([Counting(TagSelector(t))
                                  for t in ("a", "b", "c", "p")])
        self.assertFalse(sel.matches(p))
        # d 번 훑고 끝난다. O(n*d) 였다면 800 번을 넘겼을 것이다.
        self.assertLessEqual(calls[0], depth + 8)


class Exercise68(unittest.TestCase):
    """6-8 선택자 시퀀스"""

    def test_tag_and_class_together(self):
        tree = styled('<span class="announce">글</span>',
                      "span.announce { color: red; }")
        self.assertEqual(find_el(tree, "span")[0].style["color"], "red")

    def test_wrong_tag_does_not_match(self):
        tree = styled('<p class="announce">글</p>',
                      "span.announce { color: red; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "black")

    def test_wrong_class_does_not_match(self):
        tree = styled('<span class="other">글</span>',
                      "span.announce { color: red; }")
        self.assertEqual(find_el(tree, "span")[0].style["color"], "black")

    def test_priority_is_the_sum(self):
        sel = CSSParser("span.announce { color: red; }").parse()[0][0]
        self.assertEqual(sel.priority,
                         TagSelector("span").priority
                         + ClassSelector("announce").priority)

    def test_sequence_beats_lone_class(self):
        tree = styled('<span class="a">글</span>',
                      ".a { color: blue; } span.a { color: red; }")
        self.assertEqual(find_el(tree, "span")[0].style["color"], "red")

    def test_sequence_inside_descendant(self):
        tree = styled('<div><span class="a">글</span></div>',
                      "div span.a { color: red; }")
        self.assertEqual(find_el(tree, "span")[0].style["color"], "red")


class Exercise69(unittest.TestCase):
    """6-9 !important"""

    def test_important_beats_higher_priority(self):
        tree = styled('<p class="a">글</p>',
                      "p { color: red !important; } .a { color: blue; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "red")

    def test_important_beats_inline_free_rules(self):
        tree = styled("<p>글</p>",
                      "p { color: red !important; } p { color: blue; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "red")

    def test_normal_declarations_still_cascade(self):
        tree = styled("<p>글</p>",
                      "p { color: red !important; font-style: italic; }")
        s = find_el(tree, "p")[0].style
        self.assertEqual(s["color"], "red")
        self.assertEqual(s["font-style"], "italic")

    def test_priority_bonus(self):
        rules = CSSParser("p { color: red !important; }").parse()
        self.assertEqual(rules[0][0].priority,
                         TagSelector("p").priority + IMPORTANT_BONUS)

    def test_two_importants_use_normal_order(self):
        tree = styled('<p class="a">글</p>',
                      "p { color: red !important; } .a { color: blue !important; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "blue")


class Exercise610(unittest.TestCase):
    """6-10 :has 선택자"""

    def test_ancestor_with_descendant_matches(self):
        tree = styled("<div><p>글</p></div>", "div:has(p) { color: red; }")
        self.assertEqual(find_el(tree, "div")[0].style["color"], "red")

    def test_ancestor_without_descendant_does_not(self):
        tree = styled("<div><span>글</span></div>", "div:has(p) { color: red; }")
        self.assertEqual(find_el(tree, "div")[0].style["color"], "black")

    def test_deep_descendant_counts(self):
        tree = styled("<div><section><p>글</p></section></div>",
                      "div:has(p) { color: red; }")
        self.assertEqual(find_el(tree, "div")[0].style["color"], "red")

    def test_only_ancestors_match(self):
        tree = styled("<div><p>가</p></div><div><span>나</span></div>",
                      "div:has(p) { color: red; }")
        first, second = find_el(tree, "div")
        self.assertEqual(first.style["color"], "red")
        self.assertEqual(second.style["color"], "black")

    def test_class_inside_has(self):
        tree = styled('<div><p class="a">글</p></div>',
                      "div:has(.a) { color: red; }")
        self.assertEqual(find_el(tree, "div")[0].style["color"], "red")

    def test_prepare_visits_each_node_once(self):
        """상각 O(1): 조상 표시가 이미 된 곳에서 멈춘다."""
        depth = 50
        html = "<div>" * depth + "<p>글</p>" + "</div>" * depth
        tree = HTMLParser(html).parse()
        sel = CSSParser("div:has(p) { color: red; }").parse()[0][0]
        sel.prepare(tree)
        divs = find_el(tree, "div")
        self.assertTrue(all(id(d) in sel.satisfied for d in divs))


class CarriedForward(unittest.TestCase):
    """1~5장 연습문제가 그대로 살아 있는지"""

    def test_chapter5_toc_label(self):
        _, cmds = build('<nav id="toc"><ul><li>1장</li></ul></nav>')
        self.assertIn(ex6.TOC_LABEL, [c.text for c in texts(cmds)])

    def test_chapter5_bullets(self):
        _, cmds = build("<ul><li>하나</li><li>둘</li></ul>")
        black = [c for c in cmds if isinstance(c, DrawRect) and c.color == "black"]
        self.assertEqual(len(black), 2)

    def test_chapter5_anonymous_box(self):
        tree = styled("<div><i>가</i><b>나</b><p>다</p></div>")
        div = find_el(tree, "div")[0]
        self.assertEqual(len(group_children(div)), 2)

    def test_chapter5_head_hidden(self):
        _, cmds = build("<head><title>제목</title></head><body>본문</body>")
        drawn = [c.text for c in texts(cmds)]
        self.assertNotIn("제목", drawn)
        self.assertIn("본문", drawn)

    def test_chapter4_comment(self):
        _, cmds = build("가<!-- 숨김 -->나")
        self.assertNotIn("숨김", " ".join(c.text for c in texts(cmds)))

    def test_chapter3_pre_preserves_spaces(self):
        _, cmds = build("<pre>a    b</pre>")
        self.assertIn("a    b", [c.text for c in texts(cmds)])

    def test_chapter3_smallcaps(self):
        _, cmds = build("<abbr>abc</abbr>")
        self.assertIn("ABC", "".join(c.text for c in texts(cmds)))

    def test_chapter2_about_blank(self):
        self.assertEqual(ex6.parse_url("!!!").scheme, "about")


if __name__ == "__main__":
    unittest.main(verbosity=2)
