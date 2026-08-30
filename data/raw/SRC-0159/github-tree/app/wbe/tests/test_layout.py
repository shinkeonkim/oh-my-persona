"""배치 — 상자, 줄, 낱말, 끼워 넣는 것들."""

import unittest

from wbe.layout.boxes import (BlockLayout, DocumentLayout, LineLayout,
                              TextLayout, TOC_LABEL, group_children)
from wbe.layout.embed import (ButtonLayout, CanvasLayout, IframeLayout,
                              ImageLayout, InputLayout, CHECKBOX_SIZE,
                              IFRAME_HEIGHT_PX, IFRAME_WIDTH_PX,
                              INPUT_WIDTH_PX, IMAGE_PLACEHOLDER_COLOR,
                              PASSWORD_CHAR, display_value, is_hidden,
                              is_lazy, object_fit_rect, placeholder_size,
                              should_hide_broken)
from wbe.layout.fonts import SOFT_HYPHEN, get_font
from wbe.layout.invalidation import (DependencyError, FieldStore,
                                     ProtectedField, reconcile_children)
from wbe.dom.nodes import Element
from wbe.paint.commands import DrawRect, DrawText
from wbe.paint.geometry import Rect
from wbe.tests.helpers import build, find_el, layouts, of_type, styled, texts


class TestFonts(unittest.TestCase):
    def test_measure_and_metrics(self):
        font = get_font(16)
        self.assertGreater(font.measure("hello"), 0)
        m = font.metrics()
        self.assertAlmostEqual(m["linespace"], m["ascent"] + m["descent"],
                               places=3)

    def test_cache_separates_families(self):
        self.assertIsNot(get_font(16), get_font(16, family="monospace"))

    def test_named_metric(self):
        self.assertEqual(get_font(16).metrics("ascent"),
                         get_font(16).metrics()["ascent"])


class TestTextLayout(unittest.TestCase):
    def test_words_are_placed(self):
        _, cmds = build("<p>하나 둘 셋</p>")
        self.assertEqual(texts(cmds), ["하나", "둘", "셋"])

    def test_long_line_wraps(self):
        _, cmds = build("<p>" + "낱말 " * 60 + "</p>")
        tops = {c.rect.top for c in of_type(cmds, DrawText)}
        self.assertGreater(len(tops), 1)

    def test_bold_and_italic(self):
        _, cmds = build("<p><b>굵게</b> <i>기울임</i></p>")
        by = {c.text: c.font for c in of_type(cmds, DrawText)}
        self.assertEqual(by["굵게"].cget("weight"), "bold")
        self.assertEqual(by["기울임"].cget("slant"), "italic")

    def test_centered_title(self):
        _, cmds = build('<h1 class="title">가운데</h1>')
        left = of_type(cmds, DrawText)[0].rect.left
        self.assertGreater(left, 30)

    def test_superscript_is_smaller_and_top_aligned(self):
        _, cmds = build("<p>보통 <sup>위</sup></p>")
        by = {c.text: c for c in of_type(cmds, DrawText)}
        self.assertLess(by["위"].font.metrics("linespace"),
                        by["보통"].font.metrics("linespace"))
        self.assertLessEqual(by["위"].rect.top, by["보통"].rect.top + 1)

    def test_smallcaps(self):
        _, cmds = build("<abbr>abc</abbr>")
        self.assertIn("ABC", "".join(texts(cmds)))

    def test_pre_preserves_spaces(self):
        _, cmds = build("<pre>a    b</pre>")
        self.assertIn("a    b", texts(cmds))

    def test_pre_is_monospace(self):
        _, cmds = build("<pre>x</pre>")
        self.assertEqual(of_type(cmds, DrawText)[0].font.cget("family"),
                         "Courier New")

    def test_soft_hyphen_breaks(self):
        """줄에 안 들어가면 소프트 하이픈 자리에서 끊고 '-' 를 붙인다."""
        word = SOFT_HYPHEN.join(["아주"] * 120)
        _, cmds = build("<p>" + word + "</p>")
        self.assertTrue(any(t.endswith("-") for t in texts(cmds)))

    def test_soft_hyphen_is_invisible_when_it_fits(self):
        word = SOFT_HYPHEN.join(["가", "나"])
        _, cmds = build("<p>" + word + "</p>")
        self.assertEqual(texts(cmds), ["가나"])

    def test_br_breaks_the_line(self):
        _, cmds = build("<p>가<br>나</p>")
        by = {c.text: c.rect.top for c in of_type(cmds, DrawText)}
        self.assertLess(by["가"], by["나"])


class TestBlockLayout(unittest.TestCase):
    def test_anonymous_box_groups_inlines(self):
        tree = styled("<div><i>가</i><b>나</b><p>다</p></div>")
        div = find_el(tree, "div")[0]
        groups = group_children(div)
        self.assertEqual(len(groups), 2)
        self.assertEqual(len(groups[0]), 2)

    def test_inlines_share_a_line(self):
        _, cmds = build("<div><i>가</i><b>나</b><p>다</p></div>")
        by = {c.text: c.rect.top for c in of_type(cmds, DrawText)}
        self.assertEqual(by["가"], by["나"])
        self.assertGreater(by["다"], by["가"])

    def test_run_in_heading(self):
        _, cmds = build("<div><h6>제목.</h6><p>이어지는 본문</p></div>")
        by = {c.text: c.rect.top for c in of_type(cmds, DrawText)}
        self.assertEqual(by["제목."], by["이어지는"])

    def test_other_headings_break(self):
        _, cmds = build("<div><h2>제목</h2><p>본문</p></div>")
        by = {c.text: c.rect.top for c in of_type(cmds, DrawText)}
        self.assertLess(by["제목"], by["본문"])

    def test_head_is_not_laid_out(self):
        _, cmds = build("<head><title>제목</title></head><body>본문</body>")
        self.assertNotIn("제목", texts(cmds))
        self.assertIn("본문", texts(cmds))

    def test_bullets(self):
        _, cmds = build("<ul><li>하나</li><li>둘</li></ul>")
        self.assertEqual(len([c for c in of_type(cmds, DrawRect)
                              if c.color == "black"]), 2)

    def test_list_is_indented(self):
        doc, _ = build("<ul><li>하나</li></ul>")
        li = next(o for o in layouts(doc, BlockLayout) if o.element("li"))
        ul = next(o for o in layouts(doc, BlockLayout) if o.element("ul"))
        self.assertGreater(li.x, ul.x)

    def test_toc_label(self):
        _, cmds = build('<nav id="toc"><ul><li>1장</li></ul></nav>')
        self.assertIn(TOC_LABEL, texts(cmds))

    def test_toc_label_does_not_overlap(self):
        _, cmds = build('<nav id="toc"><ul><li>1장</li></ul></nav>')
        by = {c.text: c for c in of_type(cmds, DrawText)}
        self.assertGreaterEqual(by["1장"].rect.top,
                                by[TOC_LABEL].rect.bottom - 1)

    def test_links_bar(self):
        from wbe.layout.boxes import LINKS_BAR_COLOR
        _, cmds = build('<nav class="links">이전 다음</nav>')
        self.assertEqual(len([c for c in of_type(cmds, DrawRect)
                              if c.color == LINKS_BAR_COLOR]), 1)

    def test_width_and_height(self):
        doc, _ = build("<div>글</div>",
                       "div { width: 120px; height: 60px; }")
        div = next(o for o in layouts(doc, BlockLayout) if o.element("div"))
        self.assertEqual((div.width, div.height), (120, 60))

    def test_auto_width_fills_parent(self):
        doc, _ = build("<div>글</div>", "div { width: auto; }")
        div = next(o for o in layouts(doc, BlockLayout) if o.element("div"))
        html = next(o for o in layouts(doc, BlockLayout) if o.element("html"))
        self.assertEqual(div.width, html.width)

    def test_display_inline_joins_paragraphs(self):
        _, cmds = build("<div><p>가</p><p>나</p></div>",
                        "p { display: inline; }")
        by = {c.text: c.rect.top for c in of_type(cmds, DrawText)}
        self.assertEqual(by["가"], by["나"])


class TestEmbeds(unittest.TestCase):
    def test_input_size(self):
        doc, _ = build('<input name="a" value="x">')
        box = layouts(doc, InputLayout)[0]
        self.assertEqual(box.width, INPUT_WIDTH_PX)

    def test_checkbox_is_square(self):
        doc, _ = build('<input name="a" type="checkbox">')
        box = layouts(doc, InputLayout)[0]
        self.assertEqual((box.width, box.height),
                         (CHECKBOX_SIZE, CHECKBOX_SIZE))

    def test_checked_box_is_filled(self):
        doc, cmds = build('<input name="a" type="checkbox" checked>')
        self.assertTrue([c for c in of_type(cmds, DrawRect)
                         if c.color == "black"])

    def test_hidden_input_takes_no_space(self):
        doc, cmds = build('<input name="a" type="hidden" value="v">')
        box = layouts(doc, InputLayout)[0]
        self.assertEqual((box.width, box.height), (0, 0))
        self.assertEqual(texts(cmds), [])

    def test_password_shows_stars(self):
        node = Element("input", {"type": "password", "value": "abc"}, None)
        self.assertEqual(display_value(node), PASSWORD_CHAR * 3)
        _, cmds = build('<input name="p" type="password" value="abc">')
        self.assertIn("***", texts(cmds))
        self.assertNotIn("abc", texts(cmds))

    def test_button_lays_out_children(self):
        doc, cmds = build("<button><b>굵게</b> 그리고</button>")
        btn = layouts(doc, ButtonLayout)[0]
        self.assertGreater(btn.height, 0)
        for word in ("굵게", "그리고"):
            self.assertIn(word, texts(cmds))

    def test_button_children_stay_inside(self):
        doc, cmds = build("<button>" + "긴 내용 " * 30 + "</button>")
        btn = layouts(doc, ButtonLayout)[0]
        for cmd in of_type(cmds, DrawText):
            self.assertGreaterEqual(cmd.rect.left, btn.x - 1)
            self.assertLessEqual(cmd.rect.right, btn.x + btn.width + 1)
            self.assertLessEqual(cmd.rect.bottom, btn.y + btn.height + 1)

    def test_canvas_default_size(self):
        doc, _ = build("<canvas></canvas>")
        box = layouts(doc, CanvasLayout)[0]
        self.assertEqual((box.width, box.height), (300, 150))

    def test_canvas_attributes(self):
        doc, _ = build('<canvas width="100" height="50"></canvas>')
        box = layouts(doc, CanvasLayout)[0]
        self.assertEqual((box.width, box.height), (100, 50))

    def test_iframe_default_size(self):
        doc, _ = build('<iframe src="x"></iframe>')
        box = layouts(doc, IframeLayout)[0]
        self.assertEqual((box.width, box.height),
                         (IFRAME_WIDTH_PX, IFRAME_HEIGHT_PX))

    def test_iframe_aspect_ratio(self):
        doc, _ = build('<iframe src="x" width="200" '
                       'style="aspect-ratio: 2"></iframe>')
        box = layouts(doc, IframeLayout)[0]
        self.assertEqual((box.width, box.height), (200, 100))

    def test_lazy_image_is_not_loaded(self):
        tree = styled('<img src="x.png" loading="lazy">')
        self.assertTrue(is_lazy(find_el(tree, "img")[0]))

    def test_placeholder_without_size(self):
        tree = styled('<img src="x.png" loading="lazy">')
        self.assertEqual(placeholder_size(find_el(tree, "img")[0]), (0, 0))

    def test_placeholder_with_size(self):
        tree = styled('<img src="x.png" loading="lazy" '
                      'width="60" height="40">')
        self.assertEqual(placeholder_size(find_el(tree, "img")[0]), (60, 40))

    def test_broken_image_without_alt_hidden(self):
        tree = styled('<img src="없는.png">')
        self.assertTrue(should_hide_broken(find_el(tree, "img")[0]))
        _, cmds = build('<img src="없는.png" width="50" height="50">')
        self.assertEqual([c for c in of_type(cmds, DrawRect)
                          if c.color == IMAGE_PLACEHOLDER_COLOR], [])

    def test_broken_image_with_alt_shown(self):
        _, cmds = build('<img src="없는.png" alt="고양이" '
                        'width="80" height="50">')
        self.assertTrue([c for c in of_type(cmds, DrawRect)
                         if c.color == IMAGE_PLACEHOLDER_COLOR])
        self.assertIn("고양이", texts(cmds))


class TestObjectFit(unittest.TestCase):
    BOX = Rect(0, 0, 100, 100)

    def test_fill_stretches(self):
        out = object_fit_rect(self.BOX, 20, 10, "fill")
        self.assertEqual((out.width, out.height), (100, 100))

    def test_contain_keeps_ratio_inside(self):
        out = object_fit_rect(self.BOX, 20, 10, "contain")
        self.assertAlmostEqual(out.width / out.height, 2.0)
        self.assertLessEqual(out.width, 100)

    def test_cover_fills_the_box(self):
        out = object_fit_rect(self.BOX, 20, 10, "cover")
        self.assertGreaterEqual(out.width, 100)
        self.assertGreaterEqual(out.height, 100)

    def test_none_keeps_natural_size(self):
        out = object_fit_rect(self.BOX, 20, 10, "none")
        self.assertEqual((out.width, out.height), (20, 10))

    def test_scale_down_never_grows(self):
        out = object_fit_rect(self.BOX, 20, 10, "scale-down")
        self.assertEqual((out.width, out.height), (20, 10))


class TestInvalidation(unittest.TestCase):
    class Owner:
        def __init__(self, parent=None):
            self.parent = parent
            self.has_dirty_descendants = False

    def test_new_field_is_dirty(self):
        self.assertTrue(ProtectedField(self.Owner(), "x").dirty)

    def test_reading_dirty_raises(self):
        with self.assertRaises(DependencyError):
            ProtectedField(self.Owner(), "x").get()

    def test_reader_is_invalidated(self):
        a = ProtectedField(self.Owner(), "a")
        b = ProtectedField(self.Owner(), "b")
        a.set(1)
        b.set(a.read(notify=b) + 1)
        a.set(2)
        self.assertTrue(b.dirty)

    def test_same_value_does_not_invalidate(self):
        a = ProtectedField(self.Owner(), "a")
        b = ProtectedField(self.Owner(), "b")
        a.set(1)
        b.set(a.read(notify=b))
        a.set(1)
        self.assertFalse(b.dirty)

    def test_frozen_dependencies_checked(self):
        a = ProtectedField(self.Owner(), "a")
        a.set(1)
        b = ProtectedField(self.Owner(), "b", dependencies=[])
        with self.assertRaises(DependencyError):
            a.read(notify=b)

    def test_ancestor_flags(self):
        root = self.Owner()
        child = self.Owner(root)
        field = ProtectedField(child, "x", parent=child)
        field.set(1)
        field.mark()
        self.assertTrue(child.has_dirty_descendants)

    def test_store_has_no_dict(self):
        self.assertFalse(hasattr(FieldStore(), "__dict__"))

    def test_store_never_makes_field_objects(self):
        store = FieldStore()
        for i in range(100):
            store.set("f%d" % i, i)
        self.assertEqual(store.field_count(), 0)

    def test_store_same_semantics(self):
        a = ProtectedField(self.Owner(), "a")
        b = ProtectedField(self.Owner(), "b")
        a.set(1)
        b.set(a.read(notify=b))
        a.set(2)

        sa, sb = FieldStore(), FieldStore()
        sa.set("a", 1)
        sb.set("b", sa.read("a", notify=(sb, "b")))
        sa.set("a", 2)
        self.assertEqual(b.dirty, sb.is_dirty("b"))


class TestReconcile(unittest.TestCase):
    class Fake:
        def __init__(self, node, previous):
            self.node = node
            self.previous = previous

    def make(self, node, previous):
        return self.Fake(node, previous)

    def test_append_reuses_and_touches_one(self):
        nodes = [Element("p", {}, None) for _ in range(5)]
        old, _ = reconcile_children([], nodes, self.make)
        extra = Element("b", {}, None)
        new, changed = reconcile_children(old, nodes + [extra], self.make)
        self.assertEqual(len(changed), 1)
        self.assertIs(new[0], old[0])

    def test_prepend_touches_two(self):
        nodes = [Element("p", {}, None) for _ in range(5)]
        old, _ = reconcile_children([], nodes, self.make)
        extra = Element("b", {}, None)
        _, changed = reconcile_children(old, [extra] + nodes, self.make)
        self.assertEqual(len(changed), 2)

    def test_unchanged_list_changes_nothing(self):
        nodes = [Element("p", {}, None), Element("b", {}, None)]
        old, _ = reconcile_children([], nodes, self.make)
        new, changed = reconcile_children(old, nodes, self.make)
        self.assertEqual(changed, [])
        self.assertEqual(new, old)

    def test_previous_is_updated(self):
        a, b = Element("p", {}, None), Element("b", {}, None)
        old, _ = reconcile_children([], [a], self.make)
        new, _ = reconcile_children(old, [b, a], self.make)
        self.assertIs(new[1].previous, new[0])
        self.assertIsNone(new[0].previous)


if __name__ == "__main__":
    unittest.main(verbosity=2)
