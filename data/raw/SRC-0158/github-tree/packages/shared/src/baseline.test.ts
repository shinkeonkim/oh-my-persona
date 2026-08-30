import { describe, expect, it } from "bun:test"

import {
  authSessionSchema,
  authUserSchema,
  loginInputSchema,
  registerInputSchema,
  userRoleSchema,
} from "./auth"
import {
  CERTIFICATIONS,
  certificationCodeSchema,
  certificationSchema,
  contentAccessSchema,
  findCertification,
} from "./certifications"
import {
  answerInputSchema,
  answerResultSchema,
  categorySchema,
  questionSchema,
  quizPaginationSchema,
  quizQuerySchema,
  quizQuestionSchema,
  quizResponseSchema,
  studyNoteSchema,
} from "./content"
import { bookmarkInputSchema, progressSummarySchema, progressUpdateSchema } from "./progress"

describe("baseline: certifications exports are stable", () => {
  it("certificationCodeSchema accepts exactly aif/clf/saa", () => {
    expect(certificationCodeSchema.parse("aif")).toBe("aif")
    expect(certificationCodeSchema.parse("clf")).toBe("clf")
    expect(certificationCodeSchema.parse("saa")).toBe("saa")
    expect(certificationCodeSchema.safeParse("dva").success).toBeFalse()
  })

  it("contentAccessSchema accepts exactly public/protected", () => {
    expect(contentAccessSchema.parse("public")).toBe("public")
    expect(contentAccessSchema.parse("protected")).toBe("protected")
    expect(contentAccessSchema.safeParse("private").success).toBeFalse()
  })

  it("certificationSchema parses a valid certification object", () => {
    const result = certificationSchema.parse(CERTIFICATIONS[0])
    expect(result.code).toBe("aif")
    expect(result.examCode).toBe("AIF-C01")
  })

  it("CERTIFICATIONS has exactly 3 entries", () => {
    expect(CERTIFICATIONS).toHaveLength(3)
  })

  it("findCertification returns correct entry", () => {
    expect(findCertification("saa").examCode).toBe("SAA-C03")
  })
})

describe("baseline: auth exports are stable", () => {
  it("userRoleSchema accepts pending/reader/admin", () => {
    for (const role of ["pending", "reader", "admin"] as const) {
      expect(userRoleSchema.parse(role)).toBe(role)
    }
  })

  it("loginInputSchema normalizes email", () => {
    const result = loginInputSchema.parse({ email: " A@B.COM ", password: "secure-pass-1234" })
    expect(result.email).toBe("a@b.com")
  })

  it("registerInputSchema requires displayName", () => {
    const result = registerInputSchema.safeParse({ email: "a@b.com", password: "secure-pass-1234" })
    expect(result.success).toBeFalse()
  })

  it("authUserSchema parses a valid user", () => {
    const user = {
      id: "550e8400-e29b-41d4-a716-446655440000",
      email: "a@b.com",
      displayName: "Test",
      role: "reader",
    }
    expect(authUserSchema.parse(user).role).toBe("reader")
  })

  it("authSessionSchema parses a valid session", () => {
    const session = {
      user: {
        id: "550e8400-e29b-41d4-a716-446655440000",
        email: "a@b.com",
        displayName: "Test",
        role: "admin",
      },
      accessToken: "tok_abc",
      expiresAt: "2026-01-01T00:00:00Z",
    }
    expect(authSessionSchema.parse(session).user.role).toBe("admin")
  })
})

describe("baseline: content exports are stable", () => {
  it("categorySchema parses a valid category", () => {
    const cat = { slug: "ec2", certificationCode: "saa", order: 0, title: "EC2", summary: "" }
    expect(categorySchema.parse(cat).slug).toBe("ec2")
  })

  it("studyNoteSchema parses a valid note", () => {
    const note = {
      slug: "note-1",
      certificationCode: "clf",
      categorySlug: "basics",
      title: "Intro",
      markdown: "# Hello",
      access: "public",
    }
    expect(studyNoteSchema.parse(note).access).toBe("public")
  })

  it("questionSchema parses a valid question", () => {
    const q = {
      sourceId: "saa-001",
      certificationCode: "saa",
      categorySlug: "ec2",
      prompt: "What?",
      options: [
        { key: "A", text: "One" },
        { key: "B", text: "Two" },
      ],
      answers: ["A"],
      explanation: "Because A",
      access: "protected",
    }
    expect(questionSchema.parse(q).sourceId).toBe("saa-001")
  })

  it("quizQuerySchema has defaults", () => {
    expect(quizQuerySchema.parse({})).toEqual({ page: 1, pageSize: 20 })
  })

  it("quizQuestionSchema omits answers", () => {
    const qq = {
      id: "550e8400-e29b-41d4-a716-446655440000",
      categorySlug: "ec2",
      prompt: "Q?",
      options: [
        { key: "A", text: "X" },
        { key: "B", text: "Y" },
      ],
    }
    const parsed = quizQuestionSchema.parse(qq)
    expect(parsed).not.toHaveProperty("answers")
  })

  it("quizPaginationSchema validates page fields", () => {
    const p = { page: 1, pageSize: 20, totalQuestions: 100, totalPages: 5, category: null }
    expect(quizPaginationSchema.parse(p).totalPages).toBe(5)
  })

  it("quizResponseSchema validates full response", () => {
    const resp = {
      questions: [],
      pagination: { page: 1, pageSize: 20, totalQuestions: 0, totalPages: 0, category: null },
      categoryCounts: {},
    }
    expect(quizResponseSchema.parse(resp).questions).toHaveLength(0)
  })

  it("answerInputSchema requires at least one answer", () => {
    expect(answerInputSchema.safeParse({ selectedAnswers: [] }).success).toBeFalse()
    expect(answerInputSchema.parse({ selectedAnswers: ["B"] }).selectedAnswers).toEqual(["B"])
  })

  it("answerResultSchema validates a result", () => {
    const r = { correct: false, answers: ["C"], explanation: "Reason" }
    expect(answerResultSchema.parse(r).correct).toBeFalse()
  })
})

describe("baseline: progress exports are stable", () => {
  it("progressUpdateSchema parses valid update", () => {
    const u = {
      questionId: "550e8400-e29b-41d4-a716-446655440000",
      selectedAnswers: ["A"],
      correct: true,
    }
    expect(progressUpdateSchema.parse(u).correct).toBeTrue()
  })

  it("bookmarkInputSchema validates content types", () => {
    const b = { contentType: "question", contentId: "550e8400-e29b-41d4-a716-446655440000" }
    expect(bookmarkInputSchema.parse(b).contentType).toBe("question")
    expect(
      bookmarkInputSchema.safeParse({ contentType: "video", contentId: "abc" }).success,
    ).toBeFalse()
  })

  it("progressSummarySchema parses a summary", () => {
    const s = {
      certificationCode: "aif",
      attempted: 10,
      correct: 7,
      bookmarks: 3,
      updatedAt: "2026-01-01T00:00:00Z",
    }
    expect(progressSummarySchema.parse(s).attempted).toBe(10)
  })
})
