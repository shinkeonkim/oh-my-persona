import { describe, expect, it } from "bun:test"

import { auditStudyNote, sanitizeStudyNote } from "./copyright-filter"
import { parseQuestion } from "./question-parser"

describe("sanitizeStudyNote", () => {
  it("removes counts, distributions, and direct question links while preserving patterns", () => {
    // Given
    const markdown = `# EC2
| 항목 | 내용 |
|---|---|
| 문제 수 | **37문제** |

**문제 분포 (37문제 기준)**
| 토픽 | 문제 수 | 비율 |
|---|---|---|
| 구매 옵션 | 18 | 49% |

---
## 출제 패턴 분석
대표 신호어는 중단 가능입니다. [예시 문제](../01-ec2/example.md)`

    // When
    const sanitized = sanitizeStudyNote(markdown)

    // Then
    expect(sanitized).toContain("출제 패턴 분석")
    expect(auditStudyNote(sanitized)).toEqual([])
  })
})

describe("parseQuestion", () => {
  it("parses the canonical markdown question format", () => {
    // Given
    const markdown = `## Question
서비스를 선택하세요.

- [ ] A. Amazon EC2
- [ ] B. Amazon S3

## Answer
정답: B

## Explanation
객체 스토리지는 S3입니다.`

    // When
    const question = parseQuestion({
      sourceId: "clf:test",
      certificationCode: "clf",
      categorySlug: "storage",
      markdown,
      access: "protected",
    })

    // Then
    expect(question.answers).toEqual(["B"])
    expect(question.options).toHaveLength(2)
    expect(question.prompt).toBe("서비스를 선택하세요.")
  })
})
