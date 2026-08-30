"""9장 연습문제 구현 (9-1 ~ 9-7).

lab9.py 는 그대로 두고, 1~8장 연습문제를 이어받아 그 위에 9장 기능을 얹는다.
자바스크립트 쪽은 runtime9ex.js 에 있다.

    python3 ex9.py http://localhost:8000/

구현한 연습문제
    9-1  Node.children      직계 Element 자식만
    9-2  createElement      appendChild / insertBefore 와 함께
    9-3  removeChild        떼어 낸 서브트리를 돌려준다
    9-4  ID                 id 를 가진 요소는 같은 이름의 전역 변수
    9-5  이벤트 버블링        대상에서 조상으로, stopPropagation 으로 멈춤
    9-6  HTML 직렬화         innerHTML 을 읽으면 현재 속성이 반영된 소스
    9-7  스크립트가 추가한 스크립트와 스타일 시트
"""

import os
import re
import sys
import tkinter

import dukpy

import ex8
from ex1 import decode_entities
from ex4 import HTMLParser as BaseHTMLParser, Text, Element
from ex6 import (CSSParser as BaseCSSParser, style, cascade_priority,
                 tree_to_list, ClassSelector, TagSelector, SelectorSequence,
                 HasSelector)
from ex7 import paint_tree
from ex8 import (URL, Browser, HEIGHT, form_encode, HTMLChrome,
                 BROWSER_CSS, EXTRA_CSS)

HERE = os.path.dirname(os.path.abspath(__file__))
RUNTIME_JS = open(os.path.join(HERE, "runtime9ex.js"), encoding="utf8").read()



# 스스로 닫는 태그는 직렬화할 때 닫는 태그를 붙이지 않는다 (연습문제 9-6)
SELF_CLOSING = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

IDENTIFIER = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*$")
RESERVED = {
    "break", "case", "catch", "class", "const", "continue", "debugger",
    "default", "delete", "do", "else", "export", "extends", "finally",
    "for", "function", "if", "import", "in", "instanceof", "new", "return",
    "super", "switch", "this", "throw", "try", "typeof", "var", "void",
    "while", "with", "yield", "let", "static", "enum", "await", "implements",
    "package", "protected", "interface", "private", "public", "null", "true",
    "false", "document", "console", "window", "Node", "Event", "LISTENERS",
}


class HTMLParser(BaseHTMLParser):
    """글자 마디에 진짜 문자를 담는다.

    9-6 이 있기 전에는 &lt; 를 원문 그대로 들고 있어도 티가 안 났지만,
    innerHTML 로 읽어 다시 쓰면 &amp;lt; 가 되어 버린다. DOM 은 원문이 아니라
    문자를 담아야 하고, 직렬화가 그것을 다시 실체 참조로 바꾼다.
    """

    def handle_text(self, text, raw=False):
        self.add_text(text if raw else decode_entities(text))


class IdSelector:
    """#id. 9-4 로 id 가 자바스크립트에서 이름이 되니, 선택자로도 쓸 수 있어야
    querySelectorAll 이 쓸모 있다. 우선순위는 클래스보다 높다."""

    def __init__(self, id_):
        self.id = id_
        self.priority = 100

    def matches(self, node):
        return isinstance(node, Element) \
            and node.attributes.get("id") == self.id

    def __repr__(self):
        return "#" + self.id


class CSSParser(BaseCSSParser):
    def ident(self):
        """'#' 을 이름에 섞지 않는다. 앞에 붙는 표시로 쓰기 때문이다."""
        start = self.i
        while self.i < len(self.s):
            if self.s[self.i].isalnum() or self.s[self.i] in "-_":
                self.i += 1
            else:
                break
        if self.i == start:
            raise Exception("파싱 실패: 이름을 기대했습니다")
        return self.s[start:self.i]

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
        return base


# 9장의 CSSParser 로 다시 읽는다 (#id 선택자를 알아듣도록)
DEFAULT_STYLE_SHEET = CSSParser(BROWSER_CSS + EXTRA_CSS).parse()


def escape_attr(value):
    return (value.replace("&", "&amp;").replace('"', "&quot;")
            .replace("<", "&lt;").replace(">", "&gt;"))


def escape_text(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def serialize(node):
    """연습문제 9-6: 노드 하나를 HTML 소스로."""
    if isinstance(node, Text):
        return escape_text(node.text)
    out = "<" + node.tag
    for name, value in node.attributes.items():
        if value == "":
            out += " " + name
        else:
            out += ' %s="%s"' % (name, escape_attr(value))
    out += ">"
    if node.tag in SELF_CLOSING:
        return out
    out += serialize_children(node)
    return out + "</%s>" % node.tag


def serialize_children(node):
    return "".join(serialize(child) for child in node.children)


class JSContext:
    def __init__(self, tab):
        self.tab = tab
        self.node_to_handle = {}
        self.handle_to_node = {}
        self.id_globals = {}          # 연습문제 9-4
        self.discarded = False

        self.interp = dukpy.JSInterpreter()
        for name in ("log", "querySelectorAll", "getAttribute", "setAttribute",
                     "innerHTML_set", "innerHTML_get", "outerHTML_get",
                     "getChildren", "getParent", "ancestors",
                     "createElement", "createTextNode",
                     "appendChild", "insertBefore", "removeChild"):
            self.interp.export_function(name, getattr(self, name))
        # 마지막 문장이 함수이면 dukpy 가 값을 돌려주지 못하므로 0 으로 끝낸다
        self.interp.evaljs(RUNTIME_JS + "\n0;")

    # -- 실행 ---------------------------------------------------------- #

    def run(self, script, code):
        # 마지막 문장의 값은 쓰지 않는다. 그 값을 돌려받으려 하면
        # x.onload = function(){...} 처럼 함수로 끝나는 흔한 스크립트가
        # 멀쩡히 실행되고도 "직렬화할 수 없다"는 오류로 보고된다.
        try:
            return self.interp.evaljs(code + "\n0;")
        except dukpy.JSRuntimeError as e:
            print("스크립트", script, "가 죽었습니다:", e)

    def log(self, *args):
        print(*args)

    # -- 핸들 ---------------------------------------------------------- #

    def get_handle(self, elt):
        if elt not in self.node_to_handle:
            handle = len(self.node_to_handle)
            self.node_to_handle[elt] = handle
            self.handle_to_node[handle] = elt
        return self.node_to_handle[elt]

    def node(self, handle):
        return self.handle_to_node[handle]

    # -- 조회 ---------------------------------------------------------- #

    def querySelectorAll(self, selector_text):
        selector = CSSParser(selector_text).selector()
        if hasattr(selector, "prepare"):
            selector.prepare(self.tab.nodes)          # 6-10 의 :has
        return [self.get_handle(node)
                for node in tree_to_list(self.tab.nodes, [])
                if selector.matches(node)]

    def getAttribute(self, handle, attr):
        return self.node(handle).attributes.get(attr, "") or ""

    def setAttribute(self, handle, attr, value):
        self.node(handle).attributes[attr] = value
        self.changed()
        return value

    def getChildren(self, handle):
        """연습문제 9-1: Text 는 빼고 Element 만."""
        return [self.get_handle(child)
                for child in self.node(handle).children
                if isinstance(child, Element)]

    def getParent(self, handle):
        parent = self.node(handle).parent
        return self.get_handle(parent) if parent is not None else -1

    def ancestors(self, handle):
        """연습문제 9-5: 대상부터 뿌리까지."""
        out, node = [], self.node(handle)
        while node is not None:
            out.append(self.get_handle(node))
            node = node.parent
        return out

    # -- 만들기와 붙이기 (연습문제 9-2, 9-3) ---------------------------- #

    def createElement(self, tag):
        return self.get_handle(Element(tag.casefold(), {}, None))

    def createTextNode(self, text):
        return self.get_handle(Text(text, None))

    def detach(self, node):
        if node.parent is not None and node in node.parent.children:
            node.parent.children.remove(node)
        node.parent = None

    def appendChild(self, parent_handle, child_handle):
        parent = self.node(parent_handle)
        child = self.node(child_handle)
        self.detach(child)
        parent.children.append(child)
        child.parent = parent
        self.attach_resources(child)
        self.changed()
        return child_handle

    def insertBefore(self, parent_handle, child_handle, ref_handle):
        parent = self.node(parent_handle)
        child = self.node(child_handle)
        self.detach(child)
        if ref_handle is None or ref_handle < 0:
            parent.children.append(child)
        else:
            ref = self.node(ref_handle)
            parent.children.insert(parent.children.index(ref), child)
        child.parent = parent
        self.attach_resources(child)
        self.changed()
        return child_handle

    def removeChild(self, parent_handle, child_handle):
        """연습문제 9-3: 떼어 내면 그 서브트리는 문서 밖으로 나간다."""
        parent = self.node(parent_handle)
        child = self.node(child_handle)
        if child.parent is not parent:
            raise Exception("removeChild: 자식이 아닙니다")
        self.detach_resources(child)
        parent.children.remove(child)
        child.parent = None
        self.changed()
        return child_handle

    # -- innerHTML ----------------------------------------------------- #

    def innerHTML_get(self, handle):
        return serialize_children(self.node(handle))     # 연습문제 9-6

    def outerHTML_get(self, handle):
        return serialize(self.node(handle))

    def innerHTML_set(self, handle, s):
        elt = self.node(handle)
        for child in elt.children:
            self.detach_resources(child)                 # 연습문제 9-7
        doc = HTMLParser("<html><body>" + s + "</body></html>").parse()
        new_nodes = doc.children[0].children
        elt.children = new_nodes
        for child in elt.children:
            child.parent = elt
            self.attach_resources(child)
        self.changed()

    # -- 연습문제 9-7 --------------------------------------------------- #

    def attach_resources(self, subtree):
        """새로 들어온 <script> 는 돌리고 <link> 는 읽어 온다."""
        for node in tree_to_list(subtree, []):
            if not isinstance(node, Element):
                continue
            if node.tag == "script":
                self.tab.run_script(node)
            elif node.tag == "link" and "href" in node.attributes \
                    and node.attributes.get("rel") == "stylesheet":
                self.tab.add_stylesheet(node)

    def detach_resources(self, subtree):
        """빠져나간 <link> 의 규칙은 목록에서 뺀다."""
        for node in tree_to_list(subtree, []):
            if isinstance(node, Element) and node.tag == "link":
                self.tab.remove_stylesheet(node)

    # -- 연습문제 9-4: id 전역 변수 ------------------------------------- #

    def usable_id(self, name):
        return bool(IDENTIFIER.match(name)) and name not in RESERVED

    def update_id_globals(self):
        current = {}
        for node in tree_to_list(self.tab.nodes, []):
            if not isinstance(node, Element):
                continue
            name = node.attributes.get("id")
            if name and self.usable_id(name) and name not in current:
                current[name] = self.get_handle(node)

        for name in list(self.id_globals):
            if name not in current:
                self.interp.evaljs("delete this[dukpy.name];", name=name)
                del self.id_globals[name]
        for name, handle in current.items():
            if self.id_globals.get(name) != handle:
                self.interp.evaljs(
                    "this[dukpy.name] = new Node(dukpy.handle);",
                    name=name, handle=handle)
                self.id_globals[name] = handle

    def changed(self):
        """DOM 이 바뀌었다. id 전역 변수를 맞추고 다시 그린다."""
        self.update_id_globals()
        self.tab.restyle()

    # -- 이벤트 -------------------------------------------------------- #

    def dispatch_event(self, type, elt):
        """연습문제 9-5: 대상에서 조상 순서로 핸들러를 부른다."""
        handles = self.ancestors(self.get_handle(elt))
        do_default = self.interp.evaljs(
            "__dispatch(dukpy.handles, dukpy.type)",
            handles=handles, type=type)
        return not do_default


# ---------------------------------------------------------------------- #
# 탭
# ---------------------------------------------------------------------- #

class Tab(ex8.Tab):
    def __init__(self, tab_height):
        super().__init__(tab_height)
        self.js = None
        self.base_rules = []
        self.link_rules = {}          # link 노드 -> 그 스타일시트의 규칙들

    def load(self, url, payload=None, record=True):
        body = url.request(payload)
        self.url = url
        self.focus = None
        if record:
            self.history.visit(url,
                               "POST" if payload is not None else "GET",
                               payload)
        ex8.VISITED.add(ex8.base_str(url))
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
        self.js.update_id_globals()          # 연습문제 9-4

        for node in tree_to_list(self.nodes, []):
            if isinstance(node, Element) and node.tag == "script":
                self.run_script(node)

        self.scroll = 0
        if url.fragment:
            self.scroll_to(url.fragment)

    # -- 자원 ---------------------------------------------------------- #

    def run_script(self, node):
        src = node.attributes.get("src")
        if src:
            try:
                code = self.url.resolve(src).request()
            except Exception:
                return
        else:
            code = "".join(c.text for c in node.children
                           if isinstance(c, Text))
        if code.strip():
            self.js.run(src or "인라인 스크립트", code)

    def add_stylesheet(self, node, restyle=True):
        try:
            body = self.url.resolve(node.attributes["href"]).request()
        except Exception:
            return
        self.link_rules[node] = CSSParser(body).parse()
        if restyle:
            self.restyle()

    def remove_stylesheet(self, node):
        if self.link_rules.pop(node, None) is not None:
            self.restyle()

    def all_rules(self):
        rules = list(self.base_rules)
        for extra in self.link_rules.values():
            rules.extend(extra)
        return sorted(rules, key=cascade_priority)

    def restyle(self):
        for node in tree_to_list(self.nodes, []):
            if isinstance(node, Element) and not hasattr(node, "is_focused"):
                node.is_focused = False
        style(self.nodes, self.all_rules())
        self.render()

    # -- 상호작용 ------------------------------------------------------ #

    def click(self, x, y):
        self.blur()
        node = self.node_at(x, y)
        if node is None:
            return None
        target = node if isinstance(node, Element) else node.parent
        if target is not None and self.js is not None:
            if self.js.dispatch_event("click", target):
                return None          # preventDefault
        while node is not None:
            if isinstance(node, Text):
                pass
            elif node.tag == "a" and "href" in node.attributes:
                return self.follow(self.url.resolve(node.attributes["href"]))
            elif node.tag == "input":
                type_ = node.attributes.get("type", "text").casefold()
                if type_ == "checkbox":
                    if "checked" in node.attributes:
                        del node.attributes["checked"]
                    else:
                        node.attributes["checked"] = ""
                else:
                    self.focus_on(node)
                    node.attributes["value"] = ""
                self.render()
                return None
            elif node.tag == "button":
                return self.submit_form(node)
            node = node.parent
        return None

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

    def submit_form(self, node):
        form = self.form_for(node)
        if form is None:
            return None
        if self.js is not None and self.js.dispatch_event("submit", form):
            return None
        body = form_encode(self.form_pairs(form))
        url = self.url.resolve(form.attributes["action"])
        method = form.attributes.get("method", "post").casefold()
        if method == "get":
            target = url.with_query(body)
            self.load(target)
            return target
        self.load(url, payload=body)
        return url


class Browser(ex8.Browser):
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
    browser.new_tab(URL(argv[0]) if argv else URL(ex8.HOME_URL))
    tkinter.mainloop()


if __name__ == "__main__":
    main(sys.argv[1:])
