"""5장 연습문제 검증.

    python3 test_ex5.py
"""

import tkinter
import unittest

import ex5
from ex5 import (HTMLParser, DocumentLayout, BlockLayout, DrawRect, DrawText,
                 paint_tree, group_children, Element, Text,
                 LINKS_BAR_COLOR, TOC_COLOR, TOC_LABEL, LIST_INDENT)

_root = None


def setUpModule():
    global _root
    _root = tkinter.Tk()
    _root.withdraw()


def tearDownModule():
    if _root is not None:
        _root.destroy()


def build(html):
    tree = HTMLParser(html).parse()
    doc = DocumentLayout(tree)
    doc.layout()
    cmds = []
    paint_tree(doc, cmds)
    return doc, cmds


def boxes(obj, out=None):
    out = [] if out is None else out
    for c in obj.children:
        out.append(c)
        boxes(c, out)
    return out


def rects(cmds, color):
    return [c for c in cmds if isinstance(c, DrawRect) and c.color == color]


def texts(cmds):
    return [c.text for c in cmds if isinstance(c, DrawText)]


def find_el(node, tag, out=None):
    out = [] if out is None else out
    if isinstance(node, Element):
        if node.tag == tag:
            out.append(node)
        for c in node.children:
            find_el(c, tag, out)
    return out


class Exercise51(unittest.TestCase):
    """5-1 링크 바"""

    def test_links_bar_has_background(self):
        _, cmds = build('<nav class="links">이전 다음</nav>')
        self.assertEqual(len(rects(cmds, LINKS_BAR_COLOR)), 1)

    def test_plain_nav_has_no_background(self):
        _, cmds = build("<nav>이전 다음</nav>")
        self.assertEqual(rects(cmds, LINKS_BAR_COLOR), [])

    def test_background_covers_the_bar(self):
        doc, cmds = build('<nav class="links">이전 다음</nav>')
        rect = rects(cmds, LINKS_BAR_COLOR)[0]
        self.assertGreater(rect.bottom, rect.top)
        self.assertGreater(rect.right, rect.left)

    def test_background_painted_under_text(self):
        _, cmds = build('<nav class="links">이전</nav>')
        rect_i = next(i for i, c in enumerate(cmds)
                      if isinstance(c, DrawRect) and c.color == LINKS_BAR_COLOR)
        text_i = next(i for i, c in enumerate(cmds) if isinstance(c, DrawText))
        self.assertLess(rect_i, text_i, "배경이 글자보다 먼저 그려져야 합니다")


class Exercise52(unittest.TestCase):
    """5-2 숨겨진 head"""

    HTML = "<head><title>제목</title></head><body>본문</body>"

    def test_head_still_in_html_tree(self):
        tree = HTMLParser(self.HTML).parse()
        self.assertEqual(len(find_el(tree, "head")), 1)

    def test_head_not_in_layout_tree(self):
        doc, _ = build(self.HTML)
        tags = [b.node.tag for b in boxes(doc)
                if isinstance(b.node, Element)]
        self.assertNotIn("head", tags)

    def test_title_not_drawn(self):
        _, cmds = build(self.HTML)
        self.assertNotIn("제목", texts(cmds))

    def test_body_still_drawn(self):
        _, cmds = build(self.HTML)
        self.assertIn("본문", texts(cmds))

    def test_script_and_style_hidden_too(self):
        _, cmds = build("<body><script>var x=1</script><p>보임</p></body>")
        self.assertNotIn("var", " ".join(texts(cmds)))
        self.assertIn("보임", texts(cmds))


class Exercise53(unittest.TestCase):
    """5-3 글머리 기호"""

    def test_bullet_drawn_for_each_item(self):
        _, cmds = build("<ul><li>하나</li><li>둘</li></ul>")
        self.assertEqual(len(rects(cmds, "black")), 2)

    def test_bullet_is_small_square(self):
        _, cmds = build("<ul><li>하나</li></ul>")
        b = rects(cmds, "black")[0]
        self.assertEqual(b.right - b.left, b.bottom - b.top)
        self.assertLessEqual(b.right - b.left, 8)

    def test_text_indented_past_bullet(self):
        doc, _ = build("<ul><li>하나</li></ul>")
        li = next(b for b in boxes(doc)
                  if isinstance(b.node, Element) and b.node.tag == "li")
        ul = next(b for b in boxes(doc)
                  if isinstance(b.node, Element) and b.node.tag == "ul")
        self.assertEqual(li.x - ul.x, LIST_INDENT)

    def test_bullet_left_of_text(self):
        doc, cmds = build("<ul><li>하나</li></ul>")
        bullet = rects(cmds, "black")[0]
        text = next(c for c in cmds if isinstance(c, DrawText))
        self.assertLess(bullet.left, text.left)

    def test_no_bullet_without_li(self):
        _, cmds = build("<p>문단</p>")
        self.assertEqual(rects(cmds, "black"), [])


class Exercise54(unittest.TestCase):
    """5-4 목차"""

    HTML = '<nav id="toc"><ul><li>1장</li></ul></nav>'

    def test_label_drawn(self):
        _, cmds = build(self.HTML)
        self.assertIn(TOC_LABEL, texts(cmds))

    def test_label_has_gray_background(self):
        _, cmds = build(self.HTML)
        self.assertEqual(len(rects(cmds, TOC_COLOR)), 1)

    def test_label_above_the_list(self):
        _, cmds = build(self.HTML)
        label = next(c for c in cmds
                     if isinstance(c, DrawText) and c.text == TOC_LABEL)
        item = next(c for c in cmds
                    if isinstance(c, DrawText) and c.text == "1장")
        self.assertLess(label.top, item.top, "제목이 목록 위에 있어야 합니다")

    def test_label_does_not_overlap_list(self):
        _, cmds = build(self.HTML)
        label = next(c for c in cmds
                     if isinstance(c, DrawText) and c.text == TOC_LABEL)
        item = next(c for c in cmds
                    if isinstance(c, DrawText) and c.text == "1장")
        self.assertGreaterEqual(item.top, label.bottom - 1,
                                "목록이 제목 아래로 밀려야 합니다")

    def test_other_nav_has_no_label(self):
        _, cmds = build("<nav><ul><li>1장</li></ul></nav>")
        self.assertNotIn(TOC_LABEL, texts(cmds))


class Exercise55(unittest.TestCase):
    """5-5 익명 블록 박스"""

    HTML = "<div><i>기울임</i><b>굵게</b><p>문단</p></div>"

    def test_groups_leading_inlines(self):
        tree = HTMLParser("<div><i>a</i><b>b</b><p>c</p></div>").parse()
        div = find_el(tree, "div")[0]
        groups = group_children(div)
        self.assertEqual(len(groups), 2, "앞의 둘이 한 묶음이어야 합니다")
        self.assertEqual(len(groups[0]), 2)

    def test_makes_two_boxes(self):
        doc, _ = build(self.HTML)
        div = next(b for b in boxes(doc)
                   if isinstance(b.node, Element) and b.node.tag == "div")
        self.assertEqual(len(div.children), 2)

    def test_anonymous_box_is_inline(self):
        doc, _ = build(self.HTML)
        div = next(b for b in boxes(doc)
                   if isinstance(b.node, Element) and b.node.tag == "div")
        self.assertTrue(div.children[0].anonymous)
        self.assertEqual(div.children[0].layout_mode(), "inline")

    def test_inlines_share_a_line(self):
        _, cmds = build(self.HTML)
        ys = {c.top for c in cmds
              if isinstance(c, DrawText) and c.text in ("기울임", "굵게")}
        self.assertEqual(len(ys), 1, "같은 줄에 놓여야 합니다")

    def test_paragraph_on_its_own_line(self):
        _, cmds = build(self.HTML)
        inline_y = next(c.top for c in cmds
                        if isinstance(c, DrawText) and c.text == "기울임")
        para_y = next(c.top for c in cmds
                      if isinstance(c, DrawText) and c.text == "문단")
        self.assertGreater(para_y, inline_y)

    def test_all_text_survives(self):
        _, cmds = build(self.HTML)
        for word in ("기울임", "굵게", "문단"):
            self.assertIn(word, texts(cmds))


class Exercise56(unittest.TestCase):
    """5-6 런인 제목"""

    HTML = "<div><h6>제목.</h6><p>이어지는 본문</p></div>"

    def test_h6_shares_line_with_paragraph(self):
        _, cmds = build(self.HTML)
        head_y = next(c.top for c in cmds
                      if isinstance(c, DrawText) and c.text == "제목.")
        body_y = next(c.top for c in cmds
                      if isinstance(c, DrawText) and c.text == "이어지는")
        self.assertEqual(head_y, body_y, "제목이 본문과 같은 줄이어야 합니다")

    def test_h6_is_bold(self):
        _, cmds = build(self.HTML)
        head = next(c for c in cmds
                    if isinstance(c, DrawText) and c.text == "제목.")
        body = next(c for c in cmds
                    if isinstance(c, DrawText) and c.text == "이어지는")
        self.assertEqual(head.font.cget("weight"), "bold")
        self.assertEqual(body.font.cget("weight"), "normal")

    def test_h6_comes_first(self):
        _, cmds = build(self.HTML)
        head = next(c for c in cmds
                    if isinstance(c, DrawText) and c.text == "제목.")
        body = next(c for c in cmds
                    if isinstance(c, DrawText) and c.text == "이어지는")
        self.assertLess(head.left, body.left)

    def test_grouped_into_one_box(self):
        tree = HTMLParser(self.HTML).parse()
        div = find_el(tree, "div")[0]
        groups = group_children(div)
        self.assertEqual(len(groups), 1, "h6 과 p 가 한 상자여야 합니다")

    def test_other_headings_unaffected(self):
        _, cmds = build("<div><h2>제목</h2><p>본문</p></div>")
        head_y = next(c.top for c in cmds
                      if isinstance(c, DrawText) and c.text == "제목")
        body_y = next(c.top for c in cmds
                      if isinstance(c, DrawText) and c.text == "본문")
        self.assertLess(head_y, body_y, "h2 는 줄을 따로 씁니다")


class CarriedForward(unittest.TestCase):
    """1~4장 연습문제가 그대로 살아 있는지"""

    def test_chapter4_comment(self):
        _, cmds = build("가<!-- 숨김 -->나")
        self.assertNotIn("숨김", " ".join(texts(cmds)))

    def test_chapter4_quoted_attribute(self):
        _, cmds = build('<nav class="links" title="a > b">x</nav>')
        self.assertEqual(len(rects(cmds, LINKS_BAR_COLOR)), 1)

    def test_chapter3_pre_preserves_spaces(self):
        _, cmds = build("<pre>a    b</pre>")
        self.assertIn("a    b", texts(cmds))

    def test_chapter3_smallcaps(self):
        _, cmds = build("<abbr>abc</abbr>")
        self.assertIn("ABC", "".join(texts(cmds)))

    def test_chapter2_about_blank(self):
        self.assertEqual(ex5.parse_url("!!!").scheme, "about")


if __name__ == "__main__":
    unittest.main(verbosity=2)
