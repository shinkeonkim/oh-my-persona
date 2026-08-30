"""2장 연습문제 구현 (2-1 ~ 2-7).

lab2.py 는 그대로 두고, 1장 연습문제(ex1.py)를 이어받아 그 위에 2장 연습문제를
얹은 Browser 를 새로 정의한다. 다음 장 연습문제 파일(ex3.py)이 여기서 import 한다.

    python3 ex2.py https://browser.engineering/
    python3 ex2.py --rtl https://browser.engineering/     # 2-7
    python3 ex2.py file:///path/to/file.html              # 1-2 도 그대로 동작

구현한 연습문제
    2-1 줄바꿈       줄바꿈 문자에서 줄을 끝내고, 문단 사이는 더 벌린다
    2-2 마우스 휠     위로 스크롤, 맨 위 고정, 휠/트랙패드 이벤트
    2-3 크기 조절     창 크기를 바꾸면 줄바꿈을 다시 계산한다
    2-4 스크롤바      맨 아래 아래로는 안 가고, 오른쪽에 파란 막대를 그린다
    2-5 이모지       글자 대신 OpenMoji PNG 를 그린다
    2-6 about:blank  잘못된 URL 이면 죽지 않고 빈 페이지를 띄운다
    2-7 텍스트 방향   오른쪽에서부터 자라나는 배치

레이아웃과 스크롤 계산은 창 없이도 시험할 수 있도록 순수 함수로 떼어 두었다.
"""

import os
import sys

from ex1 import URL as BaseURL, lex

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

# 연습문제 2-1: 문단이 바뀔 때 한 줄 높이만큼 더 벌린다.
PARAGRAPH_STEP = VSTEP

# 연습문제 2-4
SCROLLBAR_WIDTH = 12
SCROLLBAR_COLOR = "blue"

# 연습문제 2-5: 이 폴더에 <코드포인트 대문자 16진수>.png 를 넣어 두면 그림으로 그린다.
EMOJI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "openmoji")


# ---------------------------------------------------------------------- #
# 연습문제 2-6: about:blank
# ---------------------------------------------------------------------- #

class URL(BaseURL):
    """about: 스킴을 알아듣는다."""

    def __init__(self, url):
        if url.startswith("about:"):
            self.scheme = "about"
            self.view_source = False
            self.path = url[len("about:"):] or "blank"
            return
        super().__init__(url)

    def request(self, *args, **kwargs):
        if self.scheme == "about":
            return ""          # about:blank 은 빈 문서
        return super().request(*args, **kwargs)

    def __repr__(self):
        if self.scheme == "about":
            return "about:" + self.path
        return super().__repr__()


def parse_url(text):
    """잘못된 URL 이면 죽지 않고 about:blank 으로 대신한다 (연습문제 2-6)."""
    try:
        return URL(text)
    except Exception:
        return URL("about:blank")


# ---------------------------------------------------------------------- #
# 연습문제 2-5: 이모지
# ---------------------------------------------------------------------- #

def is_emoji(c):
    """그림으로 그릴 만한 문자인지."""
    o = ord(c)
    return (0x1F300 <= o <= 0x1FAFF     # 그림문자 대부분
            or 0x2600 <= o <= 0x27BF    # 기타 기호와 딩뱃
            or o in (0x2B50, 0x2B1B, 0x2B1C))


def emoji_path(c, directory=EMOJI_DIR):
    """OpenMoji 파일 이름 규칙: 코드포인트를 대문자 16진수 4자리 이상으로."""
    return os.path.join(directory, "{:04X}.png".format(ord(c)))


# ---------------------------------------------------------------------- #
# 레이아웃 (순수 함수 — 창 없이 시험 가능)
# ---------------------------------------------------------------------- #

def layout(text, width=WIDTH, rtl=False):
    """글자마다 (x, y, 글자) 를 만든다.

    연습문제 2-1 줄바꿈 문자 처리, 2-3 너비를 인자로 받기, 2-7 오른쪽 정렬.
    """
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text:
        if c == "\n":                       # 2-1
            cursor_y += VSTEP + PARAGRAPH_STEP
            cursor_x = HSTEP
            continue
        # 2-7: 오른쪽에서부터 채운다. 글자 순서는 그대로 두고 기준선만 뒤집는다.
        x = (width - HSTEP - cursor_x) if rtl else cursor_x
        display_list.append((x, cursor_y, c))
        cursor_x += HSTEP
        if cursor_x >= width - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP
    return display_list


def content_height(display_list):
    """마지막 글자까지의 높이 (연습문제 2-4)."""
    if not display_list:
        return 0
    return max(y for _, y, _ in display_list) + VSTEP


def max_scroll(display_list, height=HEIGHT):
    """더 내려갈 수 없는 지점. 내용이 화면보다 짧으면 0 (연습문제 2-2, 2-4)."""
    return max(0, content_height(display_list) - height + VSTEP)


def clamp_scroll(scroll, display_list, height=HEIGHT):
    """맨 위/맨 아래를 넘지 않게 자른다 (연습문제 2-2, 2-4)."""
    return max(0, min(scroll, max_scroll(display_list, height)))


def scrollbar_geometry(scroll, display_list, width=WIDTH, height=HEIGHT):
    """오른쪽 스크롤바의 (x0, y0, x1, y1). 다 보이면 None (연습문제 2-4)."""
    total = content_height(display_list)
    if total <= height:
        return None                          # 전부 보이면 그리지 않는다
    frac_shown = height / total
    frac_above = scroll / total
    y0 = height * frac_above
    y1 = y0 + height * frac_shown
    return (width - SCROLLBAR_WIDTH, y0, width, min(y1, height))


# ---------------------------------------------------------------------- #
# 브라우저
# ---------------------------------------------------------------------- #

class Browser:
    def __init__(self, rtl=False):
        import tkinter
        self.tkinter = tkinter
        self.rtl = rtl                                    # 2-7
        self.width, self.height = WIDTH, HEIGHT
        self.text = ""
        self.display_list = []
        self.scroll = 0
        self.emoji_cache = {}

        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
        # 연습문제 2-3: 창을 늘리면 캔버스도 따라 늘어난다.
        self.canvas.pack(fill="both", expand=True)

        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)           # 2-2
        self.window.bind("<Configure>", self.resize)      # 2-3
        self.window.bind("<MouseWheel>", self.on_wheel)   # 2-2 (macOS/Windows)
        self.window.bind("<Button-4>", self.on_wheel)     # 2-2 (Linux 위)
        self.window.bind("<Button-5>", self.on_wheel)     # 2-2 (Linux 아래)

    # -- 로드/배치 ----------------------------------------------------- #

    def load(self, url):
        self.text = lex(url.request())
        self.relayout()

    def relayout(self):
        self.display_list = layout(self.text, self.width, self.rtl)
        self.scroll = clamp_scroll(self.scroll, self.display_list, self.height)
        self.draw()

    # -- 이벤트 -------------------------------------------------------- #

    def scrolldown(self, e=None):
        self.scroll_by(SCROLL_STEP)

    def scrollup(self, e=None):
        self.scroll_by(-SCROLL_STEP)

    def scroll_by(self, delta):
        scroll = clamp_scroll(self.scroll + delta, self.display_list, self.height)
        if scroll != self.scroll:
            self.scroll = scroll
            self.draw()

    def on_wheel(self, e):
        """연습문제 2-2: 플랫폼마다 부호와 단위가 다르다."""
        if getattr(e, "num", None) == 4:            # Linux 위로
            delta = -SCROLL_STEP
        elif getattr(e, "num", None) == 5:          # Linux 아래로
            delta = SCROLL_STEP
        elif abs(e.delta) >= 120:                   # Windows 는 120 단위
            delta = -(e.delta // 120) * SCROLL_STEP
        else:                                       # macOS 는 작은 값이 그대로
            delta = -e.delta * SCROLL_STEP // 3
        self.scroll_by(delta)

    def resize(self, e):
        """연습문제 2-3: 너비가 바뀌면 줄바꿈이 달라지므로 다시 배치한다."""
        if e.width == self.width and e.height == self.height:
            return
        self.width, self.height = e.width, e.height
        self.relayout()

    # -- 그리기 -------------------------------------------------------- #

    def emoji_image(self, c):
        """연습문제 2-5: PNG 가 있으면 PhotoImage 로 캐시해 둔다."""
        if c in self.emoji_cache:
            return self.emoji_cache[c]
        path = emoji_path(c)
        image = None
        if os.path.exists(path):
            try:
                image = self.tkinter.PhotoImage(file=path)
            except Exception:
                image = None
        self.emoji_cache[c] = image
        return image

    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            if y > self.scroll + self.height:
                continue
            if y + VSTEP < self.scroll:
                continue
            image = self.emoji_image(c) if is_emoji(c) else None
            if image is not None:                                  # 2-5
                self.canvas.create_image(x, y - self.scroll,
                                         image=image, anchor="nw")
            else:
                self.canvas.create_text(x, y - self.scroll, text=c)

        bar = scrollbar_geometry(self.scroll, self.display_list,
                                 self.width, self.height)          # 2-4
        if bar:
            self.canvas.create_rectangle(*bar, fill=SCROLLBAR_COLOR, width=0)


def main(argv):
    rtl = "--rtl" in argv                                          # 2-7
    args = [a for a in argv if a != "--rtl"]
    url = parse_url(args[0]) if args else URL("about:blank")       # 2-6
    import tkinter
    Browser(rtl=rtl).load(url)
    tkinter.mainloop()


if __name__ == "__main__":
    main(sys.argv[1:])
