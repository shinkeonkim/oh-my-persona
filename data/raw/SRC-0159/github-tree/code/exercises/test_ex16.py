"""16장 연습문제 검증.

    python3 test_ex16.py

무효화는 "얼마나 적게 다시 하는가"가 핵심이므로, 다시 계산한 노드 수를 세어
확인한다.
"""

import unittest
import urllib.parse

import ex11
import ex13
import ex14
import ex15
import ex16
from ex16 import (ProtectedField, FieldStore, DependencyError, Tab, Frame16,
                  JSContext, reconcile_children, mark_style_dirty,
                  style_incremental, mark_paint_dirty, paint_tree_cached,
                  clear_style_flags)
from ex15 import DocumentLayout, BlockLayout
from ex14 import CSSParser
from ex11 import DrawText, DrawRect, Rect, flatten, WIDTH, HEIGHT
from ex10 import URL, Element, Text, tree_to_list, cascade_priority


def doc_url(html):
    return "data:text/html," + urllib.parse.quote(html)


def make_tab(html):
    tab = Tab(None, 500)
    tab.load(URL(doc_url(html)))
    return tab


def styled(html, css=""):
    tree = ex15.HTMLParser(html).parse()
    for node in tree_to_list(tree, []):
        if isinstance(node, Element):
            node.is_focused = node.is_hovered = node.focus_visible = False
    rules = CSSParser(ex15.BROWSER_CSS_15).parse()
    if css:
        rules.extend(CSSParser(css).parse())
    ex13.style(tree, sorted(rules, key=cascade_priority), None, None)
    return tree


def build(html, css=""):
    doc = DocumentLayout(styled(html, css))
    doc.layout()
    cmds = []
    ex13.paint_tree(doc, cmds)
    return doc, cmds


def find_el(node, tag, out=None):
    out = [] if out is None else out
    if isinstance(node, Element):
        if node.tag == tag:
            out.append(node)
        for c in node.children:
            find_el(c, tag, out)
    return out


def by_id(nodes, name):
    return next(n for n in tree_to_list(nodes, [])
                if isinstance(n, Element)
                and n.attributes.get("id") == name)


def drawn(tab):
    return [c.text for c in tab.flat_display_list if hasattr(c, "text")]


class Owner:
    """보호 필드를 매달아 둘 최소한의 주인."""

    def __init__(self, parent=None):
        self.parent = parent
        self.has_dirty_descendants = False


class ChapterSixteenBasics(unittest.TestCase):
    """16장 본문 — ProtectedField 와 의존성"""

    def test_new_field_is_dirty(self):
        field = ProtectedField(Owner(), "x")
        self.assertTrue(field.dirty)

    def test_reading_a_dirty_field_raises(self):
        with self.assertRaises(DependencyError):
            ProtectedField(Owner(), "x").get()

    def test_set_makes_it_clean(self):
        field = ProtectedField(Owner(), "x")
        field.set(5)
        self.assertFalse(field.dirty)
        self.assertEqual(field.get(), 5)

    def test_reader_is_invalidated(self):
        a = ProtectedField(Owner(), "a")
        b = ProtectedField(Owner(), "b")
        a.set(1)
        b.set(a.read(notify=b) + 1)
        a.set(2)
        self.assertTrue(b.dirty)

    def test_same_value_does_not_invalidate(self):
        a = ProtectedField(Owner(), "a")
        b = ProtectedField(Owner(), "b")
        a.set(1)
        b.set(a.read(notify=b))
        a.set(1)
        self.assertFalse(b.dirty)

    def test_frozen_dependencies_are_checked(self):
        a = ProtectedField(Owner(), "a")
        a.set(1)
        b = ProtectedField(Owner(), "b", dependencies=[])
        with self.assertRaises(DependencyError):
            a.read(notify=b)

    def test_declared_dependency_is_allowed(self):
        a = ProtectedField(Owner(), "a")
        a.set(1)
        b = ProtectedField(Owner(), "b", dependencies=[a])
        self.assertEqual(a.read(notify=b), 1)

    def test_copy_tracks_the_dependency(self):
        a = ProtectedField(Owner(), "a")
        b = ProtectedField(Owner(), "b")
        a.set(1)
        b.copy(a)
        a.set(2)
        self.assertTrue(b.dirty)


class Exercise161(unittest.TestCase):
    """16-1 요소 비우기"""

    HTML = '<div id="d"><p>가</p><b>나</b></div><p id="e">다</p>'

    def test_children_are_removed(self):
        tab = make_tab(self.HTML)
        tab.root_frame.js.interp.evaljs("d.replaceChildren();0;")
        self.assertEqual(by_id(tab.root_frame.nodes, "d").children, [])

    def test_content_is_no_longer_drawn(self):
        tab = make_tab(self.HTML)
        tab.root_frame.js.interp.evaljs("d.replaceChildren();0;")
        tab.render()
        self.assertNotIn("가", drawn(tab))
        self.assertIn("다", drawn(tab))

    def test_it_returns_undefined(self):
        tab = make_tab(self.HTML)
        self.assertIsNone(
            tab.root_frame.js.interp.evaljs("d.replaceChildren()"))

    def test_only_the_touched_subtree_restyles(self):
        tab = make_tab(self.HTML)
        tab.root_frame.js.interp.evaljs("d.replaceChildren();0;")
        touched = len(tab.root_frame.style_stats)
        total = len(tree_to_list(tab.root_frame.nodes, []))
        self.assertLess(touched, total, "문서 전체를 다시 훑으면 안 됩니다")

    def test_emptying_twice_is_safe(self):
        tab = make_tab(self.HTML)
        tab.root_frame.js.interp.evaljs("d.replaceChildren();0;")
        tab.root_frame.js.interp.evaljs("d.replaceChildren();0;")
        self.assertEqual(by_id(tab.root_frame.nodes, "d").children, [])

    def test_removed_iframe_is_unloaded(self):
        inner = doc_url("<p>안쪽</p>").replace('"', "%22")
        tab = make_tab('<div id="d"><iframe src="%s"></iframe></div>' % inner)
        self.assertEqual(len(tab.frames()), 2)
        tab.root_frame.js.interp.evaljs("d.replaceChildren();0;")
        self.assertEqual(len(tab.frames()), 1)


class Exercise162(unittest.TestCase):
    """16-2 레이아웃 단계 보호하기"""

    def test_document_field_starts_dirty(self):
        owner = Owner()
        field = ProtectedField(owner, "document")
        self.assertTrue(field.dirty)

    def test_layout_marks_it_clean(self):
        owner = Owner()
        field = ProtectedField(owner, "document")
        field.set("배치 결과")
        self.assertFalse(field.dirty)

    def test_style_change_dirties_layout(self):
        owner = Owner()
        style = ProtectedField(owner, "style")
        document = ProtectedField(owner, "document")
        style.set({"width": "100px"})
        document.set(style.read(notify=document))
        style.set({"width": "200px"})
        self.assertTrue(document.dirty, "스타일이 바뀌면 배치도 다시")

    def test_opacity_animation_does_not_dirty_layout(self):
        """opacity 는 그리기만 다시 하면 됩니다."""
        tree = styled("<div>글</div>", "div { opacity: 1; }")
        div = find_el(tree, "div")[0]
        anim = ex13.NumericAnimation(1, 0, 10)
        div.animations = {"opacity": anim}
        self.assertFalse(anim.needs_layout)

    def test_width_animation_does_dirty_layout(self):
        anim = ex13.PxAnimation("0px", "10px", 10)
        self.assertTrue(anim.needs_layout)

    def test_ancestor_flags_are_set(self):
        root = Owner()
        child = Owner(root)
        field = ProtectedField(child, "x", parent=child)
        field.set(1)
        field.mark()
        self.assertTrue(child.has_dirty_descendants)


class Exercise163(unittest.TestCase):
    """16-3 자식 옮기기"""

    HTML = '<div id="a"><p id="p">글</p></div><div id="b"></div>'

    def test_child_moves_to_the_new_parent(self):
        tab = make_tab(self.HTML)
        tab.root_frame.js.interp.evaljs("b.replaceChildren(p);0;")
        self.assertEqual(by_id(tab.root_frame.nodes, "b").children,
                         [by_id(tab.root_frame.nodes, "p")])

    def test_old_parent_loses_it(self):
        tab = make_tab(self.HTML)
        tab.root_frame.js.interp.evaljs("b.replaceChildren(p);0;")
        self.assertEqual(by_id(tab.root_frame.nodes, "a").children, [])

    def test_parent_pointer_is_updated(self):
        tab = make_tab(self.HTML)
        tab.root_frame.js.interp.evaljs("b.replaceChildren(p);0;")
        node = by_id(tab.root_frame.nodes, "p")
        self.assertIs(node.parent, by_id(tab.root_frame.nodes, "b"))

    def test_content_is_still_drawn(self):
        tab = make_tab(self.HTML)
        tab.root_frame.js.interp.evaljs("b.replaceChildren(p);0;")
        tab.render()
        self.assertIn("글", drawn(tab))

    def test_order_follows_the_arguments(self):
        tab = make_tab('<div id="a"><p id="p">가</p><b id="q">나</b></div>'
                       '<div id="b"></div>')
        tab.root_frame.js.interp.evaljs("b.replaceChildren(q, p);0;")
        tags = [c.tag for c in by_id(tab.root_frame.nodes, "b").children]
        self.assertEqual(tags, ["b", "p"])

    def test_existing_children_are_replaced(self):
        tab = make_tab('<div id="a"><p id="p">가</p></div>'
                       '<div id="b"><i>버려질 것</i></div>')
        tab.root_frame.js.interp.evaljs("b.replaceChildren(p);0;")
        tab.render()
        self.assertNotIn("버려질", drawn(tab))


class Exercise164(unittest.TestCase):
    """16-4 style 을 위한 자손 플래그"""

    HTML = "<div><p>가</p><p>나</p></div>" + "<section><p>다</p></section>"

    def rules(self):
        return sorted(CSSParser(ex15.BROWSER_CSS_15).parse(),
                      key=cascade_priority)

    def test_first_pass_visits_everything(self):
        tree = ex15.HTMLParser(self.HTML).parse()
        for node in tree_to_list(tree, []):
            mark_style_dirty(node)
        visited = style_incremental(tree, self.rules())
        self.assertEqual(len(visited), len(tree_to_list(tree, [])))

    def test_clean_tree_visits_nothing(self):
        tree = ex15.HTMLParser(self.HTML).parse()
        for node in tree_to_list(tree, []):
            mark_style_dirty(node)
        style_incremental(tree, self.rules())
        self.assertEqual(style_incremental(tree, self.rules()), [])

    def test_dirty_leaf_marks_its_ancestors(self):
        tree = ex15.HTMLParser(self.HTML).parse()
        for node in tree_to_list(tree, []):
            mark_style_dirty(node)
        style_incremental(tree, self.rules())
        leaf = find_el(tree, "section")[0]
        mark_style_dirty(leaf)
        self.assertTrue(tree.has_dirty_style_descendants)

    def test_only_the_dirty_branch_is_visited(self):
        tree = ex15.HTMLParser(self.HTML).parse()
        for node in tree_to_list(tree, []):
            mark_style_dirty(node)
        style_incremental(tree, self.rules())
        section = find_el(tree, "section")[0]
        mark_style_dirty(section)
        visited = style_incremental(tree, self.rules())
        self.assertLess(len(visited), len(tree_to_list(tree, [])))
        self.assertIn(section, visited)

    def test_restyling_a_parent_restyles_its_children(self):
        """상속 때문에 부모가 바뀌면 자식도 다시 봐야 합니다."""
        tree = ex15.HTMLParser(self.HTML).parse()
        for node in tree_to_list(tree, []):
            mark_style_dirty(node)
        style_incremental(tree, self.rules())
        div = find_el(tree, "div")[0]
        mark_style_dirty(div)
        visited = style_incremental(tree, self.rules())
        for child in div.children:
            self.assertIn(child, visited)

    def test_tab_uses_the_incremental_pass(self):
        tab = make_tab('<div id="d"><p>가</p></div><p>나</p>')
        tab.root_frame.restyle()
        self.assertEqual(tab.root_frame.style_stats, [])


class Exercise165(unittest.TestCase):
    """16-5 브라우저 크기 조절"""

    def test_resize_changes_the_frame_width(self):
        tab = make_tab("<p>글</p>")
        tab.resize(400, 300)
        self.assertEqual(tab.root_frame.width, 400)

    def test_narrower_window_wraps_more(self):
        tab = make_tab("<p>" + "낱말 " * 60 + "</p>")
        wide_lines = len({c.rect.top for c in tab.flat_display_list
                          if hasattr(c, "text")})
        tab.resize(300, 500)
        narrow_lines = len({c.rect.top for c in tab.flat_display_list
                            if hasattr(c, "text")})
        self.assertGreater(narrow_lines, wide_lines)

    def test_resize_triggers_media_queries(self):
        tab = make_tab("<style>@media (max-width: 400px) "
                       "{ p { color: red; } }</style><p>글</p>")
        self.assertEqual(find_el(tab.root_frame.nodes, "p")[0].style["color"],
                         "black")
        tab.resize(300, 500)
        self.assertEqual(find_el(tab.root_frame.nodes, "p")[0].style["color"],
                         "red")

    def test_resize_keeps_the_content(self):
        tab = make_tab("<p>그대로</p>")
        tab.resize(400, 300)
        self.assertIn("그대로", drawn(tab))

    def test_height_is_recorded(self):
        tab = make_tab("<p>글</p>")
        tab.resize(400, 300)
        self.assertEqual(tab.tab_height, 300)


class Exercise166(unittest.TestCase):
    """16-6 자식 매칭하기"""

    class FakeLayout:
        def __init__(self, node, previous):
            self.node = node
            self.previous = previous

    def make(self, node, previous):
        return self.FakeLayout(node, previous)

    def test_appending_reuses_the_old_children(self):
        a, b = Element("p", {}, None), Element("b", {}, None)
        old, _ = reconcile_children([], [a], self.make)
        new, changed = reconcile_children(old, [a, b], self.make)
        self.assertIs(new[0], old[0], "이미 있던 것은 다시 만들지 않습니다")
        self.assertEqual(len(changed), 1)

    def test_new_child_is_created(self):
        a, b = Element("p", {}, None), Element("b", {}, None)
        old, _ = reconcile_children([], [a], self.make)
        new, changed = reconcile_children(old, [a, b], self.make)
        self.assertIs(changed[0], new[1])

    def test_removing_a_child_drops_it(self):
        a, b = Element("p", {}, None), Element("b", {}, None)
        old, _ = reconcile_children([], [a, b], self.make)
        new, _ = reconcile_children(old, [a], self.make)
        self.assertEqual(len(new), 1)
        self.assertIs(new[0], old[0])

    def test_unchanged_list_changes_nothing(self):
        a, b = Element("p", {}, None), Element("b", {}, None)
        old, _ = reconcile_children([], [a, b], self.make)
        new, changed = reconcile_children(old, [a, b], self.make)
        self.assertEqual(changed, [])
        self.assertEqual(new, old)

    def test_appending_at_the_end_touches_one_child(self):
        nodes = [Element("p", {}, None) for _ in range(5)]
        old, _ = reconcile_children([], nodes, self.make)
        extra = Element("b", {}, None)
        _, changed = reconcile_children(old, nodes + [extra], self.make)
        self.assertEqual(len(changed), 1, "뒤에 붙이면 하나만 손댑니다")


class Exercise167(unittest.TestCase):
    """16-7 previous 무효화"""

    class FakeLayout:
        def __init__(self, node, previous):
            self.node = node
            self.previous = previous

    def make(self, node, previous):
        return self.FakeLayout(node, previous)

    def test_insert_at_the_front_updates_previous(self):
        a, b = Element("p", {}, None), Element("b", {}, None)
        old, _ = reconcile_children([], [a], self.make)
        new, changed = reconcile_children(old, [b, a], self.make)
        self.assertIs(new[1].previous, new[0])
        self.assertIn(old[0], changed, "앞 형제가 바뀌면 다시 배치해야 합니다")

    def test_first_child_has_no_previous(self):
        a = Element("p", {}, None)
        new, _ = reconcile_children([], [a], self.make)
        self.assertIsNone(new[0].previous)

    def test_insert_in_the_middle(self):
        a, b, c = (Element("p", {}, None), Element("b", {}, None),
                   Element("i", {}, None))
        old, _ = reconcile_children([], [a, c], self.make)
        new, changed = reconcile_children(old, [a, b, c], self.make)
        self.assertIs(new[2].previous, new[1])
        self.assertEqual(len(changed), 2, "새 자식과 그 뒤 하나만")

    def test_untouched_siblings_are_not_marked(self):
        nodes = [Element("p", {}, None) for _ in range(5)]
        old, _ = reconcile_children([], nodes, self.make)
        extra = Element("b", {}, None)
        _, changed = reconcile_children(old, [extra] + nodes, self.make)
        self.assertEqual(len(changed), 2, "새 것과 그 다음 하나뿐")

    def test_insert_before_through_the_dom(self):
        tab = make_tab('<div id="d"><b id="q">나</b></div>')
        tab.root_frame.js.interp.evaljs(
            "var i = document.createElement('i');"
            "d.insertBefore(i, q);0;")
        self.assertEqual([c.tag for c in by_id(tab.root_frame.nodes,
                                               "d").children],
                         ["i", "b"])


class Exercise168(unittest.TestCase):
    """16-8 :hover 의사 클래스"""

    HTML = '<div id="d">글자</div>'
    CSS = ("div { display: block; background-color: blue; } "
           "div:hover { background-color: red; }")

    def hover_tab(self):
        return make_tab("<style>" + self.CSS + "</style>" + self.HTML)

    def test_selector_is_parsed(self):
        rules = CSSParser(self.CSS).parse()
        hover = [sel for sel, _ in rules
                 if getattr(sel, "pseudoclass", None) == "hover"]
        self.assertEqual(len(hover), 1)

    def test_not_hovered_by_default(self):
        tab = self.hover_tab()
        self.assertEqual(by_id(tab.root_frame.nodes, "d")
                         .style["background-color"], "blue")

    def test_hovering_changes_the_style(self):
        tab = self.hover_tab()
        text = next(c for c in tab.flat_display_list
                    if getattr(c, "text", None) == "글자")
        tab.hover(text.rect.left + 1, text.rect.top + 1 - tab.scroll)
        self.assertEqual(by_id(tab.root_frame.nodes, "d")
                         .style["background-color"], "red")

    def test_moving_away_clears_it(self):
        tab = self.hover_tab()
        text = next(c for c in tab.flat_display_list
                    if getattr(c, "text", None) == "글자")
        tab.hover(text.rect.left + 1, text.rect.top + 1 - tab.scroll)
        tab.hover(5000, 5000)
        self.assertEqual(by_id(tab.root_frame.nodes, "d")
                         .style["background-color"], "blue")

    def test_hovering_the_same_node_is_a_no_op(self):
        tab = self.hover_tab()
        text = next(c for c in tab.flat_display_list
                    if getattr(c, "text", None) == "글자")
        x, y = text.rect.left + 1, text.rect.top + 1 - tab.scroll
        self.assertTrue(tab.hover(x, y))
        self.assertFalse(tab.hover(x, y), "같은 곳이면 다시 하지 않습니다")

    def test_hover_restyles_only_what_changed(self):
        tab = self.hover_tab()
        text = next(c for c in tab.flat_display_list
                    if getattr(c, "text", None) == "글자")
        tab.hover(text.rect.left + 1, text.rect.top + 1 - tab.scroll)
        total = len(tree_to_list(tab.root_frame.nodes, []))
        self.assertLess(len(tab.root_frame.style_stats), total)


class Exercise169(unittest.TestCase):
    """16-9 ProtectedField 없애기"""

    def test_store_starts_dirty(self):
        store = FieldStore()
        store.declare("x")
        self.assertTrue(store.is_dirty("x"))

    def test_reading_dirty_raises(self):
        store = FieldStore()
        store.declare("x")
        with self.assertRaises(DependencyError):
            store.get("x")

    def test_set_and_get(self):
        store = FieldStore()
        store.set("x", 5)
        self.assertEqual(store.get("x"), 5)

    def test_invalidation_crosses_stores(self):
        a, b = FieldStore(), FieldStore()
        a.set("x", 1)
        b.set("y", a.read("x", notify=(b, "y")) + 1)
        a.set("x", 2)
        self.assertTrue(b.is_dirty("y"))

    def test_same_value_does_not_invalidate(self):
        a, b = FieldStore(), FieldStore()
        a.set("x", 1)
        b.set("y", a.read("x", notify=(b, "y")))
        a.set("x", 1)
        self.assertFalse(b.is_dirty("y"))

    def test_ancestor_flags_still_work(self):
        root = FieldStore()
        child = FieldStore(root)
        child.set("x", 1)
        child.mark("x")
        self.assertTrue(root.has_dirty_descendants)

    def test_no_field_objects_are_created(self):
        store = FieldStore()
        for i in range(100):
            store.set("f%d" % i, i)
        self.assertEqual(store.field_count(), 0)

    def test_store_uses_slots(self):
        """딕셔너리 하나 없이 슬롯만 씁니다."""
        self.assertFalse(hasattr(FieldStore(), "__dict__"))

    def test_same_semantics_as_protected_field(self):
        a = ProtectedField(Owner(), "a")
        b = ProtectedField(Owner(), "b")
        a.set(1)
        b.set(a.read(notify=b))
        a.set(2)

        sa, sb = FieldStore(), FieldStore()
        sa.set("a", 1)
        sb.set("b", sa.read("a", notify=(sb, "b")))
        sa.set("a", 2)
        self.assertEqual(b.dirty, sb.is_dirty("b"))


class Exercise1610(unittest.TestCase):
    """16-10 paint 최적화하기"""

    HTML = "<div><p>가</p></div><div><p>나</p></div><div><p>다</p></div>"

    def fresh(self):
        doc = DocumentLayout(styled(self.HTML))
        doc.layout()
        cmds = []
        stats = paint_tree_cached(doc, cmds)
        return doc, cmds, stats

    def test_first_paint_paints_everything(self):
        _, _, stats = self.fresh()
        self.assertGreater(stats["repainted"], 0)
        self.assertEqual(stats["reused"], 0)

    def test_second_paint_reuses_everything(self):
        doc, _, _ = self.fresh()
        cmds = []
        stats = paint_tree_cached(doc, cmds)
        self.assertEqual(stats["repainted"], 0)
        self.assertEqual(stats["reused"], 1)

    def test_reused_display_list_is_the_same(self):
        doc, first, _ = self.fresh()
        second = []
        paint_tree_cached(doc, second)
        self.assertEqual([type(c).__name__ for c in flatten(first)],
                         [type(c).__name__ for c in flatten(second)])

    def test_dirtying_one_box_repaints_only_its_branch(self):
        doc, _, _ = self.fresh()
        target = [o for o in tree_to_list(doc, [])
                  if isinstance(o, BlockLayout) and o.element("p")][1]
        mark_paint_dirty(target)
        cmds = []
        stats = paint_tree_cached(doc, cmds)
        total = len(tree_to_list(doc, []))
        self.assertGreater(stats["reused"], 0)
        self.assertLess(stats["repainted"], total)

    def test_dirty_branch_reaches_the_root(self):
        doc, _, _ = self.fresh()
        target = [o for o in tree_to_list(doc, [])
                  if isinstance(o, BlockLayout) and o.element("p")][1]
        mark_paint_dirty(target)
        self.assertTrue(doc.has_dirty_paint_descendants)

    def test_content_is_still_complete_after_a_partial_repaint(self):
        doc, _, _ = self.fresh()
        target = [o for o in tree_to_list(doc, [])
                  if isinstance(o, BlockLayout) and o.element("p")][1]
        mark_paint_dirty(target)
        cmds = []
        paint_tree_cached(doc, cmds)
        words = [c.text for c in flatten(cmds) if hasattr(c, "text")]
        for word in ("가", "나", "다"):
            self.assertIn(word, words)


class CarriedForward(unittest.TestCase):
    """1~15장 연습문제가 그대로 도는지"""

    def test_chapter15_canvas(self):
        tab = make_tab('<canvas id="c" width="100" height="50"></canvas>'
                       '<script>var x = c.getContext("2d");'
                       'x.fillStyle = "red"; x.fillRect(5,5,20,20);</script>')
        self.assertTrue([c for c in tab.flat_display_list
                         if isinstance(c, DrawRect) and c.color == "red"])

    def test_chapter15_iframe(self):
        inner = doc_url("<p>안쪽</p>").replace('"', "%22")
        tab = make_tab('<iframe src="%s"></iframe>' % inner)
        self.assertEqual(len(tab.frames()), 2)

    def test_chapter14_zoom_property(self):
        tree = styled('<div style="zoom: 2"><p>글</p></div>')
        self.assertAlmostEqual(ex14.effective_zoom(find_el(tree, "p")[0]), 2.0)

    def test_chapter13_z_index(self):
        _, cmds = build('<div id="a">가</div><div id="b">나</div>',
                        "#a { position: relative; z-index: 5; } "
                        "#b { position: relative; z-index: 1; }")
        self.assertEqual([c.text for c in flatten(cmds)
                          if isinstance(c, DrawText)], ["나", "가"])

    def test_chapter11_border_radius(self):
        _, cmds = build("<div>글</div>",
                        "div { background-color: red; border-radius: 10px; }")
        self.assertTrue([c for c in flatten(cmds)
                         if isinstance(c, ex11.DrawRRect)])

    def test_chapter10_password(self):
        _, cmds = build('<input name="p" type="password" value="abc">')
        self.assertIn("***", [c.text for c in flatten(cmds)
                              if isinstance(c, DrawText)])

    def test_chapter9_dom(self):
        tab = make_tab('<div id="d"><p>가</p>글자<b>나</b></div>')
        self.assertEqual(tab.root_frame.js.interp.evaljs("d.children.length"),
                         2)

    def test_chapter5_bullets(self):
        _, cmds = build("<ul><li>하나</li><li>둘</li></ul>")
        self.assertEqual(len([c for c in flatten(cmds)
                              if isinstance(c, DrawRect)
                              and c.color == "black"]), 2)

    def test_chapter3_smallcaps(self):
        _, cmds = build("<abbr>abc</abbr>")
        self.assertIn("ABC", "".join(c.text for c in flatten(cmds)
                                     if isinstance(c, DrawText)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
