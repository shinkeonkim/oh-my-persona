import type { CopyrightFinding } from "./types"

const SENSITIVE_PATTERNS = [
  { rule: "question-count", expression: /(?:문제|문항)\s*수\s*\|?\s*\*{0,2}\d+/i },
  { rule: "question-ratio", expression: /(?:문제|정답)(?:\s*유형)?\s*(?:비율|분포)/i },
  {
    rule: "question-link",
    expression: /\[[^\]]*(?:예시\s*문제|문제\s*풀기)[^\]]*\]\([^)]*\.md\)/i,
  },
  { rule: "question-bank", expression: /문제\s*은행\s*(?:홈|바로가기)/i },
] as const

function removeSensitiveSections(markdown: string): string {
  const retained: string[] = []
  let hiddenHeadingLevel = 0

  for (const line of markdown.split("\n")) {
    if (/^\*\*(?:문제|정답).*분포[^*]*\*\*$/i.test(line.trim())) {
      hiddenHeadingLevel = 7
      continue
    }
    if (hiddenHeadingLevel === 7 && line.trim() === "---") {
      hiddenHeadingLevel = 0
      retained.push(line)
      continue
    }
    const heading = line.match(/^(#{2,6})\s+(.+)$/)
    if (heading !== null) {
      const level = heading[1]?.length ?? 0
      const title = heading[2] ?? ""
      if (/(?:문제|정답).*분포/i.test(title)) {
        hiddenHeadingLevel = level
        continue
      }
      if (hiddenHeadingLevel > 0 && level <= hiddenHeadingLevel) hiddenHeadingLevel = 0
    }
    if (hiddenHeadingLevel === 0) retained.push(line)
  }

  return retained.join("\n")
}

function removeSensitiveTableRows(markdown: string): string {
  return markdown
    .split("\n")
    .filter((line) => !/^\|[^|]*(?:문제 수|문항 수|시험 비중|문제 비율)[^|]*\|/i.test(line))
    .join("\n")
}

function replaceQuestionLinks(markdown: string): string {
  return markdown
    .replace(/\[([^\]]*(?:예시\s*문제|문제\s*풀기)[^\]]*)\]\([^)]*\.md\)/gi, "$1")
    .replace(/\((?:약\s*)?\d+\s*(?:문제|문항)\)/g, "")
}

export function sanitizeStudyNote(markdown: string): string {
  return replaceQuestionLinks(removeSensitiveTableRows(removeSensitiveSections(markdown)))
    .replace(/\n{3,}/g, "\n\n")
    .trim()
}

export function auditStudyNote(markdown: string): readonly CopyrightFinding[] {
  const findings: CopyrightFinding[] = []
  for (const pattern of SENSITIVE_PATTERNS) {
    const match = markdown.match(pattern.expression)
    if (match?.[0] !== undefined) findings.push({ rule: pattern.rule, excerpt: match[0] })
  }
  return findings
}
