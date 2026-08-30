"""문서 트리의 마디.

`Text` 는 글자, `Element` 는 태그다. 두 마디 모두 `children` 과 `parent` 를
들고 있어서 트리를 위아래로 오갈 수 있다.
"""

ENTITIES = {
    "&lt;": "<",
    "&gt;": ">",
    "&amp;": "&",
    "&quot;": '"',
    "&#39;": "'",
}


def decode_entities(text):
    for entity, char in ENTITIES.items():
        text = text.replace(entity, char)
    return text


class Text:
    def __init__(self, text, parent):
        self.text = text
        self.children = []
        self.parent = parent
        # 스타일·무효화가 쓰는 자리
        self.style = {}
        self.animations = {}
        self.needs_style = True
        self.has_dirty_style_descendants = True

    def __repr__(self):
        return "Text(%r)" % self.text


class Element:
    def __init__(self, tag, attributes, parent):
        self.tag = tag
        self.attributes = attributes
        self.children = []
        self.parent = parent
        self.style = {}
        self.animations = {}
        self.needs_style = True
        self.has_dirty_style_descendants = True
        # 상호작용 상태
        self.is_focused = False
        self.is_hovered = False
        self.focus_visible = False
        # 끼워 넣는 것들이 채운다
        self.image = None
        self.background_image = None
        self.canvas_context = None
        self.frame = None

    def __repr__(self):
        return "<%s>" % self.tag


def tree_to_list(tree, out=None):
    out = [] if out is None else out
    out.append(tree)
    for child in tree.children:
        tree_to_list(child, out)
    return out


def print_tree(node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)


def is_descendant(node, ancestor):
    while node is not None:
        if node is ancestor:
            return True
        node = node.parent
    return False


def inner_text(node):
    return " ".join(n.text for n in tree_to_list(node)
                    if isinstance(n, Text)).strip()
