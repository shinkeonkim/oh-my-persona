"""10장 연습문제 구현 (10-1 ~ 10-6).

lab10.py 는 그대로 두고, 1~9장 연습문제를 이어받아 그 위에 10장 기능을 얹는다.
자바스크립트 쪽은 runtime10ex.js 에 있다.

    python3 ex10.py http://localhost:8000/

10장 본문 기능(쿠키, 동일 출처 정책, XMLHttpRequest, CSP)에 더해

    10-1 새로운 입력      hidden 은 자리도 없이, password 는 별표로
    10-2 인증서 오류      잡아서 경고 페이지로, 안전한 곳에는 자물쇠
    10-3 스크립트 접근    document.cookie 와 HttpOnly
    10-4 쿠키 만료        Max-Age / Expires, 서버 세션도 함께
    10-5 CORS           Origin 을 보내고 Access-Control-Allow-Origin 을 본다
    10-6 Referer        Referrer-Policy 를 지킨다
"""

import email.utils
import os
import ssl
import sys
import time
import tkinter

import dukpy

import ex9
from ex1 import MAX_REDIRECTS
from ex4 import Text, Element
from ex6 import style, cascade_priority, tree_to_list
from ex7 import Rect, DrawText, DrawRect, DrawLine, DrawOutline, paint_tree
from ex8 import HEIGHT, form_encode
from ex9 import (HTMLParser, CSSParser, JSContext as JSContext9,
                 DEFAULT_STYLE_SHEET, serialize, serialize_children)

HERE = os.path.dirname(os.path.abspath(__file__))
RUNTIME_JS = open(os.path.join(HERE, "runtime10ex.js"), encoding="utf8").read()

LOCK = "\N{lock}"                       # 연습문제 10-2
PASSWORD_CHAR = "*"                     # 연습문제 10-1

# host -> {name: (value, params)}
COOKIE_JAR = {}

# 연습문제 10-6
REFERRER_POLICIES = {"no-referrer", "same-origin", "no-referrer-when-downgrade"}


class CertificateError(Exception):
    """연습문제 10-2: 인증서를 믿을 수 없다."""


# ---------------------------------------------------------------------- #
# 쿠키
# ---------------------------------------------------------------------- #

def parse_cookie(header):
    """'k=v; SameSite=Lax; HttpOnly' -> (k, v, params)"""
    parts = header.split(";")
    key, _, value = parts[0].strip().partition("=")
    params = {}
    for param in parts[1:]:
        name, _, val = param.strip().partition("=")
        params[name.strip().casefold()] = val.strip()
    return key.strip(), value.strip(), params


def cookie_expiry(params, now=None):
    """연습문제 10-4: Max-Age 가 Expires 보다 우선한다. 없으면 세션 쿠키."""
    now = time.time() if now is None else now
    if "max-age" in params:
        try:
            return now + float(params["max-age"])
        except ValueError:
            return None
    if "expires" in params:
        try:
            return email.utils.parsedate_to_datetime(
                params["expires"]).timestamp()
        except (TypeError, ValueError):
            return None
    return None


def store_cookie(host, header, now=None):
    key, value, params = parse_cookie(header)
    expires = cookie_expiry(params, now)
    if expires is not None:
        params["__expires"] = expires
        if expires <= (time.time() if now is None else now):
            COOKIE_JAR.get(host, {}).pop(key, None)      # 이미 지난 쿠키는 삭제
            return key, value, params
    COOKIE_JAR.setdefault(host, {})[key] = (value, params)
    return key, value, params


def live_cookies(host, now=None):
    """만료된 것은 빼고 돌려준다 (연습문제 10-4)."""
    now = time.time() if now is None else now
    jar = COOKIE_JAR.get(host, {})
    for key in [k for k, (_, p) in jar.items()
                if p.get("__expires") is not None and p["__expires"] <= now]:
        del jar[key]
    return jar


def cookie_header(host, top_level=True, script_visible=False, now=None):
    """보낼 Cookie 헤더 값. 없으면 None."""
    out = []
    for key, (value, params) in live_cookies(host, now).items():
        if not top_level and params.get("samesite", "lax").casefold() == "lax":
            continue                                     # 본문의 SameSite
        if script_visible and "httponly" in params:      # 연습문제 10-3
            continue
        out.append("%s=%s" % (key, value))
    return "; ".join(out) if out else None


# ---------------------------------------------------------------------- #
# URL
# ---------------------------------------------------------------------- #

class URL(ex9.URL):
    def __init__(self, url):
        super().__init__(url)
        self.response_headers = {}

    def origin(self):
        return "{}://{}:{}".format(self.scheme, self.host, self.port)

    def is_secure(self):
        return self.scheme == "https"

    # -- 연습문제 10-6 -------------------------------------------------- #

    def referrer_value(self, referrer, policy):
        if referrer is None:
            return None
        policy = (policy or "no-referrer-when-downgrade").casefold()
        if policy == "no-referrer":
            return None
        if policy == "same-origin" and referrer.origin() != self.origin():
            return None
        if policy == "no-referrer-when-downgrade" \
                and referrer.is_secure() and not self.is_secure():
            return None
        return str(referrer)

    # -- 요청 ----------------------------------------------------------- #

    def request(self, referrer=None, payload=None, redirects_left=MAX_REDIRECTS,
                origin=None, referrer_policy=None, top_level=True):
        self.response_headers = {}
        if self.scheme in ("about", "data", "file"):
            return super().request(None)

        try:
            s = self._connect()
        except ssl.SSLCertVerificationError as e:          # 연습문제 10-2
            raise CertificateError(str(e))
        except ssl.SSLError as e:
            raise CertificateError(str(e))

        s.send(self._bytes(payload, referrer, referrer_policy, origin,
                           top_level))
        response = s.makefile("rb", newline="\r\n")
        _, status, _ = self._read_status(response)
        headers = self._read_headers(response)

        for header in headers.get("set-cookie-all", []):
            store_cookie(self.host, header)

        if 300 <= status < 400 and "location" in headers:
            self._finish(s, headers, body=b"")
            if redirects_left <= 0:
                raise Exception("리다이렉트가 너무 많이 이어집니다")
            nxt = self.resolve(headers["location"])
            return nxt.request(referrer, None, redirects_left - 1,
                               origin, referrer_policy, top_level)

        body = self._read_body(response, headers)
        self._finish(s, headers, body)
        self.response_headers = headers
        return body.decode("utf8", "replace")

    def _read_headers(self, response):
        """Set-Cookie 는 여러 번 올 수 있어서 따로 모은다."""
        out, all_cookies = {}, []
        while True:
            line = response.readline()
            if line in (b"\r\n", b"\n", b""):
                break
            header, _, value = line.decode("utf8").partition(":")
            header = header.casefold()
            value = value.strip()
            if header == "set-cookie":
                all_cookies.append(value)
            out[header] = value
        if all_cookies:
            out["set-cookie-all"] = all_cookies
        return out

    def _bytes(self, payload, referrer, referrer_policy, origin, top_level):
        headers = {
            "Host": self.host,
            "Connection": "keep-alive",
            "User-Agent": "wbe-ko/1.0",
        }
        method = "POST" if payload is not None else "GET"
        data = payload.encode("utf8") if payload is not None else b""
        if payload is not None:
            headers["Content-Length"] = str(len(data))
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        cookie = cookie_header(self.host, top_level=top_level)
        if cookie:
            headers["Cookie"] = cookie
        if origin is not None:                             # 연습문제 10-5
            headers["Origin"] = origin
        ref = self.referrer_value(referrer, referrer_policy)   # 10-6
        if ref:
            headers["Referer"] = ref

        lines = ["{} {} HTTP/1.1".format(method, self.path)]
        lines += ["{}: {}".format(k, v) for k, v in headers.items()]
        return ("\r\n".join(lines) + "\r\n\r\n").encode("utf8") + data


# ---------------------------------------------------------------------- #
# 콘텐츠 보안 정책
# ---------------------------------------------------------------------- #

def parse_csp(header):
    """'default-src http://a http://b' -> ['http://a', 'http://b']"""
    if not header:
        return None
    parts = header.split()
    if len(parts) < 2 or parts[0].casefold() != "default-src":
        return None
    return parts[1:]


# ---------------------------------------------------------------------- #
# 입력 요소 (연습문제 10-1)
# ---------------------------------------------------------------------- #

def input_type(node):
    return node.attributes.get("type", "text").casefold()


def is_hidden(node):
    return input_type(node) == "hidden"


def display_value(node):
    """화면에 보일 글자. password 는 별표."""
    value = node.attributes.get("value", "")
    if input_type(node) == "password":
        return PASSWORD_CHAR * len(value)
    return value


class InputLayout(ex9.ex8.InputLayout):
    def is_hidden(self):
        return is_hidden(self.node)

    def layout(self):
        if self.is_hidden():
            self.width = self.height = 0        # 자리를 차지하지 않는다
            if self.previous:
                space = self.previous.font.measure(" ") \
                    if self.previous.space else 0
                self.x = self.previous.x + space + self.previous.width
            else:
                self.x = self.parent.x
            return
        super().layout()

    def ascent(self):
        return 0 if self.is_hidden() else super().ascent()

    def paint(self):
        if self.is_hidden():
            return []
        if self.is_checkbox():
            return super().paint()
        cmds = []
        bg = self.node.style.get("background-color", "transparent")
        if bg != "transparent":
            cmds.append(DrawRect(self.self_rect(), bg, self.node))
        text = display_value(self.node)                  # 연습문제 10-1
        if self.node.is_focused:
            cx = self.x + self.font.measure(text)
            cmds.append(DrawLine(cx, self.y, cx, self.y + self.height,
                                 "black", 1, self.node))
        if text:
            cmds.append(DrawText(self.x, self.y, text, self.font,
                                 self.node.style["color"], self.node))
        return cmds


class BlockLayout(ex9.ex8.BlockLayout):
    def input(self, node):
        font = self.font_for(node)
        if is_hidden(node):
            line = self.children[-1]
            previous = line.children[-1] if line.children else None
            line.children.append(InputLayout(node, line, previous, font))
            return
        width = ex9.ex8.CHECKBOX_SIZE if input_type(node) == "checkbox" \
            else ex9.ex8.INPUT_WIDTH_PX
        if self.cursor_x + width > self.width:
            self.new_line()
        line = self.children[-1]
        previous = line.children[-1] if line.children else None
        line.children.append(InputLayout(node, line, previous, font))
        self.cursor_x += width + font.measure(" ")

    def layout(self):
        # 자식 BlockLayout 도 10장의 것이어야 한다
        indent = self.list_indent()
        self.x = self.parent.x + indent
        css_width = ex9.ex8.parse_px(self.style_of("width", "auto"))
        self.width = css_width if css_width is not None \
            else self.parent.width - indent
        self.y = (self.previous.y + self.previous.height
                  if self.previous else self.parent.content_top())

        mode = self.layout_mode()
        if mode == "block":
            previous = None
            for group in ex9.ex8.group_children(self.node):
                child = BlockLayout(group, self, previous)
                self.children.append(child)
                previous = child
            for child in self.children:
                child.layout()
        else:
            self.centered = self.superscript = False
            self.smallcaps = self.pre = False
            self.new_line()
            for node in self.nodes:
                if self.skip_self and node is self.node \
                        and isinstance(node, Element):
                    for child in node.children:
                        self.recurse(child)
                else:
                    self.recurse(node)
            for line in self.children:
                line.layout()

        css_height = ex9.ex8.parse_px(self.style_of("height", "auto"))
        if css_height is not None:
            self.height = css_height
        else:
            self.height = self.toc_label_height() + \
                sum(c.height for c in self.children)


class DocumentLayout(ex9.ex8.DocumentLayout):
    def layout(self):
        self.width = ex9.ex8.WIDTH - 2 * ex9.ex8.HSTEP
        self.x, self.y = ex9.ex8.HSTEP, ex9.ex8.VSTEP
        child = BlockLayout([self.node], self, None)
        self.children.append(child)
        child.layout()
        self.height = child.height


# ---------------------------------------------------------------------- #
# 자바스크립트
# ---------------------------------------------------------------------- #

class JSContext(JSContext9):
    def __init__(self, tab):
        self.tab = tab
        self.node_to_handle = {}
        self.handle_to_node = {}
        self.id_globals = {}
        self.discarded = False

        self.interp = dukpy.JSInterpreter()
        for name in ("log", "querySelectorAll", "getAttribute", "setAttribute",
                     "innerHTML_get", "innerHTML_set", "outerHTML_get",
                     "getChildren", "getParent", "ancestors",
                     "createElement", "createTextNode",
                     "appendChild", "insertBefore", "removeChild",
                     "XMLHttpRequest_send", "cookie_get", "cookie_set"):
            self.interp.export_function(name, getattr(self, name))
        self.interp.evaljs(RUNTIME_JS + "\n0;")

    # -- 연습문제 10-3 -------------------------------------------------- #

    def cookie_get(self):
        return cookie_header(self.tab.url.host, script_visible=True) or ""

    def cookie_set(self, text):
        store_cookie(self.tab.url.host, text)
        return text

    # -- XMLHttpRequest ------------------------------------------------- #

    def XMLHttpRequest_send(self, method, url, body):
        full_url = self.tab.url.resolve(url)
        cross_origin = full_url.origin() != self.tab.url.origin()
        if not self.tab.allowed_request(full_url):
            raise Exception("콘텐츠 보안 정책이 %s 를 막았습니다" % full_url)

        origin = self.tab.url.origin() if cross_origin else None
        out = full_url.request(referrer=self.tab.url,
                               payload=body if method.upper() == "POST" else None,
                               origin=origin,
                               referrer_policy=self.tab.referrer_policy,
                               top_level=not cross_origin)
        if cross_origin:
            # 연습문제 10-5: 서버가 허락해야만 결과를 넘겨준다
            allow = full_url.response_headers.get(
                "access-control-allow-origin", "")
            if allow not in ("*", self.tab.url.origin()):
                raise Exception("교차 출처 요청이 허용되지 않았습니다")
        return out


# ---------------------------------------------------------------------- #
# 탭
# ---------------------------------------------------------------------- #

WARNING_PAGE = ("<!doctype html><html><head><title>안전하지 않은 연결</title>"
                "</head><body><h1>이 사이트의 인증서를 믿을 수 없습니다</h1>"
                "<p>{}</p><p>{}</p></body></html>")


class Tab(ex9.Tab):
    def __init__(self, tab_height):
        super().__init__(tab_height)
        self.allowed_origins = None       # CSP
        self.referrer_policy = None       # 연습문제 10-6
        self.insecure = False             # 연습문제 10-2

    def allowed_request(self, url):
        return self.allowed_origins is None \
            or url.origin() in self.allowed_origins

    def load(self, url, payload=None, record=True):
        self.insecure = False
        referrer = self.url if self.url is not None else None
        try:
            body = url.request(referrer=referrer, payload=payload,
                               referrer_policy=self.referrer_policy)
        except CertificateError as e:                    # 연습문제 10-2
            body = WARNING_PAGE.format(ex9.escape_text(str(url)),
                                       ex9.escape_text(str(e)))
            self.insecure = True
            url.response_headers = {}

        self.url = url
        self.focus = None
        if record:
            self.history.visit(url,
                               "POST" if payload is not None else "GET",
                               payload)
        ex9.ex8.VISITED.add(ex9.ex8.base_str(url))

        headers = getattr(url, "response_headers", {}) or {}
        self.allowed_origins = parse_csp(
            headers.get("content-security-policy"))
        policy = headers.get("referrer-policy", "").casefold()
        self.referrer_policy = policy if policy in REFERRER_POLICIES else None

        self.nodes = HTMLParser(body).parse()
        for node in tree_to_list(self.nodes, []):
            if isinstance(node, Element):
                node.is_focused = False

        self.base_rules = DEFAULT_STYLE_SHEET.copy()
        self.link_rules = {}
        for node in tree_to_list(self.nodes, []):
            if isinstance(node, Element) and node.tag == "style":
                text = "".join(c.text for c in node.children
                               if isinstance(c, Text))
                self.base_rules.extend(CSSParser(text).parse())

        self.mark_visited_links()
        self.js = JSContext(self)

        for node in tree_to_list(self.nodes, []):
            if not isinstance(node, Element):
                continue
            if node.tag == "link" and "href" in node.attributes \
                    and node.attributes.get("rel") == "stylesheet":
                self.add_stylesheet(node, restyle=False)

        self.restyle()
        self.js.update_id_globals()

        for node in tree_to_list(self.nodes, []):
            if isinstance(node, Element) and node.tag == "script":
                self.run_script(node)

        self.scroll = 0
        if url.fragment:
            self.scroll_to(url.fragment)

    def render(self):
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)

    def sub_request(self, url):
        """스크립트·스타일시트 같은 딸린 자원 하나 가져오기."""
        if not self.allowed_request(url):
            print("콘텐츠 보안 정책이", url, "를 막았습니다")
            return None
        try:
            return url.request(referrer=self.url,
                               referrer_policy=self.referrer_policy)
        except Exception:
            return None

    def run_script(self, node):
        src = node.attributes.get("src")
        if src:
            code = self.sub_request(self.url.resolve(src))
            if code is None:
                return
        else:
            code = "".join(c.text for c in node.children
                           if isinstance(c, Text))
        if code.strip():
            self.js.run(src or "인라인 스크립트", code)

    def add_stylesheet(self, node, restyle=True):
        body = self.sub_request(self.url.resolve(node.attributes["href"]))
        if body is None:
            return
        self.link_rules[node] = CSSParser(body).parse()
        if restyle:
            self.restyle()

    def keypress(self, char):
        if self.focus is None:
            return False
        if self.js is not None and \
                self.js.dispatch_event("keydown", self.focus):
            return True
        self.focus.attributes["value"] = \
            self.focus.attributes.get("value", "") + char
        self.render()
        return True


# ---------------------------------------------------------------------- #
# 크롬 — 자물쇠 (연습문제 10-2)
# ---------------------------------------------------------------------- #

class HTMLChrome(ex9.HTMLChrome):
    def html(self):
        out = super().html()
        tab = self.browser.active_tab
        if tab is None or tab.url is None:
            return out
        if tab.url.is_secure() and not tab.insecure:
            mark = '<span id="lock">%s</span> ' % LOCK
        elif tab.insecure:
            mark = '<span id="lock">!</span> '
        else:
            mark = ""
        return out.replace('<input id="address"', mark + '<input id="address"')


class Browser(ex9.Browser):
    def __init__(self, root=None):
        super().__init__(root)
        self.chrome = HTMLChrome(self)

    def new_tab(self, url, background=False):
        tab = Tab(HEIGHT - self.chrome.bottom)
        tab.load(url)
        self.tabs.append(tab)
        if not background or self.active_tab is None:
            self.active_tab = tab
        self.chrome.render()
        self.draw()
        return tab


def main(argv):
    browser = Browser()
    browser.new_tab(URL(argv[0]) if argv else URL(ex9.ex8.HOME_URL))
    tkinter.mainloop()


if __name__ == "__main__":
    main(sys.argv[1:])
