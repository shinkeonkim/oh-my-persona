"""5장 연습문제 구현 (5-1 ~ 5-6).

lab5.py 는 그대로 두고, 1~4장 연습문제를 이어받아 그 위에 5장 연습문제를 얹는다.
3~4장의 글자 배치 기능(가운데 정렬·위 첨자·소프트 하이픈·스몰 캡·<pre>)은
BlockLayout 안으로 옮겨 그대로 살아 있다.

    python3 ex5.py https://browser.engineering/

구현한 연습문제
    5-1 링크 바        <nav class="links"> 에 옅은 회색 배경
    5-2 숨겨진 head    <head> 는 레이아웃 트리에 넣지 않는다
    5-3 글머리 기호     <li> 앞에 작은 사각형, 글자는 오른쪽으로 들여쓰기
    5-4 목차           <nav id="toc"> 위에 회색 배경의 제목 줄
    5-5 익명 블록 박스   글자 같은 형제들을 하나의 블록으로 묶는다
    5-6 런인 제목       <h6> 을 다음 문단의 첫머리로 붙인다

BlockLayout 이 노드 하나가 아니라 '형제 노드 목록'을 받는 것이 핵심이다.
5-5 도 5-6 도 결국 '어떤 형제들을 한 상자에 담을까' 의 문제라서 같은 장치로 풀린다.
"""

import sys
import tkinter

from ex2 import (URL, parse_url, WIDTH, HEIGHT, HSTEP, VSTEP, SCROLL_STEP,
                 SCROLLBAR_COLOR)
from ex3 import get_font, SOFT_HYPHEN, PRE_FAMILY, SUP_SCALE, SMALLCAPS_SCALE
from ex4 import HTMLParser, SourceParser, Text, Element, print_tree

BLOCK_ELEMENTS = [
    "html", "body", "article", "section", "nav", "aside",
    "h1", "h2", "h3", "h4", "h5", "h6", "hgroup", "header",
    "footer", "address", "p", "hr", "pre", "blockquote",
    "ol", "ul", "menu", "li", "dl", "dt", "dd", "figure",
    "figcaption", "main", "div", "table", "form", "fieldset",
    "legend", "details", "summary",
]

# 연습문제 5-1 / 5-4
LINKS_BAR_COLOR = "#eeeeee"
TOC_COLOR = "#dddddd"
TOC_LABEL = "Table of Contents"

# 연습문제 5-3
BULLET_SIZE = 4
LIST_INDENT = 2 * HSTEP


# ---------------------------------------------------------------------- #
# 그리기 명령
# ---------------------------------------------------------------------- #

class DrawText:
    def __init__(self, x1, y1, text, font):
        self.top = y1
        self.left = x1
        self.text = text
        self.font = font
        self.bottom = y1 + font.metrics("linespace")

    def execute(self, scroll, canvas):
        canvas.create_text(self.left, self.top - scroll, text=self.text,
                           font=self.font, anchor="nw")

    def __repr__(self):
        return "DrawText(%r)" % self.text


class DrawRect:
    def __init__(self, x1, y1, x2, y2, color):
        self.top, self.left = y1, x1
        self.bottom, self.right = y2, x2
        self.color = color

    def execute(self, scroll, canvas):
        canvas.create_rectangle(self.left, self.top - scroll,
                                self.right, self.bottom - scroll,
                                width=0, fill=self.color)

    def __repr__(self):
        return "DrawRect(%s)" % self.color


def paint_tree(layout_object, display_list):
    display_list.extend(layout_object.paint())
    for child in layout_object.children:
        paint_tree(child, display_list)


# ---------------------------------------------------------------------- #
# 어떤 형제들을 한 상자에 담을까 (5-2, 5-5, 5-6)
# ---------------------------------------------------------------------- #

def is_block(node):
    return isinstance(node, Element) and node.tag in BLOCK_ELEMENTS


def is_skipped(node):
    """연습문제 5-2: <head> 는 트리에는 있지만 화면에는 없다."""
    return isinstance(node, Element) and node.tag in ("head", "script", "style")


def group_children(node):
    """자식들을 레이아웃 상자 단위(형제 목록)로 묶는다.

    - 5-2 <head> 는 건너뛴다
    - 5-6 <h6> 은 자기 상자를 만들지 않고 다음 묶음의 첫머리로 들어간다
    - 5-5 글자 같은 형제들이 이어지면 하나의 익명 상자로 묶는다
    """
    groups = []
    run = []          # 글자 같은 형제들을 모으는 중인 익명 상자
    pending_runin = []  # 다음 묶음 앞에 붙일 <h6>

    def flush_run():
        if run:
            groups.append(run[:])
            run.clear()

    for child in node.children:
        if is_skipped(child):
            continue
        if isinstance(child, Element) and child.tag == "h6":      # 5-6
            flush_run()
            pending_runin.append(child)
            continue
        if is_block(child):
            flush_run()
            groups.append(pending_runin + [child])
            pending_runin = []
        else:
            if pending_runin:
                run.extend(pending_runin)
                pending_runin = []
            run.append(child)
    flush_run()
    if pending_runin:
        groups.append(pending_runin)
    return groups


# ---------------------------------------------------------------------- #
# 레이아웃
# ---------------------------------------------------------------------- #

class BlockLayout:
    def __init__(self, nodes, parent, previous):
        # 연습문제 5-5: 노드 하나가 아니라 형제 목록을 받는다
        self.nodes = nodes if isinstance(nodes, list) else [nodes]
        self.node = self.nodes[0]
        self.parent = parent
        self.previous = previous
        self.children = []
        self.x = self.y = self.width = self.height = None
        self.display_list = []

    # -- 모드 ---------------------------------------------------------- #

    @property
    def anonymous(self):
        """5-5 로 만들어진 익명 상자인지 (요소 하나에 대응하지 않는다)."""
        return len(self.nodes) > 1 or isinstance(self.node, Text)

    def element(self, tag=None):
        """이 상자가 대응하는 요소. 익명 상자면 None."""
        if len(self.nodes) == 1 and isinstance(self.node, Element):
            if tag is None or self.node.tag == tag:
                return self.node
        return None

    def layout_mode(self):
        if any(isinstance(n, Text) for n in self.nodes):
            return "inline"
        if len(self.nodes) > 1:
            return "inline"                      # 5-5 익명 상자
        node = self.node
        if any(is_block(c) for c in node.children):
            return "block"
        return "inline" if node.children else "block"

    # -- 배치 ---------------------------------------------------------- #

    def toc_label_height(self):
        """연습문제 5-4: 목차 위에 넣을 제목 줄 높이."""
        if self.element("nav") and self.node.attributes.get("id") == "toc":
            return get_font(12, "bold", "roman").metrics("linespace")
        return 0

    def list_indent(self):
        """연습문제 5-3: <li> 는 글머리 기호만큼 들여쓴다."""
        return LIST_INDENT if self.element("li") else 0

    def content_top(self):
        """자식이 시작할 y. 연습문제 5-4 의 제목 줄만큼 아래로 민다."""
        return self.y + self.toc_label_height()

    def layout(self):
        indent = self.list_indent()
        self.x = self.parent.x + indent
        self.width = self.parent.width - indent
        # 첫 자식은 부모의 content_top 에서 시작한다 (5-4)
        self.y = (self.previous.y + self.previous.height
                  if self.previous else self.parent.content_top())

        label = self.toc_label_height()

        mode = self.layout_mode()
        if mode == "block":
            previous = None
            for group in group_children(self.node):
                child = BlockLayout(group, self, previous)
                self.children.append(child)
                previous = child
        else:
            self.cursor_x = 0
            self.cursor_y = label
            self.size, self.weight, self.style = 12, "normal", "roman"
            self.centered = self.superscript = self.smallcaps = self.pre = False
            self.line = []
            for node in self.nodes:
                self.recurse(node)
            self.flush()

        for child in self.children:
            child.layout()

        if mode == "block":
            self.height = label + sum(c.height for c in self.children)
        else:
            self.height = self.cursor_y

    # -- 글자 배치 (3~4장 연습문제를 그대로 가져옴) ---------------------- #

    def font(self):
        size = self.size
        if self.superscript:
            size = max(6, int(size * SUP_SCALE))
        return get_font(size, self.weight, self.style,
                        PRE_FAMILY if self.pre else None)

    def recurse(self, node):
        if isinstance(node, Text):
            if self.pre:
                self.pre_text(node.text)
            else:
                for word in node.text.split():
                    self.word(word)
        else:
            self.open_tag(node)
            for child in node.children:
                self.recurse(child)
            self.close_tag(node)

    def open_tag(self, node):
        tag = node.tag
        if tag == "i":
            self.style = "italic"
        elif tag == "b":
            self.weight = "bold"
        elif tag == "small":
            self.size -= 2
        elif tag == "big":
            self.size += 4
        elif tag == "br":
            self.flush()
        elif tag == "sup":
            self.superscript = True
        elif tag == "abbr":
            self.smallcaps = True
        elif tag == "h6":
            self.weight = "bold"            # 5-6 런인 제목은 굵게
        elif tag == "pre":
            self.flush()
            self.pre = True
        elif tag == "h1" and node.attributes.get("class") == "title":
            self.flush()
            self.centered = True

    def close_tag(self, node):
        tag = node.tag
        if tag == "i":
            self.style = "roman"
        elif tag == "b":
            self.weight = "normal"
        elif tag == "small":
            self.size += 2
        elif tag == "big":
            self.size -= 4
        elif tag == "sup":
            self.superscript = False
        elif tag == "abbr":
            self.smallcaps = False
        elif tag == "h6":
            self.weight = "normal"          # 5-6: 줄을 끝내지 않는다
        elif tag == "pre":
            self.flush()
            self.pre = False
        elif tag == "h1" and node.attributes.get("class") == "title":
            self.flush()
            self.centered = False

    def measure(self, text, font):
        return font.measure(text)

    def place(self, text, font, space=True):
        self.line.append((self.cursor_x, text, font, self.superscript))
        self.cursor_x += self.measure(text, font)
        if space:
            self.cursor_x += self.measure(" ", font)

    def fits(self, text, font):
        return self.cursor_x + self.measure(text, font) <= self.width

    def word(self, word):
        if self.smallcaps:
            self.smallcaps_word(word)
            return
        font = self.font()
        plain = word.replace(SOFT_HYPHEN, "")
        if not self.fits(plain, font):
            if SOFT_HYPHEN in word and self.hyphenate(word, font):
                return
            self.flush()
        self.place(plain, font)

    def hyphenate(self, word, font):
        parts = word.split(SOFT_HYPHEN)
        for i in range(len(parts) - 1, 0, -1):
            head = "".join(parts[:i]) + "-"
            if self.fits(head, font):
                self.place(head, font, space=False)
                self.flush()
                self.word(SOFT_HYPHEN.join(parts[i:]))
                return True
        return False

    def smallcaps_word(self, word):
        big = get_font(self.size, self.weight, self.style)
        small = get_font(max(6, int(self.size * SMALLCAPS_SCALE)), "bold",
                         self.style)
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
            self.place(run.upper() if lower else run,
                       small if lower else big, space=last)

    def pre_text(self, text):
        for i, seg in enumerate(text.split("\n")):
            if i:
                self.flush()
            if seg:
                self.place(seg, self.font(), space=False)

    def line_width(self):
        if not self.line:
            return 0
        first_x = self.line[0][0]
        last_x, last_text, last_font, _ = self.line[-1]
        return last_x + self.measure(last_text, last_font) - first_x

    def flush(self):
        if not self.line:
            self.cursor_x = 0
            return
        metrics = [font.metrics() for _, _, font, _ in self.line]
        max_ascent = max(m["ascent"] for m in metrics)
        max_descent = max(m["descent"] for m in metrics)
        baseline = self.cursor_y + 1.25 * max_ascent
        offset = ((self.width - self.line_width()) / 2 - self.line[0][0]
                  if self.centered else 0)
        for rel_x, text, font, is_sup in self.line:
            y = (baseline - max_ascent) if is_sup \
                else (baseline - font.metrics("ascent"))
            self.display_list.append(
                (self.x + rel_x + offset, self.y + y, text, font))
        self.cursor_x = 0
        self.cursor_y = baseline + 1.25 * max_descent
        self.line = []

    # -- 그리기 -------------------------------------------------------- #

    def paint(self):
        cmds = []
        el = self.element()

        if el is not None:
            if el.tag == "pre":
                cmds.append(DrawRect(self.x, self.y,
                                     self.x + self.width, self.y + self.height,
                                     "gray"))
            # 연습문제 5-1
            if el.tag == "nav" and el.attributes.get("class") == "links":
                cmds.append(DrawRect(self.x, self.y,
                                     self.x + self.width, self.y + self.height,
                                     LINKS_BAR_COLOR))
            # 연습문제 5-4
            if el.tag == "nav" and el.attributes.get("id") == "toc":
                font = get_font(12, "bold", "roman")
                h = font.metrics("linespace")
                cmds.append(DrawRect(self.x, self.y,
                                     self.x + self.width, self.y + h, TOC_COLOR))
                cmds.append(DrawText(self.x, self.y, TOC_LABEL, font))
            # 연습문제 5-3
            if el.tag == "li":
                top = self.y + (VSTEP - BULLET_SIZE) // 2
                left = self.x - LIST_INDENT // 2
                cmds.append(DrawRect(left, top,
                                     left + BULLET_SIZE, top + BULLET_SIZE,
                                     "black"))

        if self.layout_mode() == "inline":
            for x, y, word, font in self.display_list:
                cmds.append(DrawText(x, y, word, font))
        return cmds

    def __repr__(self):
        what = "익명" if self.anonymous else self.node
        return "BlockLayout[%s](x=%s, y=%s, w=%s, h=%s, %s)" % (
            self.layout_mode(), self.x, self.y, self.width, self.height, what)


class DocumentLayout:
    def __init__(self, node):
        self.node = node
        self.parent = None
        self.previous = None
        self.children = []
        self.x = self.y = self.width = self.height = None

    def content_top(self):
        return self.y

    def layout(self):
        self.width = WIDTH - 2 * HSTEP
        self.x = HSTEP
        self.y = VSTEP
        child = BlockLayout([self.node], self, None)
        self.children.append(child)
        child.layout()
        self.height = child.height

    def paint(self):
        return []

    def __repr__(self):
        return "DocumentLayout(w=%s, h=%s)" % (self.width, self.height)


# ---------------------------------------------------------------------- #
# 브라우저
# ---------------------------------------------------------------------- #

class Browser:
    def __init__(self):
        self.scroll = 0
        self.display_list = []
        self.document = None
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.canvas.pack(fill="both", expand=True)
        self.window.bind("<Down>", lambda e: self.scroll_by(SCROLL_STEP))
        self.window.bind("<Up>", lambda e: self.scroll_by(-SCROLL_STEP))
        self.window.bind("<MouseWheel>",
                         lambda e: self.scroll_by(-e.delta * SCROLL_STEP // 3))

    def load(self, url):
        body = url.request()
        parser = SourceParser(body) if url.view_source else HTMLParser(body)
        self.nodes = parser.parse()
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)
        self.draw()

    def clamp(self, scroll):
        bottom = max(0, self.document.height + 2 * VSTEP - HEIGHT)
        return max(0, min(scroll, bottom))

    def scroll_by(self, delta):
        scroll = self.clamp(self.scroll + delta)
        if scroll != self.scroll:
            self.scroll = scroll
            self.draw()

    def draw(self):
        self.canvas.delete("all")
        for cmd in self.display_list:
            if cmd.top > self.scroll + HEIGHT:
                continue
            if cmd.bottom < self.scroll:
                continue
            cmd.execute(self.scroll, self.canvas)
        total = self.document.height + 2 * VSTEP
        if total > HEIGHT:
            y0 = HEIGHT * (self.scroll / total)
            self.canvas.create_rectangle(
                WIDTH - 12, y0, WIDTH,
                min(y0 + HEIGHT * (HEIGHT / total), HEIGHT),
                fill=SCROLLBAR_COLOR, width=0)


def main(argv):
    url = parse_url(argv[0]) if argv else URL("about:blank")
    Browser().load(url)
    tkinter.mainloop()


if __name__ == "__main__":
    main(sys.argv[1:])
