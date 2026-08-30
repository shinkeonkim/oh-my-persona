import { describe, expect, it } from "bun:test"

import { loginInputSchema } from "./auth"
import { CERTIFICATIONS, findCertification } from "./certifications"
import {
  answerInputSchema,
  answerResultSchema,
  questionSchema,
  quizQuerySchema,
  quizResponseSchema,
} from "./content"

describe("shared schemas", () => {
  it("normalizes a valid login email", () => {
    // Given
    const input = { email: "  USER@Example.com ", password: "a-secure-password" }

    // When
    const result = loginInputSchema.parse(input)

    // Then
    expect(result.email).toBe("user@example.com")
  })

  it("rejects a question with an invalid option key", () => {
    // Given
    const input = {
      sourceId: "saa-01",
      certificationCode: "saa",
      categorySlug: "ec2",
      prompt: "Question",
      options: [
        { key: "A", text: "First" },
        { key: "F", text: "Second" },
      ],
      answers: ["A"],
      explanation: "Explanation",
      access: "protected",
    }

    // When
    const result = questionSchema.safeParse(input)

    // Then
    expect(result.success).toBeFalse()
  })

  it("returns every approved certification by code", () => {
    // Given
    const codes = CERTIFICATIONS.map((certification) => certification.code)

    // When
    const titles = codes.map((code) => findCertification(code).title)

    // Then
    expect(titles).toHaveLength(3)
  })
})

describe("quizQuerySchema", () => {
  it("applies defaults for page and pageSize", () => {
    const result = quizQuerySchema.parse({})
    expect(result).toEqual({ page: 1, pageSize: 20 })
  })

  it("accepts an optional category filter", () => {
    const result = quizQuerySchema.parse({ category: "ec2", page: 2 })
    expect(result).toEqual({ category: "ec2", page: 2, pageSize: 20 })
  })

  it("coerces string page/pageSize from query params", () => {
    const result = quizQuerySchema.parse({ page: "3", pageSize: "10" })
    expect(result).toEqual({ page: 3, pageSize: 10 })
  })

  it("rejects pageSize above 50", () => {
    expect(quizQuerySchema.safeParse({ pageSize: 51 }).success).toBeFalse()
  })

  it("rejects page below 1", () => {
    expect(quizQuerySchema.safeParse({ page: 0 }).success).toBeFalse()
  })
})

describe("quizResponseSchema", () => {
  it("validates a full paginated response", () => {
    const input = {
      questions: [
        {
          id: "550e8400-e29b-41d4-a716-446655440000",
          categorySlug: "ec2",
          prompt: "What is EC2?",
          options: [
            { key: "A", text: "Compute" },
            { key: "B", text: "Storage" },
          ],
        },
      ],
      pagination: {
        page: 1,
        pageSize: 20,
        totalQuestions: 1,
        totalPages: 1,
        category: null,
      },
      categoryCounts: { ec2: 1 },
    }
    expect(quizResponseSchema.safeParse(input).success).toBeTrue()
  })

  it("requires categorySlug on each question", () => {
    const input = {
      questions: [{ id: "550e8400-e29b-41d4-a716-446655440000", prompt: "Q", options: [] }],
      pagination: { page: 1, pageSize: 20, totalQuestions: 0, totalPages: 0, category: null },
      categoryCounts: {},
    }
    expect(quizResponseSchema.safeParse(input).success).toBeFalse()
  })
})

describe("answerInputSchema", () => {
  it("accepts valid answer keys", () => {
    const result = answerInputSchema.parse({ selectedAnswers: ["A", "C"] })
    expect(result.selectedAnswers).toEqual(["A", "C"])
  })

  it("rejects empty selectedAnswers", () => {
    expect(answerInputSchema.safeParse({ selectedAnswers: [] }).success).toBeFalse()
  })

  it("rejects invalid keys", () => {
    expect(answerInputSchema.safeParse({ selectedAnswers: ["Z"] }).success).toBeFalse()
  })
})

describe("answerResultSchema", () => {
  it("validates a correct answer result", () => {
    const input = { correct: true, answers: ["A"], explanation: "Because A" }
    expect(answerResultSchema.safeParse(input).success).toBeTrue()
  })
})
