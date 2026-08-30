"""HTML 파서.

글자를 훑는 일(`parse`)과 트리를 쌓는 일(`add_text`/`add_tag`)을 나눠 두었다.
`handle_text`/`handle_tag` 훅만 갈아끼우면 훑는 규칙을 그대로 쓰면서 다른
결과물을 만들 수 있다 — `SourceParser` 가 그렇게 한다.

주석·스크립트·따옴표 속성·잘못 중첩된 서식 태그를 모두 다룬다.
"""

from wbe.dom.nodes import Element, Text, decode_entities

SELF_CLOSING_TAGS = [
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
]
HEAD_TAGS = [
    "base", "basefont", "bgsound", "noscript",
    "link", "meta", "title", "style", "script",
]

# 잘못 중첩돼도 바로잡아 줄 서식 태그
FORMATTING_TAGS = ["b", "i", "big", "small", "em", "strong", "u", "s",
                   "abbr", "sup"]

# 같은 태그가 또 열리면 앞의 것을 닫는다. 값은 거기서 멈출 태그들.
AUTO_CLOSE = {
    "p": [],                     # 어디서 만나든 앞의 <p> 를 닫는다
    "li": ["ul", "ol"],          # 단, 새 목록 안으로 들어가면 멈춘다
}


def tag_name(raw):
    raw = raw.strip()
    return raw.split()[0].casefold() if raw.split() else ""


class HTMLParser:
    def __init__(self, body):
        self.body = body
        self.unfinished = []

    # -- 글자 훑기 (상태 기계) ------------------------------------------ #

    def parse(self):
        body, i, text = self.body, 0, ""
        while i < len(body):
            if body.startswith("<!--", i):
                if text:
                    self.handle_text(text)
                    text = ""
                i = self.skip_comment(i)
            elif body[i] == "<":
                if text:
                    self.handle_text(text)
                    text = ""
                i, raw = self.read_tag(i)
                if raw is None:
                    break                        # 안 닫힌 태그는 버린다
                self.handle_tag(raw)
                if tag_name(raw) == "script":
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
        """`<!-->` 는 빈 주석이다. `<!--` 바로 뒤에 `>` 가 오면 거기서 끝난다."""
        start = i + len("<!--")
        if self.body.startswith(">", start):
            return start + 1
        end = self.body.find("-->", start)
        return len(self.body) if end < 0 else end + len("-->")

    def read_tag(self, i):
        """따옴표 안의 `>` 는 태그를 끝내지 않는다."""
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
        """`</script>` 전까지는 무조건 글자로 본다."""
        lowered = self.body.casefold()
        end = lowered.find("</script", i)
        if end < 0:
            return len(self.body), self.body[i:]
        raw = self.body[i:end]
        after, _ = self.read_tag(end)
        return after, raw

    # -- 훅 ------------------------------------------------------------- #

    def handle_text(self, text, raw=False):
        # 트리에는 원문이 아니라 실제 문자를 담는다. 그래야 innerHTML 로 다시
        # 적을 때 &lt; 가 &amp;lt; 로 겹치지 않는다. <script> 안은 그대로 둔다.
        self.add_text(text if raw else decode_entities(text))

    def handle_tag(self, raw):
        self.add_tag(raw)

    # -- 속성 ----------------------------------------------------------- #

    def get_attributes(self, text):
        """따옴표 안의 공백을 견딘다."""
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
                if len(value) >= 2 and value[0] in "\"'" \
                        and value[-1] == value[0]:
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
            if name in FORMATTING_TAGS and self.close_mis_nested(name):
                return
            node = self.unfinished.pop()
            self.unfinished[-1].children.append(node)
        elif tag in SELF_CLOSING_TAGS:
            parent = self.unfinished[-1]
            parent.children.append(Element(tag, attributes, parent))
        else:
            if tag in AUTO_CLOSE:
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
        """같은 태그가 열려 있으면 닫아서 형제로 만든다."""
        for j in range(len(self.unfinished) - 1, 0, -1):
            name = self.unfinished[j].tag
            if name in stoppers:
                return               # 새 목록 안이면 중첩이 맞다
            if name == tag:
                while len(self.unfinished) > j:
                    self.close_element()
                return

    def close_mis_nested(self, name):
        """안쪽 서식 태그를 닫았다가 다시 연다. 처리했으면 True."""
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
            elif open_tags == ["html"] and \
                    tag not in ["head", "body", "/html"]:
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


class SourceParser(HTMLParser):
    """view-source: 를 위한 구문 강조.

    훑는 규칙은 그대로 두고 결과만 `<pre>` 안에 담는다. 태그는 보통 글꼴로,
    내용은 `<b>` 로 감싸 굵게 그린다. 파서를 상속했으므로 주석·스크립트·
    따옴표 처리가 실제 파서와 어긋날 일이 없다.
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


def parse_document(body, view_source=False):
    return (SourceParser(body) if view_source else HTMLParser(body)).parse()
