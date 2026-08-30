import { describe, expect, it } from "bun:test"
import type { QuizCategoryProgress, QuizSessionConfig, QuizWrongNote } from "@aws-study/shared"

import {
  buildWrongNotesMarkdown,
  eligibleQuestionCount,
  sessionQuestionCount,
} from "./quiz-lobby-state"

const categories: readonly QuizCategoryProgress[] = [
  { slug: "compute", title: "Compute", total: 20, attempted: 12, correct: 9, wrong: 3 },
  { slug: "storage", title: "Storage", total: 30, attempted: 10, correct: 6, wrong: 4 },
]

function config(mode: QuizSessionConfig["mode"]): QuizSessionConfig {
  return {
    certificationCode: "saa",
    mode,
    order: "sequential",
    questionLimit: null,
    categorySlugs: ["storage"],
  }
}

describe("quiz lobby state", () => {
  it("counts all, unseen, and wrong questions only in selected categories", () => {
    expect(eligibleQuestionCount(categories, config("all"))).toBe(30)
    expect(eligibleQuestionCount(categories, config("unseen"))).toBe(20)
    expect(eligibleQuestionCount(categories, config("wrong"))).toBe(4)
  })

  it("caps a session only when a positive limit is configured", () => {
    expect(sessionQuestionCount(30, null)).toBe(30)
    expect(sessionQuestionCount(30, 10)).toBe(10)
    expect(sessionQuestionCount(4, 10)).toBe(4)
  })

  it("exports a wrong-note Markdown document with submitted and correct answers", () => {
    const notes: readonly QuizWrongNote[] = [
      {
        questionId: "20000000-0000-4000-8000-000000000001",
        categorySlug: "storage",
        prompt: "Which service stores objects?",
        options: [
          { key: "A", text: "Amazon S3" },
          { key: "B", text: "Amazon EC2" },
        ],
        answers: ["A"],
        explanation: "Amazon S3 stores objects.",
        selectedAnswers: ["B"],
        updatedAt: "2026-08-05T00:00:00.000Z",
      },
    ]

    const markdown = buildWrongNotesMarkdown("SAA", notes, "2026-08-05T01:00:00.000Z")
    expect(markdown).toContain("# SAA 오답 노트")
    expect(markdown).toContain("제출: **B** / 정답: **A**")
    expect(markdown).toContain("- ✓ **A.** Amazon S3")
  })
})
