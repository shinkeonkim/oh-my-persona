# HTML 트리 구성하기

*Constructing an HTML Tree*

[웹 브라우저 엔지니어링](https://browser.engineering/index.html)의 4장 · [원문](https://browser.engineering/html.html)

← 이전: [텍스트 서식 지정하기](https://browser.engineering/text.html) · 다음: [페이지 배치하기](https://browser.engineering/layout.html) →

[![웹 브라우저 엔지니어링 표지](cover.jpg)](https://global.oup.com/academic/product/web-browser-engineering-9780198913863)

> _웹 브라우저 엔지니어링_이 출간되었습니다. [책 구매하기 »](https://global.oup.com/academic/product/web-browser-engineering-9780198913863)

## 목차

- [노드의 트리](#노드의-트리)
- [트리 구성하기](#트리-구성하기)
- [파서 디버깅하기](#파서-디버깅하기)
- [자체 닫힘 태그](#자체-닫힘-태그)
- [노드 트리 사용하기](#노드-트리-사용하기)
- [작성자의 실수 처리하기](#작성자의-실수-처리하기)
- [요약](#요약)
- [개요](#개요)
- [연습문제](#연습문제)
- [각주](#각주)

---

지금까지 우리 브라우저는 웹 페이지를 여는 태그, 닫는 태그, 텍스트의 흐름으로 봅니다. 하지만 HTML은 사실 트리이며, 아직은 트리 구조가 중요하지 않았지만 앞으로 CSS, JavaScript, 시각 효과 같은 기능에서는 핵심이 될 것입니다. 그래서 이 장에서는 제대로 된 HTML 파서를 추가하고 레이아웃 엔진이 그것을 사용하도록 바꾸겠습니다.

## 노드의 트리

HTML 트리[^1]에는 여는 태그와 닫는 태그의 쌍마다 노드 하나가 있고, 연속된 텍스트마다 노드 하나가 있습니다.[^2] 그 구조를 보여 주는 간단한 HTML 문서가 그림 1에 있습니다.

![그림 1: 태그, 텍스트, 중첩 구조를 보여 주는 HTML 문서.](html-syntax.png)

*그림 1: 태그, 텍스트, 중첩 구조를 보여 주는 HTML 문서.*

우리 브라우저가 트리를 사용하려면 토큰이 노드로 진화해야 합니다. 즉 각 토큰에 자식 목록과 부모 포인터를 추가해야 한다는 뜻입니다. 다음은 트리의 잎에 해당하는 텍스트를 나타내는 새로운 `Text` 클래스입니다.

```python
class Text:
    def __init__(self, text, parent):
        self.text = text
        self.children = []
        self.parent = parent
```

노드 하나를 만드는 데 태그 두 개(여는 태그와 닫는 태그)가 필요하므로, `Tag` 클래스의 이름을 `Element`로 바꾸고 다음과 같이 만듭시다.

```python
class Element:
    def __init__(self, tag, parent):
        self.tag = tag
        self.children = []
        self.parent = parent
```

일관성을 위해 텍스트 노드에는 자식이 없는데도 `Text`와 `Element` 양쪽에 `children` 필드를 추가했습니다.

소스 코드로부터 노드의 트리를 구성하는 것을 파싱이라고 합니다. 파서는 한 번에 요소나 텍스트 노드 하나씩 트리를 만들어 갑니다. 그런데 그 말은 파서가 진행하는 동안 _미완성_ 트리를 저장해야 한다는 뜻입니다. 예를 들어 파서가 지금까지 다음과 같은 HTML 조각을 읽었다고 합시다.

```
<html><video></video><section><h1>This is my webpage
```

파서는 태그 다섯 개(그리고 텍스트 노드 하나)를 보았습니다. 남은 HTML에는 여는 태그, 닫는 태그, 텍스트가 더 있겠지만, 어떤 토큰을 만나든 이미 닫힌 `<video>` 태그에는 새 노드가 추가되지 않습니다. 그러니 그 노드는 "완성"된 것입니다. 하지만 다른 노드들은 미완성입니다. 뒤에 어떤 HTML이 오느냐에 따라 `<html>`, `<section>`, `<h1>` 노드에는 자식이 더 추가될 수 있습니다. 그림 2를 보세요.

![그림 2: HTML을 파싱하는 동안의 완성된 노드와 미완성 노드.](html-lr-2.gif)

*그림 2: HTML을 파싱하는 동안의 완성된 노드와 미완성 노드.*

파서는 HTML 파일을 처음부터 끝까지 읽으므로, 이 미완성 태그들은 항상 트리의 특정 부분에 있습니다. 미완성 태그는 항상 _열렸지만_ 아직 닫히지 않았고, 항상 완성된 노드보다 _소스에서 뒤쪽에_ 있으며, 항상 _다른 미완성 태그의 자식_ 입니다. 이 사실들을 활용하기 위해, 미완성 트리를 미완성 태그들의 리스트로 표현하되 부모가 자식보다 앞에 오도록 정렬해 저장합시다. 리스트의 첫 번째 노드는 HTML 트리의 루트이고, 마지막 노드는 가장 최근의 미완성 태그입니다.[^3]

파싱은 `lex`보다 조금 복잡하므로 여러 함수로 나누어 새로운 `HTMLParser` 클래스로 정리하겠습니다. 이 클래스는 분석 중인 소스 코드와 미완성 트리도 함께 저장할 수 있습니다.

```python
class HTMLParser:
    def __init__(self, body):
        self.body = body
        self.unfinished = []
```

파서가 시작하기 전에는 아무 태그도 보지 못했으므로, 트리를 저장하는 `unfinished` 리스트는 비어 있는 상태로 시작합니다. 하지만 파서가 토큰을 읽어 감에 따라 그 리스트가 채워집니다. 우선 지금 있는 `lex` 함수의 이름을 포부를 담아 `parse`로 바꾸는 것부터 시작합시다.

```python
class HTMLParser:
    def parse(self):
        # ...
```

`parse`를 조금 손봐야 합니다. 지금 `parse`는 `Tag`와 `Text` 객체를 만들어 `out` 배열에 덧붙입니다. 우리는 이것이 `Element`와 `Text` 객체를 만들어 `unfinished` 트리에 추가하기를 원합니다. 트리는 리스트보다 조금 복잡하므로, 트리에 추가하는 로직은 `add_text`와 `add_tag`라는 새 메서드 두 개로 옮기겠습니다.

```python
def parse(self):
    text = ""
    in_tag = False
    for c in self.body:
        if c == "<":
            in_tag = True
            if text: self.add_text(text)
            text = ""
        elif c == ">":
            in_tag = False
            self.add_tag(text)
            text = ""
        else:
            text += c
    if not in_tag and text:
        self.add_text(text)
    return self.finish()
```

`out` 변수가 사라졌고, 반환값도 새로운 `finish` 메서드로 옮겼다는 점에 주의하세요. 이 메서드는 미완성 트리를 최종적인 완성 트리로 변환합니다. 그렇다면 트리에는 어떻게 무언가를 추가할까요?

### 더 알아보기

HTML은 오랜 계보를 지닌 문서 처리 시스템에서 유래했습니다. 그 전신인 [SGML](https://en.wikipedia.org/wiki/Standard_Generalized_Markup_Language)은 [RUNOFF](https://en.wikipedia.org/wiki/TYPSET_and_RUNOFF)까지 거슬러 올라가며, 지금 Linux 매뉴얼 페이지에 쓰이는 [troff](https://troff.org)와 형제 관계입니다. SGML을 표준화한 [위원회](https://www.iso.org/committee/45374.html)는 지금 `.odf`, `.docx`, `.epub` 형식을 다루고 있습니다.

## 트리 구성하기

트리에 노드를 추가하는 이야기를 해 봅시다. 텍스트 노드를 추가하려면 마지막 미완성 노드의 자식으로 추가합니다.

```python
class HTMLParser:
    def add_text(self, text):
        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)
```

반면 태그는 여는 태그일 수도 _있고_ 닫는 태그일 수도 있으므로 조금 더 복잡합니다.

```python
class HTMLParser:
    def add_tag(self, tag):
        if tag.startswith("/"):
            # ...
        else:
            # ...
```

여는 태그는 리스트 끝에 미완성 노드를 추가합니다.

```python
def add_tag(self, tag):
    # ...
    else:
        parent = self.unfinished[-1]
        node = Element(tag, parent)
        self.unfinished.append(node)
```

반대로 닫는 태그는 마지막 미완성 노드를 리스트의 이전 미완성 노드에 추가함으로써 그것을 완성합니다.

```python
def add_tag(self, tag):
    if tag.startswith("/"):
        node = self.unfinished.pop()
        parent = self.unfinished[-1]
        parent.children.append(node)
    # ...
```

파서가 끝나면, 남아 있는 미완성 노드들을 모두 완성하는 것만으로 미완성 트리를 완성 트리로 바꿉니다.

```python
class HTMLParser:
    def finish(self):
        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        return self.unfinished.pop()
```

이것은 _거의_ 완전한 파서이지만, 문서의 시작과 끝에서 제대로 동작하지 않습니다. 맨 처음 여는 태그는 부모가 없는 예외 사례입니다.

```python
def add_tag(self, tag):
    # ...
    else:
        parent = self.unfinished[-1] if self.unfinished else None
        # ...
```

맨 마지막 태그도 예외 사례인데, 추가할 미완성 노드가 없기 때문입니다.

```python
def add_tag(self, tag):
    if tag.startswith("/"):
        if len(self.unfinished) == 1: return
        # ...
```

좋습니다, 다 됐습니다. 파서를 시험해 보고 얼마나 잘 동작하는지 봅시다!

### 더 알아보기

잘못 설계된 JavaScript의 `document.write` 메서드는 HTML 소스 코드가 파싱되는 도중에 JavaScript가 그것을 수정할 수 있게 해 줍니다! 이는 사실 [나쁜 생각](https://developer.mozilla.org/en-US/docs/Web/API/Document/write)입니다. `document.write`를 구현하려면 HTML 파서가 멈춰 서서 JavaScript를 실행해야 하는데, 그러면 페이지 뒤쪽에서 사용되는 이미지, CSS, JavaScript의 요청이 느려집니다. 이를 해결하기 위해 현대 브라우저는 [투기적 파싱(speculative parsing)](https://developer.mozilla.org/en-US/docs/Glossary/speculative_parsing)을 사용해 파싱이 끝나기도 전에 추가 리소스를 미리 불러오기 시작합니다.

## 파서 디버깅하기

파서가 올바른 일을, 즉 올바른 트리를 만들고 있는지 어떻게 알 수 있을까요? 시작점은 파서가 만들어 내는 트리를 _보는_ 것입니다. 간단한 재귀적 예쁜 출력기(pretty-printer)로 그렇게 할 수 있습니다.

```python
def print_tree(node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)
```

여기서는 트리의 각 노드를 출력하면서 들여쓰기로 트리 구조를 보여 줍니다. 각 노드를 출력해야 하므로, 노드에 보기 좋은 출력 형태를 부여하는 데 시간을 들일 가치가 있습니다. Python에서 그것은 `__repr__` 함수를 정의하는 것을 뜻합니다.

```python
class Text:
    def __repr__(self):
        return repr(self.text)

class Element:
    def __repr__(self):
        return "<" + self.tag + ">"
```

일반적으로 어떤 데이터 객체든 `__repr__` 메서드를 정의하고, 그 `__repr__` 메서드가 관련된 모든 필드를 출력하게 하는 것이 좋은 습관입니다.

이 장에 해당하는 [웹 페이지](https://browser.engineering/html.html)로 시험해 보세요. HTML 소스 코드를 파싱한 다음 `print_tree`를 호출해 시각화합니다.

```
body = URL(sys.argv[1]).request()
nodes = HTMLParser(body).parse()
print_tree(nodes)
```

앞부분에서 다음과 같은 것이 보일 것입니다.

```
 <!doctype html>
   '\n'
   <html lang="en-US" xml:lang="en-US">
     '\n'
     <head>
       '\n  '
       <meta charset="utf-8" />
```

몇 가지가 곧바로 눈에 띕니다. 맨 위의 `<!doctype html>` 태그부터 살펴봅시다.

[doctype](https://html.spec.whatwg.org/multipage/syntax.html#the-doctype)이라고 불리는 이 특별한 태그는 항상 HTML 문서의 맨 처음에 옵니다. 하지만 이것은 사실 요소가 전혀 아니며, 닫는 태그도 있어서는 안 됩니다. 우리 브라우저는 doctype을 아무 데도 쓰지 않을 것이므로 버리는 편이 가장 좋습니다.[^4]

```python
def add_tag(self, tag):
    if tag.startswith("!"): return
    # ...
```

이 코드는 느낌표로 시작하는 모든 태그를 무시하는데, 그러면 doctype 선언뿐 아니라 주석도 버려집니다. HTML에서 주석은 `<!-- 주석 텍스트 -->`로 씁니다.

그런데 doctype만 버려서는 충분하지 않습니다. 지금 파서를 실행하면 죽어 버립니다. doctype 다음에 줄바꿈이 오는데, 우리 파서가 그것을 텍스트로 취급해 트리에 넣으려 하기 때문입니다. 그런데 파서가 아직 여는 태그를 하나도 보지 못했으니 트리가 없습니다. 단순하게 가기 위해, 이 문제를 피해 가도록 브라우저가 공백만으로 이루어진 텍스트 노드를 건너뛰게 합시다.[^5]

```python
def add_text(self, text):
    if text.isspace(): return
    # ...
```

이제 `browser.engineering` 홈페이지에 대해 파싱된 HTML 트리의 앞부분은 다음과 비슷해 보입니다.

```
 <html lang="en-US" xml:lang="en-US">
   <head>
     <meta charset="utf-8" /="">
       <link rel="prefetch" ...>
         <link rel="prefetch" ...>
```

다음 문제입니다. 왜 모든 것이 이렇게 깊게 들여쓰기되어 있을까요? 이 열린 요소들은 왜 한 번도 닫히지 않을까요?

### 더 알아보기

SGML에서는 문서 타입 선언에 유효한 태그를 정의하는 URL이 들어 있었고, HTML의 예전 버전에서도 그렇게 하는 것이 권장되었습니다. 브라우저는 문서 타입 선언이 없다는 사실로 SGML 이전의 아주 오래된 HTML 버전을 [식별하지만](https://developer.mozilla.org/en-US/docs/Web/HTML/Quirks_Mode_and_Standards_Mode),[^6] URL은 사용하지 않습니다. 그래서 현대 HTML에는 `<!doctype html>`이 최선의 문서 타입 선언입니다.

## 자체 닫힘 태그

`<meta>`나 `<link>` 같은 요소는 자체 닫힘(self-closing) 태그라고 불립니다. 이 태그들은 내용을 감싸지 않으므로 `</meta>`나 `</link>`라고 쓰는 일이 없습니다. 우리 파서에는 이들을 위한 특별한 지원이 필요합니다. HTML에는 이러한 자체 닫힘 태그의 [구체적인 목록](https://html.spec.whatwg.org/multipage/syntax.html#void-elements)이 있습니다(명세에서는 이들을 "void" 태그라고 부릅니다).[^7]

```python
SELF_CLOSING_TAGS = [
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
]
```

우리 파서는 이 목록에 있는 태그들을 자동으로 닫아야 합니다.

```python
def add_tag(self, tag):
    # ...
    elif tag in self.SELF_CLOSING_TAGS:
        parent = self.unfinished[-1]
        node = Element(tag, parent)
        parent.children.append(node)
```

이 코드는 맞아 보이지만 제대로 동작하지 않습니다. 왜 그럴까요? 우리 파서는 `meta`라는 이름의 태그를 찾고 있는데, 실제로 찾은 것은 "`meta name=...`"이라는 이름의 태그이기 때문입니다. `<meta>` 태그에 속성이 있어서 자체 닫힘 처리 코드가 발동하지 않은 것입니다.

HTML 속성은 요소에 대한 정보를 덧붙입니다. 여는 태그에는 속성이 몇 개든 올 수 있습니다. 속성 값은 따옴표로 감쌀 수도, 감싸지 않을 수도, 아예 생략할 수도 있습니다. 조금 복잡한 문제인 공백을 포함하는 값은 무시하고, 기본적인 속성 지원에 집중합시다.

값에 들어 있는 공백을 처리하지 않으므로, 공백을 기준으로 나누어 태그 이름과 속성–값 쌍을 얻을 수 있습니다.

```python
class HTMLParser:
    def get_attributes(self, text):
        parts = text.split()
        tag = parts[0].casefold()
        attributes = {}
        for attrpair in parts[1:]:
            # ...
        return tag, attributes
```

HTML 태그 이름은 대소문자를 구분하지 않으며, 덧붙이자면 속성 이름도 그렇습니다. 그래서 케이스 폴딩을 합니다.[^8] 그다음 루프 안에서 각 속성–값 쌍을 이름과 값으로 나눕니다. 가장 쉬운 경우는 등호가 둘을 구분해 주는, 따옴표 없는 속성입니다.

```python
def get_attributes(self, text):
    # ...
    for attrpair in parts[1:]:
        if "=" in attrpair:
            key, value = attrpair.split("=", 1)
            attributes[key.casefold()] = value
    # ...
```

`<input disabled>`처럼 값이 생략될 수도 있는데, 이 경우 속성 값은 빈 문자열이 기본값이 됩니다.

```python
for attrpair in parts[1:]:
    # ...
    else:
        attributes[attrpair.casefold()] = ""
```

마지막으로 값이 따옴표로 감싸여 있을 수 있는데, 이때는 따옴표를 벗겨 내야 합니다.[^9]

```python
if "=" in attrpair:
    # ...
    if len(value) > 2 and value[0] in ["'", "\""]:
        value = value[1:-1]
    # ...
```

이 속성들은 `Element` 안에 저장하겠습니다.

```python
class Element:
    def __init__(self, tag, attributes, parent):
        self.tag = tag
        self.attributes = attributes
        # ...
```

즉 `Element`를 만드는 데 필요한 `attributes`를 얻기 위해 `add_tag`의 맨 위에서 `get_attributes`를 호출해야 합니다.

```python
def add_tag(self, tag):
    tag, attributes = self.get_attributes(tag)
    # ...
```

`add_tag`에서 `text` 대신 `tag`와 `attribute`를 사용하는 것을 잊지 말고, 파서를 다시 시험해 보세요.

```
 <html>
    <head>
      <meta>
      <link>
      <link>
      <link>
      <link>
      <link>
      <meta>
```

거의 다 됐습니다! 속성을 출력해 보면, 공백이 들어 있는 속성(`meta` 태그 중 하나의 `author` 같은)이 여러 개의 속성으로 잘못 파싱되고, 자체 닫힘 태그 끝의 슬래시가 잘못하여 추가 속성으로 취급되는 것을 볼 수 있습니다. 더 나은 파서라면 이 문제들을 고칠 것입니다. 하지만 우리 파서는 이대로 두고 — 우리가 만드는 브라우저에서는 이 문제들이 걸림돌이 되지 않습니다 — 이것을 브라우저에 통합하는 일로 넘어갑시다.

### 더 알아보기

`<br/>`처럼 자체 닫힘 태그 끝에 슬래시를 붙이는 것은 [XHTML](https://www.w3.org/TR/xhtml1/)이 HTML을 대체할 것처럼 보이던 시절에 유행했고, 저 같은 옛날 사람은 그 습관을 끝내 버리지 못했습니다. 하지만 [XML](https://www.w3.org/TR/xml/#sec-starttags)과 달리 HTML에서는 자체 닫힘 태그를 어떤 특별한 문법이 아니라 이름으로 식별하므로, 슬래시는 선택 사항입니다.

## 노드 트리 사용하기

지금 `Layout` 클래스는 토큰 단위로 동작합니다. 이제는 노드 단위로 동작하게 하고 싶습니다. 그러니 기존 `token` 메서드를 두 부분으로 나눕시다. 여는 태그에 대한 모든 경우는 새로운 `open_tag` 메서드로, 닫는 태그에 대한 모든 경우는 새로운 `close_tag` 메서드로 옮깁니다.[^10]

```python
class Layout:
    def open_tag(self, tag):
        if tag == "i":
            self.style = "italic"
        # ...

    def close_tag(self, tag):
        if tag == "i":
            self.style = "roman"
        # ...
```

이제 `Layout` 객체가 노드 트리를 순회하며 `open_tag`, `close_tag`, `text`를 올바른 순서로 호출하게 해야 합니다.

```python
def recurse(self, tree):
    if isinstance(tree, Text):
        for word in tree.text.split():
            self.word(word)
    else:
        self.open_tag(tree.tag)
        for child in tree.children:
            self.recurse(child)
        self.close_tag(tree.tag)
```

이제 `Layout` 생성자는 토큰 리스트를 순회하는 대신 `recurse`를 호출할 수 있습니다. 또한 브라우저가 노드 트리를 구성하도록 다음과 같이 해야 합니다.

```python
class Browser:
    def load(self, url):
        body = url.request()
        self.nodes = HTMLParser(body).parse()
        self.display_list = Layout(self.nodes).display_list
        self.draw()
```

실행해 보세요. 이제 브라우저는 파싱된 HTML 트리를 사용할 것입니다.

### 더 알아보기

`doctype` 문법은 웹 페이지가 어떤 버전의 HTML을 쓰는지 선언하는 일종의 버전 관리입니다. 그런데 사실 `doctype`의 `html` 값은 특정 버전의 HTML이 아니라 더 일반적으로 [_HTML 리빙 스탠더드_](https://html.spec.whatwg.org/)를 가리킵니다.[^11] 기능이 추가되면서 계속 바뀌기 때문에 "리빙 스탠더드"라고 부릅니다. 이러한 변화의 메커니즘은 그저 브라우저가 새 기능을 출시하는 것일 뿐, HTML의 "버전"이 바뀌는 것이 아닙니다. 일반적으로 웹은 _버전 없는 플랫폼_ 입니다. 새 기능은 대개 확장으로 추가되지만, 기존 기능을 깨뜨리지 않는 한에서만 그렇습니다.[^12]

## 작성자의 실수 처리하기

이제 파서는 HTML 페이지를 올바르게 처리합니다. 적어도 `<head>` 태그를 잊지 않고, 연 태그는 모두 닫으며, 아침에 이불도 개는 모범생 프로그래머가 HTML을 작성했을 때는 그렇습니다. 평범한 인간에게는 그런 절제력이 없으므로 브라우저는 망가지고 혼란스럽고 `head`가 없는 HTML도 처리해야 합니다. 실제로 현대 HTML 파서는 마크업이 아무리 혼란스럽더라도 _어떤_ 문자열이든 HTML 트리로 변환해 낼 수 있습니다.[^13]

예상하시겠지만 전체 알고리즘은 믿기 힘들 만큼 복잡하며, 인간의 실수를 분류해 놓은 듯한 수십 개의 점점 더 특수한 사례들로 이루어져 있습니다. 그중 비교적 괜찮은 기능 하나가 _암묵적_ 태그입니다. 보통 HTML 문서는 익숙한 상용구로 시작합니다.

```
<!doctype html>
<html>
  <head>
  </head>
  <body>
  </body>
</html>
```

사실 doctype을 제외한 _이 여섯 개 태그 전부_ 가 선택 사항입니다. 웹 페이지가 이들을 생략하면 브라우저가 자동으로 삽입해 줍니다. 새로운 `implicit_tags` 함수를 통해 우리 브라우저에도 암묵적 태그를 넣어 봅시다. 이 함수는 `add_text`와 `add_tag` 양쪽에서 호출해야 합니다.

```python
class HTMLParser:
    def add_text(self, text):
        if text.isspace(): return
        self.implicit_tags(None)
        # ...

    def add_tag(self, tag):
        tag, attributes = self.get_attributes(tag)
        if tag.startswith("!"): return
        self.implicit_tags(tag)
        # ...
```

무시되는 공백과 doctype에 대해서는 `implicit_tags`가 호출되지 않는다는 점에 주의하세요. 빈 문자열에 대해서도 `<html>`과 `<body>` 태그가 만들어지도록 `finish`에서도 호출합시다.

```python
class HTMLParser:
    def finish(self):
        if not self.unfinished:
            self.implicit_tags(None)
        # ...
```

`implicit_tags`의 인자는 태그 이름입니다(텍스트 노드의 경우 `None`). 무엇이 생략되었는지 판단하기 위해 이를 미완성 태그 목록과 비교하겠습니다.

```python
class HTMLParser:
    def implicit_tags(self, tag):
        while True:
            open_tags = [node.tag for node in self.unfinished]
            # ...
```

`implicit_tags`에 루프가 있는 이유는 여러 태그가 연달아 생략되었을 수 있기 때문입니다. 루프를 한 번 돌 때마다 태그를 하나씩만 추가합니다. 어떤 암묵적 태그를 추가할지(추가하기는 할지) 판단하려면 열려 있는 태그들과 지금 삽입되는 태그를 살펴봐야 합니다.

가장 쉬운 경우인 암묵적 `<html>` 태그부터 시작합시다. 문서의 첫 태그가 `<html>`이 아닌 다른 것이라면 암묵적 `<html>` 태그가 필요합니다.

```python
while True:
    # ...
    if open_tags == [] and tag != "html":
        self.add_tag("html")
```

`<head>`와 `<body>`도 생략될 수 있지만, 둘 중 어느 쪽인지 알아내려면 어떤 태그가 추가되고 있는지 봐야 합니다.

```python
while True:
    # ...
    elif open_tags == ["html"] \
         and tag not in ["head", "body", "/html"]:
        if tag in self.HEAD_TAGS:
            self.add_tag("head")
        else:
            self.add_tag("body")
```

여기서 `HEAD_TAGS`는 `<head>` 요소 안에 넣어야 하는 태그들의 목록입니다.[^14]

```python
class HTMLParser:
    HEAD_TAGS = [
        "base", "basefont", "bgsound", "noscript",
        "link", "meta", "title", "style", "script",
    ]
```

`<html>`과 `<head>` 태그가 둘 다 생략되었다면 `implicit_tags`가 루프를 두 번 돌면서 둘 다 삽입하게 된다는 점에 주의하세요. 첫 번째 반복에서 `open_tags`는 `[]`이므로 코드가 `<html>` 태그를 추가하고, 두 번째 반복에서 `open_tags`는 `["html"]`이므로 `<head>` 태그를 추가합니다.[^15]

마지막으로, 파서가 `<head>` 안에 있는데 `<body>`에 들어가야 할 요소를 만나면 `</head>` 태그도 암묵적으로 처리될 수 있습니다.

```python
while True:
    # ...
    elif open_tags == ["html", "head"] and \
         tag not in ["/head"] + self.HEAD_TAGS:
        self.add_tag("/head")
```

엄밀히 말하면 `</body>`와 `</html>` 태그도 암묵적일 수 있습니다. 하지만 우리 `finish` 함수가 이미 미완성 태그를 모두 닫아 주므로 추가 코드는 필요 없습니다. 그러니 `implicit_tags`에 남은 일은 루프를 빠져나가는 것뿐입니다.

```python
while True:
    # ...
    else:
        break
```

물론 잘못된 형식의 HTML을 처리하는 규칙은 더 많습니다. 서식 태그, 중첩된 문단, 내장된 확장 가능 벡터 그래픽(SVG)과 MathML, 그 밖의 온갖 복잡한 것들이 있습니다. 각각은 예외 사례로 가득한 복잡한 규칙을 갖고 있습니다. 하지만 작성자의 실수를 처리하는 이야기는 여기서 마치겠습니다.

잘못된 형식의 HTML에 대한 규칙은 자의적으로 보일 수 있고, 실제로도 그렇습니다. 이 규칙들은 사람들이 그런 HTML을 썼을 때 무엇을 "의도했는지" 추측하려는 수년간의 시도를 거쳐 진화했고, 이제는 [HTML 파싱 표준](https://html.spec.whatwg.org/multipage/parsing.html)에 성문화되어 있습니다. 물론 이 규칙들이 잘못 "추측"할 때도 있습니다. 하지만 웹에서 흔히 그렇듯, 각 브라우저가 저마다 _올바른_ 것을 추측하려 애쓰는 것보다 모든 브라우저가 _같은_ 일을 하는 편이 더 중요합니다.

이제 그 결실입니다! 그림 3은 [이 책의 웹사이트](https://browser.engineering/)를 우리가 만든 브라우저로 불러온 스크린샷입니다.[^16]

![그림 3: 이 장의 브라우저 버전으로 본 http://browser.engineering/ 의 스크린샷.](example4-browserengineering-screenshot.png)

### 더 알아보기

암묵적 태그 덕분에 `<html>`, `<body>`, `<head>` 요소는 대체로 생략할 수 있고, 그러면 암묵적으로 다시 채워집니다. 사실 HTML 파서의 [수많은 상태](https://html.spec.whatwg.org/multipage/parsing.html#parsing-main-afterbody)는 그보다 더 엄격한 것을 보장합니다. 모든 HTML 문서에는 정확히 하나의 `<head>`와 하나의 `<body>`가 예상되는 순서로 존재합니다.[^17]

## 요약

이 장에서는 HTML이 평평한 토큰 목록이 아니라 트리라는 것을 브라우저에 가르쳤습니다. 우리가 추가한 것은 다음과 같습니다.

- HTML 토큰을 트리로 변환하는 파서

- 요소의 속성을 인식하고 처리하는 코드

- 일부 잘못된 형식의 HTML 문서에 대한 자동 교정

- HTML 트리를 배치하는 재귀적 레이아웃 알고리즘

다음 장에서 보게 되겠지만, HTML의 트리 구조는 시각적으로 복잡한 웹 페이지를 표시하는 데 필수적입니다.

> 🔗 대화형 위젯: [lab4-browser.html](https://browser.engineering/widgets/lab4-browser.html)

## 개요

우리 브라우저의 함수, 클래스, 메서드 전체 목록은 대략 다음과 같아야 합니다.

```python
class URL:
    def __init__(url)

    def request()


class Text:
    def __init__(text, parent)

    def __repr__()


class Element:
    def __init__(tag, attributes, parent)

    def __repr__()


def print_tree(node, indent)

class HTMLParser:
    SELF_CLOSING_TAGS

    HEAD_TAGS

    def __init__(body)

    def parse()

    def get_attributes(text)

    def add_text(text)

    def add_tag(tag)

    def implicit_tags(tag)

    def finish()


FONTS

def get_font(size, weight, style)

WIDTH, HEIGHT

HSTEP, VSTEP

class Layout:
    def __init__(tree)

    def recurse(tree)

    def open_tag(tag)

    def close_tag(tag)

    def flush()

    def word(word)


SCROLL_STEP

class Browser:
    def __init__()

    def draw()

    def load(url)

    def scrolldown(e)
```

## 연습문제

**4-1 _주석_.** HTML 렉서가 주석을 지원하도록 갱신하세요. HTML의 주석은 `<!--`로 시작해 `-->`로 끝납니다. 다만 주석은 태그와 다릅니다. 좌우 꺾쇠괄호를 포함한 어떤 텍스트든 담을 수 있습니다. 렉서는 주석을 건너뛰고 토큰을 전혀 만들지 않아야 합니다. 확인해 보세요. `<!-->`는 주석일까요, 아니면 주석을 시작하기만 하는 걸까요?

**4-2 _문단_.** 한 문단이 다른 문단을 담는다는 것이 무슨 뜻인지는 분명하지 않습니다. `<p>hello<p>world</p>` 같은 문서가 한 문단 안에 다른 문단이 들어가는 대신 형제 관계인 두 문단이 되도록 파서를 바꾸세요. 실제 브라우저도 이렇게 합니다. `<li>` 요소에도 같은 처리를 하되, 중첩된 목록은 여전히 가능하도록 하세요.

**4-3 _스크립트_.** `<script>` 태그 안에 들어 있는 JavaScript 코드는 왼쪽 꺾쇠괄호를 "미만"의 뜻으로 사용합니다. `<script>` 태그의 내용을 특별하게 취급하도록 렉서를 수정하세요. `</script>` 닫는 태그를 제외하고는 `<script>` 안에서 어떤 태그도 허용되지 않아야 합니다.[^18]

**4-4 _따옴표로 감싼 속성_.** 따옴표로 감싼 속성에는 공백과 오른쪽 꺾쇠괄호가 들어갈 수 있습니다. 이것이 제대로 지원되도록 렉서를 고치세요. 힌트: 현재 렉서는 (`in_tag`로 결정되는) 두 개의 상태를 가진 유한 상태 기계입니다. 상태가 더 필요할 것입니다.

**4-5 _구문 강조_.** [연습문제 1-5](https://browser.engineering/http.html#exercises)처럼 `view-source` 프로토콜을 구현하되, HTML 페이지의 소스 코드에 구문 강조를 적용하세요. HTML 태그의 소스 코드는 보통 폰트로 두고 텍스트 내용은 굵게 만드세요. 구현했다면 줄바꿈을 보존하기 위해 텍스트를 `<pre>` 태그로 감싸기도 하세요. 힌트: HTML 파서를 상속받아 구문 강조기를 구현하세요.

**4-6 _잘못 중첩된 서식 태그_.** `<b>Bold <i>both</b> italic</i>` 같은 마크업을 지원하도록 HTML 파서를 확장하세요. 그러려면 열려 있는 텍스트 서식 요소의 집합을 추적하고, 텍스트 서식 요소가 잘못된 순서로 닫힐 때 암묵적인 여는 태그와 닫는 태그를 삽입해야 합니다. 예를 들어 위의 굵게/이탤릭 예제에서는 `</b>` 앞에 암묵적 `</i>`를, 그 뒤에 암묵적 `<i>`를 삽입해야 합니다.

## 각주

[^1]: 이것은 보통 [문서 객체 모델(Document Object Model)](https://en.wikipedia.org/wiki/Document_Object_Model)의 약자를 따 DOM 트리라고 불리는 트리입니다. 지금은 계속 HTML 트리라고 부르겠습니다.

[^2]: 실제로는 주석, doctype, `CDATA` 구역, 처리 명령 같은 다른 종류의 노드도 있습니다. 심지어 사용이 중단된 종류도 있습니다!

[^3]: Python을 비롯한 대부분의 언어에서는 리스트의 앞쪽보다 뒤쪽에서 추가하고 제거하는 것이 더 빠릅니다.

[^4]: 실제 브라우저는 doctype을 사용해 표준 준수 모드와 레거시 파싱·레이아웃 모드 사이를 전환합니다.

[^5]: 실제 브라우저는 `make<span></span>up`을 한 단어로, `make<span> </span>up`을 두 단어로 올바르게 렌더링하기 위해 공백을 보존합니다. 우리 브라우저는 그러지 않습니다. 게다가 공백을 무시하면 공백만 있는 텍스트 태그에 대한 특수 처리를 피할 수 있어 이후 장들이 단순해집니다.

[^6]: 테이블 셀의 세로 레이아웃에 하위 호환되지 않는 변경이 생기면서 "[거의 표준(almost standards)](https://hsivonen.fi/doctype/)" 또는 "제한적 쿼크(limited quirks)" 모드라는 미친 것도 생겼습니다. 정말입니다. 제가 지어낼 필요도 없습니다!

[^7]: 이 태그들 중 상당수는 잘 알려져 있지 않습니다. 브라우저는 여기 나열되지 않은 `keygen` 같은 몇몇 구식 자체 닫힘 태그도 추가로 지원합니다.

[^8]: 텍스트를 소문자로 바꾸는 것은 체로키어 같은 언어에서 대소문자 무시 비교를 하는 [잘못된 방법](https://www.b-list.org/weblog/2018/nov/26/case/)입니다. HTML에 한정하면 태그 이름은 ASCII 문자만 사용하므로 소문자로 바꾸는 것만으로 충분하지만, 좋은 습관이므로 Python의 `casefold` 함수를 사용하겠습니다.

[^9]: 따옴표로 감싼 속성은 따옴표 사이에 공백을 허용합니다. 이를 제대로 파싱하려면 그냥 공백으로 나누는 대신 유한 상태 기계 같은 것이 필요합니다.

[^10]: 텍스트 토큰에 대한 경우는 더 이상 필요 없습니다. 우리 브라우저는 기존의 `add_text` 메서드를 직접 호출하면 되기 때문입니다.

[^11]: HTML에 새로운 `doctype` 버전이 다시 추가되는 일은 없을 것으로 예상됩니다.

[^12]: 기능을 제거할 수는 있지만, 오직 대다수 사이트가 그것을 더 이상 쓰지 않게 되었을 때만 가능합니다. 그래서 다른 플랫폼에 비해 웹의 기능을 제거하기가 매우 어렵습니다.

[^13]: 그렇습니다, 미친 짓이죠. 2000년대 초 몇 년 동안 W3C는 이를 [없애려 했습니다](https://www.w3.org/TR/xhtml1/). 실패했지만요.

[^14]: `<script>` 태그는 head 구역과 body 구역 어느 쪽에도 들어갈 수 있지만, 기본적으로는 head로 들어갑니다.

[^15]: 이 `add_tag` 메서드들 자체가 `implicit_tags`를 호출하므로, 어떤 경우를 빠뜨리면 무한 루프에 빠질 수 있습니다. 저는 `implicit_tags`가 추가하는 모든 태그가 그 자체로 더 많은 암묵적 태그를 유발하지 않도록 조심했습니다.

[^16]: 공정하게 말하면, 3장의 브라우저로 봐도 거의 같아 보입니다.

[^17]: 적어도 문서 하나당 그렇습니다. 프레임이나 템플릿을 사용하는 HTML 파일에는 `<head>`와 `<body>`가 여러 개 있을 수 있지만, 그것들은 서로 다른 문서에 속합니다.

[^18]: 엄밀히 말하면 `</script` 뒤에 [공백, 탭, `\v`, `\r`, 슬래시, 또는 초과 기호](https://html.spec.whatwg.org/multipage/parsing.html#script-data-end-tag-name-state)가 오는 경우입니다. JavaScript 코드 안에서 `</script>` 태그를 언급해야 한다면 문자열을 여러 개로 쪼개야 합니다.

---

저작권 © 2018–2024 [Pavel Panchekha](https://pavpanchekha.com) & [Chris Harrelson](https://twitter.com/chrishtr). 이 문서는 [Web Browser Engineering](https://browser.engineering/html.html)의 한국어 번역입니다.
