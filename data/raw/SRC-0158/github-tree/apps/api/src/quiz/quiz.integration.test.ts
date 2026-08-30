import { afterAll, beforeAll, describe, expect, it } from "bun:test"
import {
  categories,
  createDatabase,
  questionProgress,
  questions,
  quizAttempts,
  quizSessions,
  users,
} from "@aws-study/db"
import { migrate } from "drizzle-orm/postgres-js/migrator"

import {
  connectionUrl,
  createDb,
  removeContainerIfExists,
  startContainer,
} from "../../../../packages/db/src/test-helpers"
import { QuizLobbyService } from "./quiz-lobby.service"
import { QuizProgressService } from "./quiz-progress.service"
import { QuizSessionService } from "./quiz-session.service"
import { QuizStateService } from "./quiz-state.service"

const CONTAINER = "quiz-service-test-postgres"
const PORT = 5437
const PASSWORD = "quiztest"
const DATABASE = "quiz_service"
const USER_ID = "10000000-0000-4000-8000-000000000001"
const QUESTION_1 = "20000000-0000-4000-8000-000000000001"
const QUESTION_2 = "20000000-0000-4000-8000-000000000002"
const MIGRATIONS = new URL("../../../../packages/db/drizzle", import.meta.url).pathname

function url(database: string): string {
  return connectionUrl(PORT, PASSWORD, database)
}

const database = createDatabase(url(DATABASE))
const lobbyService = new QuizLobbyService(database)
const progressService = new QuizProgressService(database)
const sessionService = new QuizSessionService(database)
const stateService = new QuizStateService(database)

describe("quiz service integration", () => {
  beforeAll(async () => {
    await removeContainerIfExists(CONTAINER)
    await startContainer(CONTAINER, PORT, PASSWORD)
    await createDb(url("postgres"), DATABASE)
    await migrate(database, { migrationsFolder: MIGRATIONS })
    await database.insert(users).values({
      id: USER_ID,
      email: "reader@example.com",
      displayName: "Reader",
      passwordHash: "hash",
      role: "reader",
    })
    await database.insert(categories).values([
      { certificationCode: "saa", slug: "compute", order: 1, title: "Compute" },
      { certificationCode: "saa", slug: "storage", order: 2, title: "Storage" },
    ])
    await database.insert(questions).values([
      {
        id: QUESTION_1,
        sourceId: "quiz-service-q1",
        certificationCode: "saa",
        categorySlug: "compute",
        prompt: "Compute question",
        options: [
          { key: "A", text: "Correct" },
          { key: "B", text: "Wrong" },
        ],
        answers: ["A"],
        explanation: "A is correct",
      },
      {
        id: QUESTION_2,
        sourceId: "quiz-service-q2",
        certificationCode: "saa",
        categorySlug: "storage",
        prompt: "Storage question",
        options: [
          { key: "A", text: "Wrong" },
          { key: "B", text: "Correct" },
        ],
        answers: ["B"],
        explanation: "B is correct",
      },
    ])
    await database.insert(questionProgress).values({
      userId: USER_ID,
      questionId: QUESTION_2,
      attempts: 1,
      correctAttempts: 0,
      lastCorrect: false,
      selectedAnswers: ["A"],
    })
  }, 60_000)

  afterAll(async () => {
    await removeContainerIfExists(CONTAINER)
  })

  it("returns per-category lobby statistics and default preferences", async () => {
    const lobby = await lobbyService.get(USER_ID, "saa")

    expect(lobby.stats).toEqual({ total: 2, attempted: 1, correct: 0, wrong: 1 })
    expect(lobby.categories).toEqual([
      { slug: "compute", title: "Compute", total: 1, attempted: 0, correct: 0, wrong: 0 },
      { slug: "storage", title: "Storage", total: 1, attempted: 1, correct: 0, wrong: 1 },
    ])
    expect(lobby.preference.categorySlugs).toEqual(["compute", "storage"])
    expect((await progressService.wrongNotes(USER_ID, "saa"))[0]?.questionId).toBe(QUESTION_2)
  })

  it("creates a wrong-only session, resumes it, and records a server-scored attempt", async () => {
    const started = await sessionService.start(USER_ID, {
      certificationCode: "saa",
      mode: "wrong",
      order: "sequential",
      questionLimit: null,
      categorySlugs: ["compute", "storage"],
      parentSessionId: null,
    })

    expect(started.status).toBe("active")
    expect(started.question?.questionId).toBe(QUESTION_2)
    await expect(
      sessionService.attempt(USER_ID, {
        sessionId: started.sessionId,
        questionId: QUESTION_2,
        selectedAnswers: ["E"],
      }),
    ).rejects.toThrow("Answer selection is not valid for this question")
    const feedback = await sessionService.attempt(USER_ID, {
      sessionId: started.sessionId,
      questionId: QUESTION_2,
      selectedAnswers: ["B"],
    })
    expect(feedback).toEqual({
      correct: true,
      answers: ["B"],
      explanation: "B is correct",
      completed: true,
    })

    const completed = await stateService.get(USER_ID, started.sessionId)
    expect(completed.status).toBe("completed")
    expect(completed.results).toEqual({
      correct: 1,
      total: 1,
      categories: [{ slug: "storage", correct: 1, total: 1 }],
    })
    expect(await database.select().from(quizAttempts)).toHaveLength(1)
    expect((await database.select().from(quizSessions))[0]?.status).toBe("completed")
  })

  it("resets progress for only the requested certification", async () => {
    await progressService.reset(USER_ID, "saa")
    expect((await lobbyService.get(USER_ID, "saa")).stats.attempted).toBe(0)
  })
})
