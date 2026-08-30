"""CSS 파서.

선택자, 선언, `@media` 블록, `@keyframes` 를 읽는다. 미디어 쿼리는 파싱
시점에 판정하므로, 창 크기나 다크 모드가 바뀌면 스타일시트를 다시 읽어야
한다 — `Frame.rebuild_rules()` 가 그 일을 한다.
"""

from wbe.css.selectors import (ClassSelector, DescendantSelector, HasSelector,
                               IdSelector, ImportantSelector,
                               PseudoclassSelector, PSEUDOCLASSES,
                               SelectorSequence, TagSelector)
from wbe.css.values import expand_shorthand, parse_px_value


class CSSParser:
    def __init__(self, s, media=None):
        self.s = s
        self.i = 0
        self.media = media or {}

    # -- 낱말 ----------------------------------------------------------- #

    def whitespace(self):
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1

    def literal(self, literal):
        if not (self.i < len(self.s) and self.s[self.i] == literal):
            raise Exception("파싱 실패: %r 를 기대했습니다" % literal)
        self.i += 1

    def word(self):
        """속성 이름처럼 값에 가까운 낱말."""
        start = self.i
        while self.i < len(self.s):
            if self.s[self.i].isalnum() or self.s[self.i] in "#-.%_/":
                self.i += 1
            else:
                break
        if self.i == start:
            raise Exception("파싱 실패: 낱말을 기대했습니다")
        return self.s[start:self.i]

    def ident(self):
        """선택자에 쓰는 이름. '.' 과 '#' 은 앞에 붙는 표시라 삼키지 않는다."""
        start = self.i
        while self.i < len(self.s):
            if self.s[self.i].isalnum() or self.s[self.i] in "-_":
                self.i += 1
            else:
                break
        if self.i == start:
            raise Exception("파싱 실패: 이름을 기대했습니다")
        return self.s[start:self.i]

    def value(self):
        """선언의 값.

        괄호 깊이를 센다. `url(data:image/png;base64,...)` 안의 세미콜론은
        선언의 끝이 아니다 — CSS 는 `url(...)` 을 토큰 하나로 본다.
        """
        start, depth = self.i, 0
        while self.i < len(self.s):
            c = self.s[self.i]
            if c == "(":
                depth += 1
            elif c == ")":
                depth = max(0, depth - 1)
            elif c in ";}" and depth == 0:
                break
            self.i += 1
        return self.s[start:self.i].strip()

    def ignore_until(self, chars):
        while self.i < len(self.s):
            if self.s[self.i] in chars:
                return self.s[self.i]
            self.i += 1
        return None

    # -- 선언 ----------------------------------------------------------- #

    def pair(self):
        prop = self.word()
        self.whitespace()
        self.literal(":")
        self.whitespace()
        return prop.casefold(), self.value()

    def body(self):
        """(보통 선언, !important 선언) 두 벌을 돌려준다."""
        normal, important = {}, {}
        while self.i < len(self.s) and self.s[self.i] != "}":
            try:
                prop, val = self.pair()
                target = normal
                if val.casefold().endswith("!important"):
                    val = val[:-len("!important")].strip()
                    target = important
                for k, v in expand_shorthand(prop, val).items():
                    target[k] = v
                self.whitespace()
                if self.i < len(self.s) and self.s[self.i] == ";":
                    self.literal(";")
                    self.whitespace()
            except Exception:
                why = self.ignore_until([";", "}"])
                if why == ";":
                    self.literal(";")
                    self.whitespace()
                else:
                    break
        return normal, important

    # -- 선택자 --------------------------------------------------------- #

    def simple_selector(self):
        parts = []
        if self.i < len(self.s) and self.s[self.i] == "#":
            self.literal("#")
            parts.append(IdSelector(self.ident()))
        elif self.i < len(self.s) and self.s[self.i] == ".":
            self.literal(".")
            parts.append(ClassSelector(self.ident().casefold()))
        else:
            parts.append(TagSelector(self.ident().casefold()))

        while self.i < len(self.s) and self.s[self.i] in ".#":
            if self.s[self.i] == "#":
                self.literal("#")
                parts.append(IdSelector(self.ident()))
            else:
                self.literal(".")
                parts.append(ClassSelector(self.ident().casefold()))

        base = parts[0] if len(parts) == 1 else SelectorSequence(parts)

        if self.s.startswith(":has(", self.i):
            self.i += len(":has(")
            self.whitespace()
            inner = self.simple_selector()
            self.whitespace()
            self.literal(")")
            base = HasSelector(base, inner)

        while self.i < len(self.s) and self.s[self.i] == ":":
            save = self.i
            self.literal(":")
            try:
                name = self.ident().casefold()
            except Exception:
                self.i = save
                break
            if name not in PSEUDOCLASSES:
                self.i = save
                break
            base = PseudoclassSelector(name, base)
        return base

    def selector(self):
        out = [self.simple_selector()]
        self.whitespace()
        while self.i < len(self.s) and self.s[self.i] not in "{,":
            out.append(self.simple_selector())
            self.whitespace()
        return out[0] if len(out) == 1 else DescendantSelector(out)

    def selector_list(self):
        out = [self.selector()]
        self.whitespace()
        while self.i < len(self.s) and self.s[self.i] == ",":
            self.literal(",")
            self.whitespace()
            out.append(self.selector())
            self.whitespace()
        return out

    # -- 미디어 쿼리 ---------------------------------------------------- #

    def media_query(self):
        """(prefers-color-scheme: dark) / (max-width: 400px) 등."""
        self.literal("(")
        self.whitespace()
        prop = self.ident().casefold()
        self.whitespace()
        self.literal(":")
        self.whitespace()
        value = ""
        while self.i < len(self.s) and self.s[self.i] != ")":
            value += self.s[self.i]
            self.i += 1
        self.literal(")")
        return prop, value.strip()

    def skip_block(self):
        """중괄호 한 덩어리를 통째로 건너뛴다."""
        depth = 0
        while self.i < len(self.s):
            if self.s[self.i] == "{":
                depth += 1
            elif self.s[self.i] == "}":
                depth -= 1
                if depth == 0:
                    self.i += 1
                    return
            self.i += 1

    # -- 전체 ----------------------------------------------------------- #

    def parse(self):
        rules = []
        media_stack = []
        while self.i < len(self.s):
            self.whitespace()
            if self.i >= len(self.s):
                break
            if self.s.startswith("/*", self.i):
                end = self.s.find("*/", self.i)
                self.i = len(self.s) if end < 0 else end + 2
                continue
            if self.s.startswith("@media", self.i):
                self.i += len("@media")
                self.whitespace()
                prop, value = self.media_query()
                self.whitespace()
                self.literal("{")
                media_stack.append(media_matches(prop, value, self.media))
                continue
            if self.s.startswith("@keyframes", self.i):
                self.skip_block()        # parse_keyframes 가 따로 읽는다
                continue
            if self.s[self.i] == "}":
                self.literal("}")
                if media_stack:
                    media_stack.pop()
                continue
            try:
                selectors = self.selector_list()
                self.literal("{")
                self.whitespace()
                normal, important = self.body()
                self.literal("}")
                if all(media_stack):
                    for sel in selectors:
                        if normal:
                            rules.append((sel, normal))
                        if important:
                            rules.append((ImportantSelector(sel), important))
            except Exception:
                why = self.ignore_until(["}"])
                if why == "}":
                    self.literal("}")
                else:
                    break
        return rules


def media_matches(prop, value, media):
    """미디어 쿼리 하나가 지금 상태에 맞는가."""
    from wbe.paint.geometry import WIDTH
    if prop == "prefers-color-scheme":
        return media.get("prefers-color-scheme", "light") == value
    if prop == "forced-colors":
        active = media.get("forced-colors", False)
        return active if value == "active" else not active
    if prop == "max-width":
        return media.get("width", WIDTH) <= parse_px_value(value, WIDTH)
    if prop == "min-width":
        return media.get("width", WIDTH) >= parse_px_value(value, 0)
    if prop == "width":
        return media.get("width", WIDTH) == parse_px_value(value, -1)
    return False


# ---------------------------------------------------------------------- #
# @keyframes
# ---------------------------------------------------------------------- #

def parse_keyframes(css_text):
    """`@keyframes 이름 { from {...} to {...} }` 를 이름 -> 정지점으로."""
    out = {}
    i = 0
    text = css_text
    while True:
        at = text.find("@keyframes", i)
        if at < 0:
            return out
        j = text.find("{", at)
        if j < 0:
            return out
        name = text[at + len("@keyframes"):j].strip()
        depth, k = 0, j
        while k < len(text):
            if text[k] == "{":
                depth += 1
            elif text[k] == "}":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        out[name] = parse_keyframe_body(text[j + 1:k])
        i = k + 1


def parse_keyframe_body(body):
    frames = {}
    i = 0
    while True:
        brace = body.find("{", i)
        if brace < 0:
            return frames
        selector = body[i:brace].strip().casefold()
        end = body.find("}", brace)
        if end < 0:
            return frames
        pairs = {}
        for decl in body[brace + 1:end].split(";"):
            if ":" not in decl:
                continue
            prop, _, value = decl.partition(":")
            pairs[prop.strip().casefold()] = value.strip()
        for key in selector.split(","):
            key = key.strip()
            stop = {"from": 0.0, "to": 1.0}.get(key)
            if stop is None and key.endswith("%"):
                try:
                    stop = float(key[:-1]) / 100
                except ValueError:
                    stop = None
            if stop is not None:
                frames[stop] = pairs
        i = end + 1
