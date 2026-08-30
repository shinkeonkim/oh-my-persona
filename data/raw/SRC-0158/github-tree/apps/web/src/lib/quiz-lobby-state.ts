import type { QuizCategoryProgress, QuizSessionConfig, QuizWrongNote } from "@aws-study/shared"

export function eligibleQuestionCount(
  categories: readonly QuizCategoryProgress[],
  config: QuizSessionConfig,
): number {
  const selected = new Set(config.categorySlugs)
  return categories.reduce((total, category) => {
    if (!selected.has(category.slug)) return total
    switch (config.mode) {
      case "all":
        return total + category.total
      case "unseen":
        return total + category.total - category.attempted
      case "wrong":
        return total + category.wrong
    }
    const exhaustiveMode: never = config.mode
    return exhaustiveMode
  }, 0)
}

export function sessionQuestionCount(eligible: number, limit: number | null): number {
  return limit === null ? eligible : Math.min(eligible, limit)
}

export function buildWrongNotesMarkdown(
  certification: string,
  notes: readonly QuizWrongNote[],
  generatedAt: string,
): string {
  const lines = [
    `# ${certification} 오답 노트`,
    "",
    `> 총 ${notes.length}문항 · 생성일: ${generatedAt}`,
    "",
  ]
  for (const note of notes) {
    lines.push(`## ${note.categorySlug} · ${note.questionId}`, "")
    lines.push(`- 시각: ${note.updatedAt}`)
    lines.push(
      `- 제출: **${note.selectedAnswers.join(", ")}** / 정답: **${note.answers.join(", ")}**`,
      "",
    )
    lines.push("### 문제", note.prompt, "", "### 보기")
    for (const option of note.options) {
      lines.push(
        `- ${note.answers.includes(option.key) ? "✓" : " "} **${option.key}.** ${option.text}`,
      )
    }
    lines.push("", "### 해설", note.explanation, "", "---", "")
  }
  return lines.join("\n")
}
