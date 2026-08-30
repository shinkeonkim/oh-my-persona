"""3장 연습문제 구현 (3-1 ~ 3-5).

lab3.py 는 그대로 두고, 1~2장 연습문제를 이어받아 그 위에 3장 연습문제를 얹는다.
다음 장 연습문제 파일(ex4.py)이 여기서 import 한다.

    python3 ex3.py https://browser.engineering/

구현한 연습문제
    3-1 가운데 정렬   <h1 class="title"> 안의 텍스트를 줄마다 가운데로
    3-2 위 첨자      <sup> 를 작게, 보통 글자의 윗선에 맞춰
    3-3 소프트 하이픈  단어 안의 U+00AD 에서 줄을 나누고 하이픈을 그린다
    3-4 스몰 캡      <abbr> 안의 소문자를 작은 대문자 굵게
    3-5 서식 텍스트   <pre> 안의 공백과 줄바꿈을 그대로, 고정폭 글꼴로

Layout 은 tkinter 창 없이도 만들 수 있어서(숨긴 Tk 루트만 있으면 된다) 배치 결과를
그대로 시험할 수 있다.
"""

import sys
import tkinter
import tkinter.font

from ex2 import (URL, parse_url, WIDTH, HEIGHT, HSTEP, VSTEP, SCROLL_STEP,
                 clamp_scroll, scrollbar_geometry, SCROLLBAR_COLOR)

SOFT_HYPHEN = "\N{soft hyphen}"
PRE_FAMILY = "Courier New"

# 연습문제 3-2 / 3-4 에서 글자를 얼마나 줄일지
SUP_SCALE = 0.5
SMALLCAPS_SCALE = 0.75


# ---------------------------------------------------------------------- #
# 토큰
# ---------------------------------------------------------------------- #

class Text:
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return "Text(%r)" % self.text


class Tag:
    def __init__(self, tag):
        self.tag = tag

    @property
    def name(self):
        """'h1 class="title"' -> 'h1'"""
        return self.tag.split()[0].casefold() if self.tag.split() else ""

    def has(self, needle):
        return needle in self.tag

    def __repr__(self):
        return "Tag(%r)" % self.tag


def lex(body):
    """연습문제 3-5: <pre> 안에서는 공백을 뭉개지 않으므로 원문을 그대로 담는다."""
    out, buffer, in_tag = [], "", False
    for c in body:
        if c == "<":
            in_tag = True
            if buffer:
                out.append(Text(buffer))
            buffer = ""
        elif c == ">":
            in_tag = False
            out.append(Tag(buffer))
            buffer = ""
        else:
            buffer += c
    if not in_tag and buffer:
        out.append(Text(buffer))
    return out


FONTS = {}


def get_font(size, weight, style, family=None):
    key = (size, weight, style, family)
    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight, slant=style,
                                 **({"family": family} if family else {}))
        FONTS[key] = (font, tkinter.Label(font=font))
    return FONTS[key][0]


# ---------------------------------------------------------------------- #
# 배치
# ---------------------------------------------------------------------- #

class Layout:
    def __init__(self, tokens, width=WIDTH):
        self.width = width
        self.display_list = []
        self.line = []              # (x, 글자, 폰트, 위첨자여부)
        self.cursor_x, self.cursor_y = HSTEP, VSTEP
        self.size, self.weight, self.style = 12, "normal", "roman"
        self.centered = False       # 3-1
        self.superscript = False    # 3-2
        self.smallcaps = False      # 3-4
        self.pre = False            # 3-5
        for tok in tokens:
            self.token(tok)
        self.flush()

    # -- 폰트 ---------------------------------------------------------- #

    def font(self):
        size = self.size
        if self.superscript:
            size = max(6, int(size * SUP_SCALE))
        return get_font(size, self.weight, self.style,
                        PRE_FAMILY if self.pre else None)

    # -- 토큰 처리 ------------------------------------------------------ #

    def token(self, tok):
        if isinstance(tok, Text):
            if self.pre:
                self.pre_text(tok.text)          # 3-5
            else:
                for word in tok.text.split():
                    self.word(word)
            return

        name = tok.name
        if name == "i":
            self.style = "italic"
        elif name == "/i":
            self.style = "roman"
        elif name == "b":
            self.weight = "bold"
        elif name == "/b":
            self.weight = "normal"
        elif name == "small":
            self.size -= 2
        elif name == "/small":
            self.size += 2
        elif name == "big":
            self.size += 4
        elif name == "/big":
            self.size -= 4
        elif name == "br":
            self.flush()
        elif name == "/p":
            self.flush()
            self.cursor_y += VSTEP
        elif name == "h1" and tok.has('class="title"'):   # 3-1
            self.flush()
            self.centered = True
        elif name == "/h1":
            self.flush()
            self.centered = False
        elif name == "sup":                                # 3-2
            self.superscript = True
        elif name == "/sup":
            self.superscript = False
        elif name == "abbr":                               # 3-4
            self.smallcaps = True
        elif name == "/abbr":
            self.smallcaps = False
        elif name == "pre":                                # 3-5
            self.flush()
            self.pre = True
        elif name == "/pre":
            self.flush()
            self.pre = False

    # -- 낱말 배치 ------------------------------------------------------ #

    def measure(self, text, font):
        return font.measure(text)

    def place(self, text, font, space=True):
        """줄 버퍼에 한 조각을 놓고 커서를 옮긴다."""
        self.line.append((self.cursor_x, text, font, self.superscript))
        self.cursor_x += self.measure(text, font)
        if space:
            self.cursor_x += self.measure(" ", font)

    def fits(self, text, font):
        return self.cursor_x + self.measure(text, font) <= self.width - HSTEP

    def word(self, word):
        if self.smallcaps:
            self.smallcaps_word(word)            # 3-4
            return
        font = self.font()
        plain = word.replace(SOFT_HYPHEN, "")
        if not self.fits(plain, font):
            if SOFT_HYPHEN in word and self.hyphenate(word, font):   # 3-3
                return
            self.flush()
        self.place(plain, font)

    def hyphenate(self, word, font):
        """연습문제 3-3: 소프트 하이픈에서 끊어 앞부분 + '-' 만 이번 줄에 둔다."""
        parts = word.split(SOFT_HYPHEN)
        for i in range(len(parts) - 1, 0, -1):
            head = "".join(parts[:i]) + "-"
            if self.fits(head, font):
                self.place(head, font, space=False)
                self.flush()
                rest = SOFT_HYPHEN.join(parts[i:])
                self.word(rest)                  # 남은 부분도 다시 시도
                return True
        return False

    def smallcaps_word(self, word):
        """연습문제 3-4: 소문자만 작은 대문자 굵게, 나머지는 그대로."""
        big = get_font(self.size, self.weight, self.style)
        small = get_font(max(6, int(self.size * SMALLCAPS_SCALE)), "bold", self.style)
        if not self.fits(word.replace(SOFT_HYPHEN, ""), big):
            self.flush()
        runs, cur, cur_lower = [], "", None
        for c in word.replace(SOFT_HYPHEN, ""):
            lower = c.islower()
            if cur and lower != cur_lower:
                runs.append((cur, cur_lower))
                cur = ""
            cur, cur_lower = cur + c, lower
        if cur:
            runs.append((cur, cur_lower))
        for i, (run, lower) in enumerate(runs):
            last = (i == len(runs) - 1)
            if lower:
                self.place(run.upper(), small, space=last)
            else:
                self.place(run, big, space=last)

    def pre_text(self, text):
        """연습문제 3-5: 줄바꿈은 줄을 끝내고, 공백은 그대로 둔다. 자동 줄바꿈 없음."""
        segments = text.split("\n")
        for i, seg in enumerate(segments):
            if i:
                self.flush()
            if seg:
                self.place(seg, self.font(), space=False)

    # -- 줄 마무리 ------------------------------------------------------ #

    def line_width(self):
        if not self.line:
            return 0
        first_x = self.line[0][0]
        last_x, last_text, last_font, _ = self.line[-1]
        return last_x + self.measure(last_text, last_font) - first_x

    def flush(self):
        if not self.line:
            self.cursor_x = HSTEP
            return

        metrics = [font.metrics() for _, _, font, _ in self.line]
        max_ascent = max(m["ascent"] for m in metrics)
        max_descent = max(m["descent"] for m in metrics)
        baseline = self.cursor_y + 1.25 * max_ascent

        offset = 0
        if self.centered:                                   # 3-1
            offset = (self.width - self.line_width()) / 2 - self.line[0][0]

        for x, text, font, is_sup in self.line:
            if is_sup:
                # 3-2: 위 첨자의 윗선을 보통 글자의 윗선에 맞춘다
                y = baseline - max_ascent
            else:
                y = baseline - font.metrics("ascent")
            self.display_list.append((x + offset, y, text, font))

        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = HSTEP
        self.line = []


def content_height(display_list):
    if not display_list:
        return 0
    return max(y + font.metrics("linespace") for _, y, _, font in display_list)


# ---------------------------------------------------------------------- #
# 브라우저 (2장 연습문제의 스크롤·크기조절·스크롤바를 이어받는다)
# ---------------------------------------------------------------------- #

class Browser:
    def __init__(self):
        self.width, self.height = WIDTH, HEIGHT
        self.tokens = []
        self.display_list = []
        self.scroll = 0

        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.canvas.pack(fill="both", expand=True)

        self.window.bind("<Down>", lambda e: self.scroll_by(SCROLL_STEP))
        self.window.bind("<Up>", lambda e: self.scroll_by(-SCROLL_STEP))
        self.window.bind("<Configure>", self.resize)
        self.window.bind("<MouseWheel>", self.on_wheel)
        self.window.bind("<Button-4>", self.on_wheel)
        self.window.bind("<Button-5>", self.on_wheel)

    def load(self, url):
        self.tokens = lex(url.request())
        self.relayout()

    def relayout(self):
        self.display_list = Layout(self.tokens, self.width).display_list
        self.scroll = self.clamp(self.scroll)
        self.draw()

    def clamp(self, scroll):
        bottom = max(0, content_height(self.display_list) - self.height + VSTEP)
        return max(0, min(scroll, bottom))

    def scroll_by(self, delta):
        scroll = self.clamp(self.scroll + delta)
        if scroll != self.scroll:
            self.scroll = scroll
            self.draw()

    def on_wheel(self, e):
        if getattr(e, "num", None) == 4:
            delta = -SCROLL_STEP
        elif getattr(e, "num", None) == 5:
            delta = SCROLL_STEP
        elif abs(e.delta) >= 120:
            delta = -(e.delta // 120) * SCROLL_STEP
        else:
            delta = -e.delta * SCROLL_STEP // 3
        self.scroll_by(delta)

    def resize(self, e):
        if e.width == self.width and e.height == self.height:
            return
        self.width, self.height = e.width, e.height
        self.relayout()

    def draw(self):
        self.canvas.delete("all")
        for x, y, text, font in self.display_list:
            if y > self.scroll + self.height:
                continue
            if y + font.metrics("linespace") < self.scroll:
                continue
            self.canvas.create_text(x, y - self.scroll, text=text,
                                    font=font, anchor="nw")
        total = content_height(self.display_list)
        if total > self.height:
            frac_shown = self.height / total
            y0 = self.height * (self.scroll / total)
            self.canvas.create_rectangle(
                self.width - 12, y0, self.width,
                min(y0 + self.height * frac_shown, self.height),
                fill=SCROLLBAR_COLOR, width=0)


def main(argv):
    url = parse_url(argv[0]) if argv else URL("about:blank")
    Browser().load(url)
    tkinter.mainloop()


if __name__ == "__main__":
    main(sys.argv[1:])
