"""4장 연습문제 구현 (4-1 ~ 4-6).

lab4.py 는 그대로 두고, 1~3장 연습문제를 이어받아 그 위에 4장 연습문제를 얹는다.
3장까지의 배치 기능(가운데 정렬·위 첨자·소프트 하이픈·스몰 캡·<pre>)은 토큰 순회에서
트리 순회로 옮겨 그대로 살아 있다.

    python3 ex4.py https://browser.engineering/
    python3 ex4.py view-source:https://example.org/     # 4-5 구문 강조

구현한 연습문제
    4-1 주석          <!-- ... --> 를 토큰으로 만들지 않고 건너뛴다
    4-2 문단          <p>/<li> 가 겹치면 형제로 만든다 (중첩 목록은 유지)
    4-3 스크립트       <script> 안은 </script> 전까지 통째로 텍스트
    4-4 따옴표 속성     따옴표 안의 공백과 꺾쇠를 견딘다
    4-5 구문 강조      view-source 에서 태그는 보통, 텍스트는 굵게
    4-6 잘못 중첩 태그  <b>Bold <i>both</b> italic</i> 를 바로잡는다
"""

import sys
import tkinter

from ex2 import (URL, parse_url, WIDTH, HEIGHT, HSTEP, VSTEP, SCROLL_STEP,
                 SCROLLBAR_COLOR)
from ex3 import (get_font, content_height, SOFT_HYPHEN, PRE_FAMILY,
                 SUP_SCALE, SMALLCAPS_SCALE)

SELF_CLOSING_TAGS = [
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
]
HEAD_TAGS = [
    "base", "basefont", "bgsound", "noscript",
    "link", "meta", "title", "style", "script",
]

# 연습문제 4-6: 잘못 중첩돼도 바로잡아 줄 서식 태그
FORMATTING_TAGS = ["b", "i", "big", "small", "em", "strong", "u", "s",
                   "abbr", "sup"]

# 연습문제 4-2: 이 태그들은 같은 태그가 또 열리면 앞의 것을 닫는다
AUTO_CLOSE = {
    "p": [],                     # 어디서 만나든 앞의 <p> 를 닫는다
    "li": ["ul", "ol"],          # 단, 새 목록 안으로 들어가면 멈춘다
}


class Text:
    def __init__(self, text, parent):
        self.text = text
        self.children = []
        self.parent = parent

    def __repr__(self):
        return "Text(%r)" % self.text


class Element:
    def __init__(self, tag, attributes, parent):
        self.tag = tag
        self.attributes = attributes
        self.children = []
        self.parent = parent

    def __repr__(self):
        return "<%s>" % self.tag


def print_tree(node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)


# ---------------------------------------------------------------------- #
# 파서
# ---------------------------------------------------------------------- #

class HTMLParser:
    def __init__(self, body):
        self.body = body
        self.unfinished = []

    # -- 글자 훑기 (상태 기계) ------------------------------------------ #

    def parse(self):
        body, i, text = self.body, 0, ""
        while i < len(body):
            if body.startswith("<!--", i):                 # 4-1
                if text:
                    self.handle_text(text)
                    text = ""
                i = self.skip_comment(i)
            elif body[i] == "<":
                if text:
                    self.handle_text(text)
                    text = ""
                i, raw = self.read_tag(i)                  # 4-4
                if raw is None:
                    break                                  # 안 닫힌 태그는 버린다
                self.handle_tag(raw)
                if tag_name(raw) == "script":              # 4-3
                    i, raw_js = self.read_script(i)
                    if raw_js:
                        self.handle_text(raw_js, raw=True)
                    self.handle_tag("/script")
            else:
                text += body[i]
                i += 1
        if text:
            self.handle_text(text)
        return self.finish()

    def skip_comment(self, i):
        """연습문제 4-1.

        `<!-->` 는 빈 주석이다. `<!--` 바로 뒤에 `>` 가 오면 거기서 끝난다.
        (HTML 명세도 그렇게 본다.)
        """
        start = i + len("<!--")
        if self.body.startswith(">", start):
            return start + 1
        end = self.body.find("-->", start)
        return len(self.body) if end < 0 else end + len("-->")

    def read_tag(self, i):
        """연습문제 4-4: 따옴표 안의 `>` 는 태그를 끝내지 않는다."""
        i += 1                       # '<' 건너뛰기
        buf, quote = "", None
        while i < len(self.body):
            c = self.body[i]
            if quote:
                buf += c
                if c == quote:
                    quote = None
            elif c in "\"'":
                buf += c
                quote = c
            elif c == ">":
                return i + 1, buf
            else:
                buf += c
            i += 1
        return i, None               # 끝까지 안 닫혔다

    def read_script(self, i):
        """연습문제 4-3: </script> 전까지는 무조건 글자로 본다."""
        lowered = self.body.casefold()
        end = lowered.find("</script", i)
        if end < 0:
            return len(self.body), self.body[i:]
        raw = self.body[i:end]
        after, _ = self.read_tag(end)
        return after, raw

    # -- 훅 (4-5 에서 갈아끼운다) --------------------------------------- #

    def handle_text(self, text, raw=False):
        self.add_text(text)

    def handle_tag(self, raw):
        self.add_tag(raw)

    # -- 속성 ----------------------------------------------------------- #

    def get_attributes(self, text):
        """연습문제 4-4: 따옴표 안의 공백을 견딘다."""
        parts, cur, quote = [], "", None
        for c in text:
            if quote:
                cur += c
                if c == quote:
                    quote = None
            elif c in "\"'":
                cur += c
                quote = c
            elif c.isspace():
                if cur:
                    parts.append(cur)
                    cur = ""
            else:
                cur += c
        if cur:
            parts.append(cur)

        if not parts:
            return "", {}
        tag = parts[0].casefold()
        attributes = {}
        for pair in parts[1:]:
            if "=" in pair:
                key, value = pair.split("=", 1)
                if len(value) >= 2 and value[0] in "\"'" and value[-1] == value[0]:
                    value = value[1:-1]
                attributes[key.casefold()] = value
            else:
                attributes[pair.casefold()] = ""
        return tag, attributes

    # -- 트리 쌓기 ------------------------------------------------------- #

    def add_text(self, text):
        if text.isspace():
            return
        self.implicit_tags(None)
        parent = self.unfinished[-1]
        parent.children.append(Text(text, parent))

    def add_tag(self, raw):
        tag, attributes = self.get_attributes(raw)
        if not tag or tag.startswith("!"):
            return
        self.implicit_tags(tag)

        if tag.startswith("/"):
            name = tag[1:]
            if len(self.unfinished) == 1:
                return
            if name in FORMATTING_TAGS and self.close_mis_nested(name):  # 4-6
                return
            node = self.unfinished.pop()
            self.unfinished[-1].children.append(node)
        elif tag in SELF_CLOSING_TAGS:
            parent = self.unfinished[-1]
            parent.children.append(Element(tag, attributes, parent))
        else:
            if tag in AUTO_CLOSE:                                        # 4-2
                self.auto_close(tag, AUTO_CLOSE[tag])
            self.open_element(tag, attributes)

    def open_element(self, tag, attributes):
        parent = self.unfinished[-1] if self.unfinished else None
        self.unfinished.append(Element(tag, attributes, parent))

    def close_element(self):
        node = self.unfinished.pop()
        self.unfinished[-1].children.append(node)
        return node

    def auto_close(self, tag, stoppers):
        """연습문제 4-2: 같은 태그가 열려 있으면 닫아서 형제로 만든다."""
        for j in range(len(self.unfinished) - 1, 0, -1):
            name = self.unfinished[j].tag
            if name in stoppers:
                return               # 새 목록 안이면 중첩이 맞다
            if name == tag:
                while len(self.unfinished) > j:
                    self.close_element()
                return

    def close_mis_nested(self, name):
        """연습문제 4-6: 안쪽 서식 태그를 임시로 닫았다가 다시 연다."""
        idx = None
        for j in range(len(self.unfinished) - 1, 0, -1):
            if self.unfinished[j].tag == name:
                idx = j
                break
        if idx is None:
            return True              # 짝 없는 닫는 태그는 무시
        inner = [n.tag for n in self.unfinished[idx + 1:]]
        if not inner:
            return False             # 제대로 중첩됐다 — 평소대로 처리
        if not all(t in FORMATTING_TAGS for t in inner):
            return False             # 서식 태그 문제가 아니면 건드리지 않는다
        while len(self.unfinished) > idx:
            self.close_element()     # 안쪽 것들과 자기 자신을 닫고
        for t in inner:
            self.open_element(t, {})  # 안쪽 것들만 다시 연다
        return True

    def implicit_tags(self, tag):
        while True:
            open_tags = [node.tag for node in self.unfinished]
            if open_tags == [] and tag != "html":
                self.add_tag("html")
            elif open_tags == ["html"] and tag not in ["head", "body", "/html"]:
                self.add_tag("head" if tag in HEAD_TAGS else "body")
            elif open_tags == ["html", "head"] and \
                    tag not in ["/head"] + HEAD_TAGS:
                self.add_tag("/head")
            else:
                break

    def finish(self):
        if not self.unfinished:
            self.implicit_tags(None)
        while len(self.unfinished) > 1:
            self.close_element()
        return self.unfinished.pop()


def tag_name(raw):
    raw = raw.strip()
    return raw.split()[0].casefold() if raw.split() else ""


# ---------------------------------------------------------------------- #
# 연습문제 4-5: view-source 구문 강조
# ---------------------------------------------------------------------- #

class SourceParser(HTMLParser):
    """훑는 규칙은 그대로 두고, 결과만 <pre> 안에 강조해 담는다.

    태그는 보통 글꼴로, 텍스트 내용은 <b> 로 감싸 굵게 그린다.
    """

    def parse(self):
        root = Element("html", {}, None)
        body = Element("body", {}, root)
        root.children.append(body)
        self.pre = Element("pre", {}, body)
        body.children.append(self.pre)
        super().parse()
        return root

    def emit(self, text, bold=False):
        if not text:
            return
        parent = self.pre
        if bold:
            b = Element("b", {}, self.pre)
            self.pre.children.append(b)
            parent = b
        parent.children.append(Text(text, parent))

    def handle_text(self, text, raw=False):
        self.emit(text, bold=True)          # 내용은 굵게

    def handle_tag(self, raw):
        self.emit("<" + raw + ">")          # 태그는 보통

    def finish(self):
        return None                          # parse() 가 root 를 돌려준다


# ---------------------------------------------------------------------- #
# 배치 (3장 연습문제를 트리 순회로 옮긴 것)
# ---------------------------------------------------------------------- #

class Layout:
    def __init__(self, tree, width=WIDTH):
        self.width = width
        self.display_list = []
        self.line = []
        self.cursor_x, self.cursor_y = HSTEP, VSTEP
        self.size, self.weight, self.style = 12, "normal", "roman"
        self.centered = False
        self.superscript = False
        self.smallcaps = False
        self.pre = False
        self.recurse(tree)
        self.flush()

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
        elif tag == "p":
            self.flush()
            self.cursor_y += VSTEP
        elif tag == "sup":
            self.superscript = False
        elif tag == "abbr":
            self.smallcaps = False
        elif tag == "pre":
            self.flush()
            self.pre = False
        elif tag == "h1" and node.attributes.get("class") == "title":
            self.flush()
            self.centered = False

    # -- 아래는 3장 연습문제 그대로 -------------------------------------- #

    def measure(self, text, font):
        return font.measure(text)

    def place(self, text, font, space=True):
        self.line.append((self.cursor_x, text, font, self.superscript))
        self.cursor_x += self.measure(text, font)
        if space:
            self.cursor_x += self.measure(" ", font)

    def fits(self, text, font):
        return self.cursor_x + self.measure(text, font) <= self.width - HSTEP

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
            self.cursor_x = HSTEP
            return
        metrics = [font.metrics() for _, _, font, _ in self.line]
        max_ascent = max(m["ascent"] for m in metrics)
        max_descent = max(m["descent"] for m in metrics)
        baseline = self.cursor_y + 1.25 * max_ascent
        offset = ((self.width - self.line_width()) / 2 - self.line[0][0]
                  if self.centered else 0)
        for x, text, font, is_sup in self.line:
            y = (baseline - max_ascent) if is_sup \
                else (baseline - font.metrics("ascent"))
            self.display_list.append((x + offset, y, text, font))
        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = HSTEP
        self.line = []


# ---------------------------------------------------------------------- #
# 브라우저
# ---------------------------------------------------------------------- #

class Browser:
    def __init__(self):
        self.width, self.height = WIDTH, HEIGHT
        self.nodes = None
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
        body = url.request()
        # 연습문제 4-5
        parser = SourceParser(body) if url.view_source else HTMLParser(body)
        self.nodes = parser.parse()
        self.relayout()

    def relayout(self):
        self.display_list = Layout(self.nodes, self.width).display_list
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
            y0 = self.height * (self.scroll / total)
            self.canvas.create_rectangle(
                self.width - 12, y0, self.width,
                min(y0 + self.height * (self.height / total), self.height),
                fill=SCROLLBAR_COLOR, width=0)


def main(argv):
    url = parse_url(argv[0]) if argv else URL("about:blank")
    Browser().load(url)
    tkinter.mainloop()


if __name__ == "__main__":
    main(sys.argv[1:])
