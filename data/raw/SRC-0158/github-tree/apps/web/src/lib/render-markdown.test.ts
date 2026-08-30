import { describe, expect, test } from "bun:test"

import { renderMarkdown } from "./render-markdown"

describe("renderMarkdown", () => {
  test("Given H1-H4 headings — When rendering markdown — Then it returns matching unique anchors", () => {
    const rendered = renderMarkdown(`
# 문서 제목
## 공통 섹션
### 공통 섹션
#### \`코드\` 상세
##### 제외할 제목
`)

    expect(rendered.headings).toEqual([
      { id: "문서-제목", label: "문서 제목", level: 1 },
      { id: "공통-섹션", label: "공통 섹션", level: 2 },
      { id: "공통-섹션-2", label: "공통 섹션", level: 3 },
      { id: "코드-상세", label: "코드 상세", level: 4 },
    ])
    expect(rendered.html).toContain('<h1 id="문서-제목">문서 제목</h1>')
    expect(rendered.html).toContain('<h4 id="코드-상세"><code>코드</code> 상세</h4>')
    expect(rendered.html).toContain('<h5 id="제외할-제목">제외할 제목</h5>')
  })

  test("Given literal marker characters — When rendering headings — Then TOC labels preserve them", () => {
    const rendered = renderMarkdown(`
# Code* 시리즈
## 크론 작업 1~20분
### 최다 출제, ~25문제
`)

    expect(rendered.headings.map(({ label }) => label)).toEqual([
      "Code* 시리즈",
      "크론 작업 1~20분",
      "최다 출제, ~25문제",
    ])
  })
})
