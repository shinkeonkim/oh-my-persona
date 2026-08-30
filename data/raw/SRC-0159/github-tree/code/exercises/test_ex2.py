"""2장 연습문제 검증.

레이아웃·스크롤·스크롤바 계산이 순수 함수라 창을 띄우지 않고 확인할 수 있다.

    python3 test_ex2.py
"""

import os
import tempfile
import unittest

import ex2
from ex2 import (HSTEP, VSTEP, WIDTH, HEIGHT, PARAGRAPH_STEP,
                 layout, content_height, max_scroll, clamp_scroll,
                 scrollbar_geometry, is_emoji, emoji_path, parse_url, URL)


def ys(display_list):
    return [y for _, y, _ in display_list]


def chars(display_list):
    return "".join(c for _, _, c in display_list)


class Exercise21(unittest.TestCase):
    """2-1 줄바꿈"""

    def test_newline_starts_new_line(self):
        dl = layout("a\nb")
        self.assertEqual(chars(dl), "ab")
        self.assertGreater(ys(dl)[1], ys(dl)[0], "줄바꿈 뒤 y 가 내려가야 합니다")

    def test_newline_resets_x(self):
        dl = layout("aaa\nb")
        self.assertEqual(dl[-1][0], HSTEP, "줄바꿈 뒤 x 가 처음으로 돌아가야 합니다")

    def test_paragraph_gap_bigger_than_wrap(self):
        wrapped = layout("x" * 200)                 # 자동 줄바꿈
        wrap_gap = sorted(set(ys(wrapped)))[1] - sorted(set(ys(wrapped)))[0]
        explicit = layout("a\nb")
        para_gap = ys(explicit)[1] - ys(explicit)[0]
        self.assertEqual(wrap_gap, VSTEP)
        self.assertEqual(para_gap, VSTEP + PARAGRAPH_STEP)
        self.assertGreater(para_gap, wrap_gap, "문단 사이가 더 벌어져야 합니다")

    def test_newline_not_drawn(self):
        self.assertNotIn("\n", chars(layout("a\nb")))


class Exercise22And24(unittest.TestCase):
    """2-2 위로 스크롤 / 2-4 맨 아래 고정"""

    def setUp(self):
        self.short = layout("짧은 글")
        self.long = layout("긴 글 " * 4000)

    def test_cannot_scroll_above_top(self):
        self.assertEqual(clamp_scroll(-500, self.long), 0)

    def test_cannot_scroll_past_bottom(self):
        limit = max_scroll(self.long)
        self.assertEqual(clamp_scroll(limit + 10_000, self.long), limit)

    def test_short_page_does_not_scroll(self):
        self.assertEqual(max_scroll(self.short), 0)
        self.assertEqual(clamp_scroll(SCROLL := 300, self.short), 0)

    def test_long_page_scrolls(self):
        self.assertGreater(max_scroll(self.long), 0)

    def test_content_height_covers_last_line(self):
        self.assertGreaterEqual(content_height(self.long), max(ys(self.long)))


class Exercise23(unittest.TestCase):
    """2-3 크기 조절 — 너비가 바뀌면 줄바꿈이 달라진다"""

    def test_narrow_window_wraps_more(self):
        text = "x" * 300
        wide = layout(text, width=800)
        narrow = layout(text, width=300)
        self.assertGreater(content_height(narrow), content_height(wide))

    def test_same_characters_regardless_of_width(self):
        text = "hello world"
        self.assertEqual(chars(layout(text, 800)), chars(layout(text, 200)))


class Exercise24Scrollbar(unittest.TestCase):
    """2-4 스크롤바"""

    def test_hidden_when_everything_fits(self):
        self.assertIsNone(scrollbar_geometry(0, layout("짧다")))

    def test_shown_when_content_overflows(self):
        dl = layout("긴 글 " * 4000)
        self.assertIsNotNone(scrollbar_geometry(0, dl))

    def test_on_right_edge(self):
        dl = layout("긴 글 " * 4000)
        x0, _, x1, _ = scrollbar_geometry(0, dl)
        self.assertEqual(x1, WIDTH)
        self.assertLess(x0, x1)

    def test_moves_down_as_you_scroll(self):
        dl = layout("긴 글 " * 4000)
        top = scrollbar_geometry(0, dl)
        mid = scrollbar_geometry(max_scroll(dl) // 2, dl)
        self.assertGreater(mid[1], top[1], "스크롤하면 막대가 내려가야 합니다")

    def test_shorter_bar_for_longer_page(self):
        def height_of(n):
            dl = layout("긴 글 " * n)
            g = scrollbar_geometry(0, dl)
            return g[3] - g[1]
        self.assertGreater(height_of(2000), height_of(20000),
                           "내용이 길수록 막대가 짧아야 합니다")

    def test_stays_inside_window(self):
        dl = layout("긴 글 " * 4000)
        _, y0, _, y1 = scrollbar_geometry(max_scroll(dl), dl)
        self.assertGreaterEqual(y0, 0)
        self.assertLessEqual(y1, HEIGHT)


class Exercise25(unittest.TestCase):
    """2-5 이모지"""

    def test_detects_emoji(self):
        self.assertTrue(is_emoji("\N{GRINNING FACE}"))
        self.assertTrue(is_emoji("\N{PARTY POPPER}"))

    def test_plain_text_is_not_emoji(self):
        for c in "a1 가.":
            self.assertFalse(is_emoji(c), c)

    def test_openmoji_filename(self):
        self.assertEqual(os.path.basename(emoji_path("\N{GRINNING FACE}")),
                         "1F600.png")

    def test_missing_file_is_tolerated(self):
        with tempfile.TemporaryDirectory() as d:
            path = emoji_path("\N{GRINNING FACE}", directory=d)
            self.assertFalse(os.path.exists(path))   # 없으면 글자로 그린다


class Exercise26(unittest.TestCase):
    """2-6 about:blank"""

    def test_about_blank_is_empty(self):
        self.assertEqual(URL("about:blank").request(), "")

    def test_malformed_url_falls_back(self):
        for bad in ["", "://", "gopher://example.org/", "!!!", "ht tp://x"]:
            self.assertEqual(parse_url(bad).scheme, "about",
                             "%r 는 about:blank 이어야 합니다" % bad)

    def test_good_url_still_parsed(self):
        self.assertEqual(parse_url("https://example.org/").scheme, "https")

    def test_chapter1_schemes_still_work(self):
        # 1장 연습문제가 그대로 이어지는지
        self.assertEqual(parse_url("data:text/html,hi").request(), "hi")
        self.assertTrue(parse_url("view-source:data:text/html,<b>x</b>").view_source)


class Exercise27(unittest.TestCase):
    """2-7 텍스트 방향"""

    def test_rtl_starts_from_right(self):
        ltr = layout("abc", rtl=False)
        rtl = layout("abc", rtl=True)
        self.assertLess(ltr[0][0], WIDTH / 2)
        self.assertGreater(rtl[0][0], WIDTH / 2, "오른쪽에서 시작해야 합니다")

    def test_rtl_grows_leftward(self):
        rtl = layout("abc", rtl=True)
        xs = [x for x, _, _ in rtl]
        self.assertEqual(xs, sorted(xs, reverse=True))

    def test_same_text_and_line_count(self):
        text = "hello world " * 30
        ltr, rtl = layout(text), layout(text, rtl=True)
        self.assertEqual(chars(ltr), chars(rtl))
        self.assertEqual(ys(ltr), ys(rtl))

    def test_rtl_stays_on_screen(self):
        for x, _, _ in layout("가나다라마" * 50, rtl=True):
            self.assertGreaterEqual(x, 0)
            self.assertLess(x, WIDTH)


if __name__ == "__main__":
    unittest.main(verbosity=2)
