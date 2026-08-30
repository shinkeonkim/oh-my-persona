"""테스트 공통 도구."""

import base64
import urllib.parse

import skia

from wbe.a11y import RecordingSpeaker
from wbe.css.parser import CSSParser
from wbe.css.selectors import cascade_priority, prepare_selectors
from wbe.css.style import style
from wbe.dom.nodes import Element, tree_to_list
from wbe.dom.parser import HTMLParser
from wbe.layout.boxes import DocumentLayout
from wbe.net.url import URL
from wbe.paint.commands import flatten
from wbe.paint.effects import paint_tree
from wbe.stylesheets import BROWSER_CSS
from wbe.tab import Tab


def doc_url(html):
    return "data:text/html," + urllib.parse.quote(html)


def data_url(html):
    return URL(doc_url(html))


def png(width=20, height=10, color=skia.ColorRED):
    surface = skia.Surface(width, height)
    with surface as canvas:
        canvas.clear(color)
    return surface.makeImageSnapshot().encodeToData().bytes()


def png_url(width=20, height=10):
    return "data:image/png;base64," + \
        base64.b64encode(png(width, height)).decode()


def make_tab(html, speaker=None, **kwargs):
    tab = Tab(None, 500, speaker=speaker or RecordingSpeaker(), **kwargs)
    tab.load(data_url(html))
    return tab


def styled(html, css="", media=None):
    tree = HTMLParser(html).parse()
    rules = CSSParser(BROWSER_CSS, media).parse()
    if css:
        rules.extend(CSSParser(css, media).parse())
    rules.sort(key=cascade_priority)
    prepare_selectors(rules, tree)
    style(tree, rules)
    return tree


def build(html, css="", media=None):
    doc = DocumentLayout(styled(html, css, media))
    doc.layout()
    cmds = []
    paint_tree(doc, cmds)
    return doc, flatten(cmds)


def find_el(node, tag, out=None):
    out = [] if out is None else out
    if isinstance(node, Element):
        if node.tag == tag:
            out.append(node)
        for c in node.children:
            find_el(c, tag, out)
    return out


def by_id(nodes, name):
    return next(n for n in tree_to_list(nodes)
                if isinstance(n, Element) and n.attributes.get("id") == name)


def of_type(cmds, cls):
    return [c for c in cmds if isinstance(c, cls)]


def texts(cmds):
    from wbe.paint.commands import DrawText
    return [c.text for c in cmds if isinstance(c, DrawText)]


def drawn(tab):
    return [c.text for c in tab.flat_display_list if hasattr(c, "text")]


def layouts(doc, cls):
    from wbe.frame import _layout_objects
    return [o for o in _layout_objects(doc) if isinstance(o, cls)]
