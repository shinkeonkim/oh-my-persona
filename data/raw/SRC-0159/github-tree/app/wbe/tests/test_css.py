"""CSS 파서, 선택자, 캐스케이드, 값."""

import unittest

from wbe.css.parser import CSSParser, media_matches, parse_keyframes
from wbe.css.selectors import (ClassSelector, IdSelector, ImportantSelector,
                               PseudoclassSelector, TagSelector,
                               cascade_priority, prepare_selectors)
from wbe.css.style import (effective_zoom, force_colors, is_block,
                           is_scrollable, mark_style_dirty, style,
                           style_incremental, z_index, FORCED_COLORS)
from wbe.css.values import (expand_shorthand, parse_aspect_ratio, parse_blur,
                            parse_outline, parse_px, parse_rgb,
                            parse_transform, parse_url_value, parse_zoom,
                            size_from_ratio)
from wbe.dom.nodes import tree_to_list
from wbe.dom.parser import HTMLParser
from wbe.stylesheets import BROWSER_CSS
from wbe.tests.helpers import find_el, styled


class TestValues(unittest.TestCase):
    def test_px(self):
        self.assertEqual(parse_px("12px"), 12)
        self.assertIsNone(parse_px("auto"))
        self.assertIsNone(parse_px("이상함"))

    def test_transform(self):
        self.assertEqual(parse_transform("translate(12px, 30px)"), (12, 30))
        self.assertIsNone(parse_transform("rotate(45deg)"))

    def test_blur(self):
        self.assertEqual(parse_blur("blur(4px)"), 4)
        self.assertEqual(parse_blur("grayscale(50%)"), 0)

    def test_outline(self):
        self.assertEqual(parse_outline("2px solid black"), (2, "black"))
        self.assertEqual(parse_outline("none"), (None, None))

    def test_url_value(self):
        self.assertEqual(parse_url_value("url(cat.png)"), "cat.png")
        self.assertEqual(parse_url_value('url("cat.png")'), "cat.png")

    def test_zoom(self):
        self.assertAlmostEqual(parse_zoom("150%"), 1.5)
        self.assertAlmostEqual(parse_zoom("2"), 2.0)
        self.assertEqual(parse_zoom(None), 1.0)

    def test_aspect_ratio(self):
        self.assertAlmostEqual(parse_aspect_ratio("16 / 9"), 16 / 9)
        self.assertIsNone(parse_aspect_ratio("1 / 0"))

    def test_size_from_ratio(self):
        self.assertEqual(size_from_ratio(200, None, 2.0, 0, 0), (200, 100))
        self.assertEqual(size_from_ratio(None, 100, 2.0, 0, 0), (200, 100))
        self.assertEqual(size_from_ratio(10, 10, 2.0, 0, 0), (10, 10))

    def test_rgb(self):
        self.assertEqual(parse_rgb("red"), (255, 0, 0))

    def test_font_shorthand(self):
        out = expand_shorthand("font", "italic bold 100% Times")
        self.assertEqual(out, {"font-style": "italic", "font-weight": "bold",
                               "font-size": "100%", "font-family": "Times"})

    def test_other_property_untouched(self):
        self.assertEqual(expand_shorthand("color", "red"), {"color": "red"})


class TestSelectors(unittest.TestCase):
    def sel(self, text):
        return CSSParser(text + " { color: red; }").parse()[0][0]

    def test_tag(self):
        tree = styled("<p>글</p>", "p { color: red; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "red")

    def test_class_beats_tag(self):
        tree = styled('<p class="a">글</p>',
                      "p { color: blue; } .a { color: red; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "red")

    def test_id_beats_class(self):
        tree = styled('<p class="a" id="b">글</p>',
                      ".a { color: blue; } #b { color: red; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "red")

    def test_priority_order(self):
        self.assertLess(TagSelector("p").priority, ClassSelector("a").priority)
        self.assertLess(ClassSelector("a").priority, IdSelector("b").priority)

    def test_sequence_sums(self):
        sel = self.sel("span.announce")
        self.assertEqual(sel.priority, 1 + 10)

    def test_sequence_matches(self):
        tree = styled('<span class="a">글</span>',
                      "span.a { color: red; }")
        self.assertEqual(find_el(tree, "span")[0].style["color"], "red")

    def test_descendant(self):
        tree = styled("<div><section><p>글</p></section></div>",
                      "div p { color: red; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "red")

    def test_descendant_order_matters(self):
        tree = styled("<div><section><p>글</p></section></div>",
                      "section div p { color: red; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "black")

    def test_descendant_walks_chain_once(self):
        """O(n+d): 선택자마다 사슬을 처음부터 다시 훑지 않는다."""
        depth = 200
        tree = HTMLParser("<div>" * depth + "<p>글</p>"
                          + "</div>" * depth).parse()
        p = find_el(tree, "p")[0]
        calls = [0]

        class Counting:
            def __init__(self, inner):
                self.inner = inner
                self.priority = inner.priority

            def matches(self, node):
                calls[0] += 1
                return self.inner.matches(node)

        from wbe.css.selectors import DescendantSelector
        sel = DescendantSelector([Counting(TagSelector(t))
                                  for t in ("a", "b", "c", "p")])
        self.assertFalse(sel.matches(p))
        self.assertLessEqual(calls[0], depth + 8)

    def test_has_selector(self):
        tree = styled("<div><p>글</p></div><div><b>글</b></div>",
                      "div:has(p) { color: red; }")
        first, second = find_el(tree, "div")
        self.assertEqual(first.style["color"], "red")
        self.assertEqual(second.style["color"], "black")

    def test_has_prepare_is_linear(self):
        from wbe.css.selectors import HasSelector
        depth = 50
        tree = HTMLParser("<div>" * depth + "<p>글</p>"
                          + "</div>" * depth).parse()
        sel = HasSelector(TagSelector("div"), TagSelector("p"))
        sel.prepare(tree)
        self.assertTrue(all(id(d) in sel.satisfied
                            for d in find_el(tree, "div")))

    def test_important_wins(self):
        tree = styled('<p class="a">글</p>',
                      "p { color: red !important; } .a { color: blue; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "red")

    def test_important_priority(self):
        rules = CSSParser("p { color: red !important; }").parse()
        self.assertIsInstance(rules[0][0], ImportantSelector)

    def test_pseudoclass_focus(self):
        tree = styled('<a href="/x">글</a>')
        a = find_el(tree, "a")[0]
        sel = PseudoclassSelector("focus", TagSelector("a"))
        self.assertFalse(sel.matches(a))
        a.is_focused = True
        self.assertTrue(sel.matches(a))

    def test_pseudoclass_has_class_weight(self):
        """div:hover 가 같은 자리의 div 규칙을 이겨야 한다."""
        sel = self.sel("div:hover")
        self.assertEqual(sel.priority, TagSelector("div").priority + 10)

    def test_focus_visible_is_separate(self):
        tree = styled('<a href="/x">글</a>')
        a = find_el(tree, "a")[0]
        a.is_focused, a.focus_visible = True, False
        self.assertTrue(
            PseudoclassSelector("focus", TagSelector("a")).matches(a))
        self.assertFalse(
            PseudoclassSelector("focus-visible", TagSelector("a")).matches(a))

    def test_hover(self):
        tree = styled("<div>글</div>", "div:hover { color: red; }")
        div = find_el(tree, "div")[0]
        self.assertEqual(div.style["color"], "black")
        div.is_hovered = True
        tree2 = styled("<div>글</div>", "div:hover { color: red; }")
        d2 = find_el(tree2, "div")[0]
        d2.is_hovered = True
        mark_style_dirty(d2)
        rules = CSSParser(BROWSER_CSS).parse()
        rules.extend(CSSParser("div:hover { color: red; }").parse())
        rules.sort(key=cascade_priority)
        style_incremental(tree2, rules)
        self.assertEqual(d2.style["color"], "red")

    def test_selector_list(self):
        tree = styled("<p>가</p><b>나</b>", "p, b { color: red; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "red")
        self.assertEqual(find_el(tree, "b")[0].style["color"], "red")


class TestParserDetails(unittest.TestCase):
    def test_paren_aware_value(self):
        """url(data:image/png;base64,...) 안의 세미콜론은 끝이 아니다."""
        rules = CSSParser(
            "div { background-image: url(data:image/png;base64,AAA); }"
        ).parse()
        self.assertEqual(rules[0][1]["background-image"],
                         "url(data:image/png;base64,AAA)")

    def test_comment_is_skipped(self):
        rules = CSSParser("/* 주석 */ p { color: red; }").parse()
        self.assertEqual(len(rules), 1)

    def test_bad_declaration_is_skipped(self):
        rules = CSSParser("p { 이상함; color: red; }").parse()
        self.assertEqual(rules[0][1], {"color": "red"})

    def test_inline_style_body(self):
        normal, important = CSSParser("color: red; width: 10px").body()
        self.assertEqual(normal, {"color": "red", "width": "10px"})

    def test_media_dark(self):
        light = styled('<a href="/x">글</a>',
                       media={"prefers-color-scheme": "light"})
        dark = styled('<a href="/x">글</a>',
                      media={"prefers-color-scheme": "dark"})
        self.assertEqual(find_el(light, "a")[0].style["color"], "blue")
        self.assertEqual(find_el(dark, "a")[0].style["color"], "lightblue")

    def test_media_max_width(self):
        css = "@media (max-width: 400px) { p { color: red; } }"
        wide = styled("<p>글</p>", css, {"width": 900})
        narrow = styled("<p>글</p>", css, {"width": 300})
        self.assertEqual(find_el(wide, "p")[0].style["color"], "black")
        self.assertEqual(find_el(narrow, "p")[0].style["color"], "red")

    def test_media_forced_colors(self):
        self.assertTrue(media_matches("forced-colors", "active",
                                      {"forced-colors": True}))

    def test_media_exact_width(self):
        self.assertTrue(media_matches("width", "400px", {"width": 400}))

    def test_keyframes(self):
        out = parse_keyframes(
            "@keyframes fade { from { opacity: 1; } to { opacity: 0; } }")
        self.assertEqual(out["fade"][0.0]["opacity"], "1")
        self.assertEqual(out["fade"][1.0]["opacity"], "0")

    def test_keyframes_percent(self):
        out = parse_keyframes(
            "@keyframes s { 0% { opacity: 1; } 100% { opacity: 0; } }")
        self.assertIn(0.0, out["s"])

    def test_keyframes_do_not_become_rules(self):
        rules = CSSParser(
            "@keyframes f { from { opacity: 1; } to { opacity: 0; } }"
            "p { color: red; }").parse()
        self.assertEqual(len(rules), 1)


class TestComputed(unittest.TestCase):
    def test_display_from_stylesheet(self):
        tree = styled("<div>글</div>")
        self.assertTrue(is_block(find_el(tree, "div")[0]))

    def test_span_is_inline(self):
        tree = styled("<span>글</span>")
        self.assertFalse(is_block(find_el(tree, "span")[0]))

    def test_display_can_be_overridden(self):
        tree = styled("<span>글</span>", "span { display: block; }")
        self.assertTrue(is_block(find_el(tree, "span")[0]))

    def test_inheritance(self):
        tree = styled("<div><p>글</p></div>", "div { color: red; }")
        self.assertEqual(find_el(tree, "p")[0].style["color"], "red")

    def test_font_family_inherited(self):
        tree = styled("<div><p>글</p></div>", "div { font-family: Courier; }")
        self.assertEqual(find_el(tree, "p")[0].style["font-family"], "Courier")

    def test_percent_font_size(self):
        tree = styled("<div><small>글</small></div>",
                      "div { font-size: 20px; }")
        self.assertEqual(find_el(tree, "small")[0].style["font-size"], "18.0px")

    def test_z_index_needs_position(self):
        tree = styled("<div>글</div>", "div { z-index: 5; }")
        self.assertEqual(z_index(find_el(tree, "div")[0]), 0)
        tree = styled("<div>글</div>",
                      "div { position: relative; z-index: 5; }")
        self.assertEqual(z_index(find_el(tree, "div")[0]), 5)

    def test_scrollable_needs_height(self):
        tree = styled("<div>글</div>", "div { overflow: scroll; }")
        self.assertFalse(is_scrollable(find_el(tree, "div")[0]))
        tree = styled("<div>글</div>",
                      "div { overflow: scroll; height: 50px; }")
        self.assertTrue(is_scrollable(find_el(tree, "div")[0]))

    def test_zoom_multiplies(self):
        tree = styled('<div style="zoom: 2"><div style="zoom: 2">'
                      "<p>글</p></div></div>")
        self.assertAlmostEqual(effective_zoom(find_el(tree, "p")[0]), 4.0)

    def test_forced_colors(self):
        tree = styled('<p style="color: #777777">글</p>')
        force_colors(tree_to_list(tree))
        self.assertEqual(find_el(tree, "p")[0].style["color"],
                         FORCED_COLORS["color"])

    def test_forced_colors_keeps_links_distinct(self):
        tree = styled('<a href="/x">글</a>')
        force_colors(tree_to_list(tree))
        self.assertEqual(find_el(tree, "a")[0].style["color"],
                         FORCED_COLORS["link"])


class TestIncrementalStyle(unittest.TestCase):
    HTML = "<div><p>가</p><p>나</p></div><section><p>다</p></section>"

    def rules(self):
        rules = CSSParser(BROWSER_CSS).parse()
        rules.sort(key=cascade_priority)
        return rules

    def fresh(self):
        tree = HTMLParser(self.HTML).parse()
        rules = self.rules()
        prepare_selectors(rules, tree)
        style(tree, rules)
        return tree, rules

    def test_first_pass_visits_everything(self):
        tree = HTMLParser(self.HTML).parse()
        rules = self.rules()
        visited = style(tree, rules)
        self.assertEqual(len(visited), len(tree_to_list(tree)))

    def test_clean_tree_visits_nothing(self):
        tree, rules = self.fresh()
        self.assertEqual(style_incremental(tree, rules), [])

    def test_only_dirty_branch_visited(self):
        tree, rules = self.fresh()
        section = find_el(tree, "section")[0]
        mark_style_dirty(section)
        visited = style_incremental(tree, rules)
        self.assertIn(section, visited)
        self.assertLess(len(visited), len(tree_to_list(tree)))

    def test_dirty_parent_restyles_children(self):
        """상속 때문에 부모가 바뀌면 자식도 다시 봐야 한다."""
        tree, rules = self.fresh()
        div = find_el(tree, "div")[0]
        mark_style_dirty(div)
        visited = style_incremental(tree, rules)
        for child in div.children:
            self.assertIn(child, visited)

    def test_ancestors_are_flagged(self):
        tree, rules = self.fresh()
        mark_style_dirty(find_el(tree, "section")[0])
        self.assertTrue(tree.has_dirty_style_descendants)


if __name__ == "__main__":
    unittest.main(verbosity=2)
