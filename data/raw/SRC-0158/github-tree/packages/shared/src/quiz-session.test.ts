import { describe, expect, it } from "bun:test"

import {
  quizAttemptInputSchema,
  quizAttemptResultSchema,
  quizLobbyResponseSchema,
  quizPreferenceSchema,
  quizQueueItemSchema,
  quizSessionConfigSchema,
  quizSessionSchema,
  quizSessionStartInputSchema,
  quizSessionStateSchema,
  quizWrongNotesSchema,
} from "./quiz-session"

const SESSION_ID = "10000000-0000-4000-8000-000000000001"
const QUESTION_ID = "20000000-0000-4000-8000-000000000001"
const USER_ID = "30000000-0000-4000-8000-000000000001"

describe("quiz session contracts", () => {
  it("parses a cert-scoped setup with unlimited questions", () => {
    const result = quizSessionConfigSchema.safeParse({
      certificationCode: "saa",
      mode: "unseen",
      order: "random",
      questionLimit: null,
      categorySlugs: ["storage", "networking"],
    })
    expect(result.success).toBeTrue()
  })

  it("rejects duplicate categories and non-positive limits", () => {
    expect(
      quizSessionConfigSchema.safeParse({
        certificationCode: "aif",
        mode: "all",
        order: "sequential",
        questionLimit: 0,
        categorySlugs: ["domain-1", "domain-1"],
      }).success,
    ).toBeFalse()
  })

  it("rejects answer-bearing queue payloads", () => {
    const result = quizQueueItemSchema.safeParse({
      questionId: QUESTION_ID,
      position: 0,
      categorySlug: "storage",
      prompt: "Which service stores objects?",
      answerCount: 1,
      options: [
        { key: "A", text: "Amazon S3" },
        { key: "B", text: "Amazon EC2" },
      ],
      answers: ["A"],
    })
    expect(result.success).toBeFalse()
  })

  it("parses an attempt without accepting correctness from the client", () => {
    expect(
      quizAttemptInputSchema.safeParse({
        sessionId: SESSION_ID,
        questionId: QUESTION_ID,
        selectedAnswers: ["A", "C"],
      }).success,
    ).toBeTrue()
    expect(
      quizAttemptInputSchema.safeParse({
        sessionId: SESSION_ID,
        questionId: QUESTION_ID,
        selectedAnswers: ["A"],
        correct: true,
      }).success,
    ).toBeFalse()
  })

  it("parses per-user per-cert preferences", () => {
    expect(
      quizPreferenceSchema.safeParse({
        userId: USER_ID,
        certificationCode: "clf",
        mode: "wrong",
        order: "sequential",
        questionLimit: 25,
        categorySlugs: ["security"],
      }).success,
    ).toBeTrue()
  })

  it("parses a restarted session with a parent link", () => {
    expect(
      quizSessionSchema.safeParse({
        id: SESSION_ID,
        userId: USER_ID,
        parentSessionId: "40000000-0000-4000-8000-000000000001",
        certificationCode: "saa",
        mode: "all",
        order: "random",
        questionLimit: 65,
        categorySlugs: ["compute"],
        status: "active",
        createdAt: "2026-08-04T00:00:00.000Z",
        completedAt: null,
      }).success,
    ).toBeTrue()
  })

  it("parses a lobby with category progress, preferences, and a resumable session", () => {
    const result = quizLobbyResponseSchema.safeParse({
      stats: { total: 100, attempted: 40, correct: 30, wrong: 10 },
      categories: [
        { slug: "storage", title: "Storage", total: 60, attempted: 20, correct: 15, wrong: 5 },
        {
          slug: "networking",
          title: "Networking",
          total: 40,
          attempted: 20,
          correct: 15,
          wrong: 5,
        },
      ],
      preference: {
        certificationCode: "saa",
        mode: "wrong",
        order: "sequential",
        questionLimit: 25,
        categorySlugs: ["storage"],
      },
      activeSessionId: SESSION_ID,
    })

    expect(result.success).toBeTrue()
  })

  it("parses session start and current-question state without answer-bearing data", () => {
    expect(
      quizSessionStartInputSchema.safeParse({
        certificationCode: "saa",
        mode: "all",
        order: "random",
        questionLimit: 65,
        categorySlugs: ["storage"],
        parentSessionId: null,
      }).success,
    ).toBeTrue()

    const state = quizSessionStateSchema.safeParse({
      sessionId: SESSION_ID,
      status: "active",
      position: 0,
      totalQuestions: 65,
      config: {
        certificationCode: "saa",
        mode: "all",
        order: "random",
        questionLimit: 65,
        categorySlugs: ["storage"],
      },
      question: {
        questionId: QUESTION_ID,
        position: 0,
        categorySlug: "storage",
        prompt: "Which service stores objects?",
        answerCount: 1,
        options: [
          { key: "A", text: "Amazon S3" },
          { key: "B", text: "Amazon EC2" },
        ],
      },
      results: null,
    })

    expect(state.success).toBeTrue()
  })

  it("rejects answer material in active session state and parses post-submit feedback", () => {
    expect(
      quizSessionStateSchema.safeParse({
        sessionId: SESSION_ID,
        status: "active",
        position: 0,
        totalQuestions: 1,
        config: {
          certificationCode: "saa",
          mode: "all",
          order: "random",
          questionLimit: 1,
          categorySlugs: ["storage"],
        },
        question: {
          questionId: QUESTION_ID,
          position: 0,
          categorySlug: "storage",
          prompt: "Which service stores objects?",
          answerCount: 1,
          options: [
            { key: "A", text: "Amazon S3" },
            { key: "B", text: "Amazon EC2" },
          ],
          answers: ["A"],
        },
        results: null,
      }).success,
    ).toBeFalse()

    expect(
      quizAttemptResultSchema.safeParse({
        correct: true,
        answers: ["A"],
        explanation: "Amazon S3 stores objects.",
        completed: true,
      }).success,
    ).toBeTrue()
  })

  it("parses exportable wrong notes only after progress exists", () => {
    expect(
      quizWrongNotesSchema.safeParse([
        {
          questionId: QUESTION_ID,
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
      ]).success,
    ).toBeTrue()
  })
})
