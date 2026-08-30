"""문서 트리를 HTML 소스로 되돌린다.

`innerHTML` 을 읽을 때 쓴다. 원문이 아니라 **현재 속성**을 적으므로,
스크립트가 바꾼 값이 그대로 나온다.
"""

from wbe.dom.nodes import Element, Text

# 닫는 태그를 붙이지 않는 태그들
SELF_CLOSING = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


def escape_text(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def escape_attr(value):
    return (value.replace("&", "&amp;").replace('"', "&quot;")
            .replace("<", "&lt;").replace(">", "&gt;"))


def serialize(node):
    if isinstance(node, Text):
        return escape_text(node.text)
    out = "<" + node.tag
    for name, value in node.attributes.items():
        out += " " + name if value == "" \
            else ' %s="%s"' % (name, escape_attr(value))
    out += ">"
    if node.tag in SELF_CLOSING:
        return out
    return out + serialize_children(node) + "</%s>" % node.tag


def serialize_children(node):
    return "".join(serialize(child) for child in node.children)
