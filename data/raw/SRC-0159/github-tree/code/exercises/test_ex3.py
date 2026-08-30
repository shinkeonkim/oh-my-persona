"""3장 연습문제 검증.

폰트 메트릭이 필요하므로 숨긴 Tk 루트를 하나 만들어 두고 배치 결과를 확인한다.

    python3 test_ex3.py
"""

import tkinter
import unittest

import ex3
from ex3 import Layout, lex, get_font, HSTEP, WIDTH, SOFT_HYPHEN, PRE_FAMILY

_root = None


def setUpModule():
    global _root
    _root = tkinter.Tk()
    _root.withdraw()


def tearDownModule():
    if _root is not None:
        _root.destroy()


def place(html, width=WIDTH):
    return Layout(lex(html), width).display_list


def texts(dl):
    return [t for _, _, t, _ in dl]


def xs(dl):
    return [x for x, _, _, _ in dl]


def ys(dl):
    return [y for _, y, _, _ in dl]


def lines(dl):
    """같은 y 끼리 묶어 줄 단위로 본다."""
    out = {}
    for x, y, t, f in dl:
        out.setdefault(round(y), []).append((x, t, f))
    return [out[k] for k in sorted(out)]


class Exercise31(unittest.TestCase):
    """3-1 가운데 정렬"""

    def test_title_is_centered(self):
        dl = place('<h1 class="title">제목</h1>')
        x = xs(dl)[0]
        self.assertGreater(x, HSTEP, "가운데로 밀려야 합니다")

    def test_plain_h1_not_centered(self):
        dl = place('<h1>제목</h1>')
        self.assertEqual(xs(dl)[0], HSTEP)

    def test_body_text_not_centered(self):
        dl = place('<h1 class="title">제목</h1>본문입니다')
        title_x = xs(dl)[0]
        body_x = xs(dl)[-1]
        self.assertGreater(title_x, body_x)
        self.assertEqual(body_x, HSTEP)

    def test_each_line_centered_separately(self):
        dl = place('<h1 class="title">' + "말 " * 120 + '</h1>')
        rows = lines(dl)
        self.assertGreater(len(rows), 1, "여러 줄이어야 의미가 있습니다")
        starts = [row[0][0] for row in rows]
        self.assertTrue(all(s > HSTEP for s in starts))
        # 줄마다 길이가 다르니 시작 x 도 달라야 한다
        self.assertGreater(len(set(starts)), 1, "줄마다 따로 가운데 정렬해야 합니다")


class Exercise32(unittest.TestCase):
    """3-2 위 첨자"""

    def test_superscript_is_smaller(self):
        dl = place('보통<sup>윗첨자</sup>')
        normal_font = dl[0][3]
        sup_font = dl[1][3]
        self.assertLess(sup_font.cget("size"), normal_font.cget("size"))

    def test_tops_line_up(self):
        dl = place('보통<sup>윗첨자</sup>')
        (_, y_normal, _, f_normal), (_, y_sup, _, f_sup) = dl[0], dl[1]
        # 위 첨자의 윗선이 보통 글자의 윗선과 같아야 한다
        self.assertAlmostEqual(y_sup, y_normal, delta=1.5)

    def test_superscript_ends(self):
        dl = place('가<sup>나</sup>다')
        self.assertEqual(dl[0][3].cget("size"), dl[2][3].cget("size"))

    def test_superscript_sits_above_baseline(self):
        dl = place('보통<sup>윗첨자</sup>')
        _, y_normal, _, f_normal = dl[0]
        _, y_sup, _, f_sup = dl[1]
        base_normal = y_normal + f_normal.metrics("ascent")
        base_sup = y_sup + f_sup.metrics("ascent")
        self.assertLess(base_sup, base_normal, "위 첨자 기준선이 더 위여야 합니다")


class Exercise33(unittest.TestCase):
    """3-3 소프트 하이픈"""

    LONG = ("super" + SOFT_HYPHEN + "cali" + SOFT_HYPHEN + "fragi" + SOFT_HYPHEN
            + "listic" + SOFT_HYPHEN + "expi" + SOFT_HYPHEN + "ali" + SOFT_HYPHEN
            + "docious")

    def test_not_shown_when_it_fits(self):
        dl = place("a" + SOFT_HYPHEN + "b")
        self.assertEqual(texts(dl), ["ab"])
        self.assertNotIn(SOFT_HYPHEN, "".join(texts(dl)))

    def test_breaks_across_lines(self):
        dl = place(self.LONG, width=120)
        self.assertGreater(len(lines(dl)), 1, "좁은 창에서 나뉘어야 합니다")

    def test_draws_hyphen_at_break(self):
        dl = place(self.LONG, width=120)
        rows = lines(dl)
        self.assertTrue(rows[0][-1][1].endswith("-"), "끊은 자리에 하이픈이 필요합니다")

    def test_no_soft_hyphen_left_in_output(self):
        dl = place(self.LONG, width=120)
        self.assertNotIn(SOFT_HYPHEN, "".join(texts(dl)))

    def test_all_letters_survive(self):
        dl = place(self.LONG, width=120)
        joined = "".join(texts(dl)).replace("-", "")
        self.assertEqual(joined, self.LONG.replace(SOFT_HYPHEN, ""))


class Exercise34(unittest.TestCase):
    """3-4 스몰 캡"""

    def test_lowercase_becomes_uppercase(self):
        dl = place("<abbr>abc</abbr>")
        self.assertEqual("".join(texts(dl)), "ABC")

    def test_lowercase_is_smaller_and_bold(self):
        dl = place("<abbr>abc</abbr>")
        font = dl[0][3]
        self.assertEqual(font.cget("weight"), "bold")
        plain = place("abc")[0][3]
        self.assertLess(font.cget("size"), plain.cget("size"))

    def test_uppercase_keeps_normal_font(self):
        dl = place("<abbr>ABC</abbr>")
        self.assertEqual(dl[0][3].cget("weight"), "normal")

    def test_mixed_word_splits_into_runs(self):
        dl = place("<abbr>aBc</abbr>")
        self.assertEqual(len(dl), 3, "소문자/대문자 구간이 나뉘어야 합니다")
        self.assertEqual("".join(texts(dl)), "ABC")
        self.assertEqual(dl[0][3].cget("weight"), "bold")     # a
        self.assertEqual(dl[1][3].cget("weight"), "normal")   # B
        self.assertEqual(dl[2][3].cget("weight"), "bold")     # c

    def test_runs_do_not_overlap(self):
        dl = place("<abbr>aBc</abbr>")
        for (x1, _, t1, f1), (x2, _, _, _) in zip(dl, dl[1:]):
            self.assertGreaterEqual(x2, x1 + f1.measure(t1) - 1)

    def test_ends_after_close_tag(self):
        dl = place("<abbr>ab</abbr>cd")
        self.assertEqual(texts(dl)[-1], "cd")


class Exercise35(unittest.TestCase):
    """3-5 서식이 지정된 텍스트"""

    def test_uses_fixed_width_font(self):
        dl = place("<pre>code</pre>")
        self.assertEqual(dl[0][3].cget("family"), PRE_FAMILY)

    def test_preserves_spaces(self):
        dl = place("<pre>a    b</pre>")
        self.assertEqual(texts(dl), ["a    b"])

    def test_newline_starts_new_line(self):
        dl = place("<pre>a\nb</pre>")
        self.assertEqual(texts(dl), ["a", "b"])
        self.assertGreater(ys(dl)[1], ys(dl)[0])

    def test_no_automatic_wrapping(self):
        dl = place("<pre>" + "x" * 400 + "</pre>", width=200)
        self.assertEqual(len(lines(dl)), 1, "<pre> 는 자동으로 줄을 바꾸지 않습니다")

    def test_bold_works_inside_pre(self):
        dl = place("<pre>a <b>b</b></pre>")
        weights = [f.cget("weight") for _, _, _, f in dl]
        self.assertIn("bold", weights)
        self.assertTrue(all(f.cget("family") == PRE_FAMILY for _, _, _, f in dl))

    def test_normal_text_after_pre(self):
        dl = place("<pre>code</pre>보통")
        self.assertNotEqual(dl[-1][3].cget("family"), PRE_FAMILY)


class CarriedForward(unittest.TestCase):
    """1~2장 연습문제가 그대로 살아 있는지"""

    def test_chapter1_data_url(self):
        self.assertEqual(ex3.parse_url("data:text/html,hi").request(), "hi")

    def test_chapter2_about_blank(self):
        self.assertEqual(ex3.parse_url("!!!").scheme, "about")

    def test_chapter2_scroll_clamp(self):
        self.assertEqual(ex3.clamp_scroll(-10, []), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
