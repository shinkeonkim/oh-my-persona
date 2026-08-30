import { describe, expect, it } from "bun:test"
import { getTableName } from "drizzle-orm"

import { quizAttempts, quizPreferences, quizQueue, quizSessions } from "./schema"

describe("quiz persistence schema", () => {
  it("exposes stable session, queue, attempt, and preference table names", () => {
    expect([quizSessions, quizQueue, quizAttempts, quizPreferences].map(getTableName)).toEqual([
      "quiz_sessions",
      "quiz_queue",
      "quiz_attempts",
      "quiz_preferences",
    ])
  })

  it("stores ordered session questions without answer columns", () => {
    expect(quizQueue.sessionId.name).toBe("session_id")
    expect(quizQueue.position.name).toBe("position")
    expect(quizQueue.questionId.name).toBe("question_id")
    expect(Object.keys(quizQueue)).not.toContain("answers")
  })

  it("scopes attempts to session, user, and question", () => {
    expect(quizAttempts.sessionId.notNull).toBeTrue()
    expect(quizAttempts.userId.notNull).toBeTrue()
    expect(quizAttempts.questionId.notNull).toBeTrue()
    expect(quizAttempts.selectedAnswers.notNull).toBeTrue()
  })

  it("scopes preferences to user and certification", () => {
    expect(quizPreferences.userId.notNull).toBeTrue()
    expect(quizPreferences.certificationCode.notNull).toBeTrue()
    expect(quizPreferences.categorySlugs.notNull).toBeTrue()
  })

  it("stores restart parent and cert-scoped session configuration", () => {
    expect(quizSessions.parentSessionId.name).toBe("parent_session_id")
    expect(quizSessions.certificationCode.name).toBe("certification_code")
    expect(quizSessions.questionLimit.name).toBe("question_limit")
    expect(quizSessions.categorySlugs.name).toBe("category_slugs")
  })
})
