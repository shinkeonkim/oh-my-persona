import { type Database, questions, quizAttempts, quizQueue, quizSessions } from "@aws-study/db"
import {
  type QuizResults,
  type QuizSessionState,
  quizResultsSchema,
  quizSessionStateSchema,
} from "@aws-study/shared"
import { ConflictException, GoneException, Injectable, NotFoundException } from "@nestjs/common"
import { and, asc, count, eq, sql } from "drizzle-orm"

import { InjectDatabase } from "../database/database.module.js"

@Injectable()
export class QuizStateService {
  constructor(@InjectDatabase() private readonly database: Database) {}

  async get(userId: string, sessionId: string): Promise<QuizSessionState> {
    const sessions = await this.database
      .select({
        status: quizSessions.status,
        certificationCode: quizSessions.certificationCode,
        mode: quizSessions.mode,
        order: quizSessions.order,
        questionLimit: quizSessions.questionLimit,
        categorySlugs: quizSessions.categorySlugs,
      })
      .from(quizSessions)
      .where(and(eq(quizSessions.id, sessionId), eq(quizSessions.userId, userId)))
      .limit(1)
    const session = sessions[0]
    if (session === undefined) throw new NotFoundException("Quiz session not found")
    if (session.status === "abandoned") throw new GoneException("Quiz session was abandoned")
    const [queueCount, attemptCount] = await Promise.all([
      this.database
        .select({ value: count() })
        .from(quizQueue)
        .where(eq(quizQueue.sessionId, sessionId)),
      this.database
        .select({ value: count() })
        .from(quizAttempts)
        .where(and(eq(quizAttempts.sessionId, sessionId), eq(quizAttempts.userId, userId))),
    ])
    const total = queueCount[0]?.value ?? 0
    const position = attemptCount[0]?.value ?? 0
    const config = {
      certificationCode: session.certificationCode,
      mode: session.mode,
      order: session.order,
      questionLimit: session.questionLimit,
      categorySlugs: session.categorySlugs,
    }
    if (session.status === "completed") {
      return quizSessionStateSchema.parse({
        sessionId,
        status: "completed",
        position,
        totalQuestions: total,
        config,
        question: null,
        results: await this.results(userId, sessionId),
      })
    }
    const rows = await this.database
      .select({
        questionId: questions.id,
        position: quizQueue.position,
        categorySlug: questions.categorySlug,
        prompt: questions.prompt,
        options: questions.options,
        answers: questions.answers,
      })
      .from(quizQueue)
      .innerJoin(questions, eq(questions.id, quizQueue.questionId))
      .where(and(eq(quizQueue.sessionId, sessionId), eq(quizQueue.position, position)))
      .limit(1)
    const question = rows[0]
    if (question === undefined) throw new ConflictException("Quiz session has no current question")
    return quizSessionStateSchema.parse({
      sessionId,
      status: "active",
      position,
      totalQuestions: total,
      config,
      question: {
        questionId: question.questionId,
        position: question.position,
        categorySlug: question.categorySlug,
        prompt: question.prompt,
        answerCount: question.answers.length,
        options: [...question.options],
      },
      results: null,
    })
  }

  private async results(userId: string, sessionId: string): Promise<QuizResults> {
    const rows = await this.database
      .select({
        slug: questions.categorySlug,
        total: count(),
        correct: sql<number>`count(*) filter (where ${quizAttempts.correct})::int`,
      })
      .from(quizAttempts)
      .innerJoin(questions, eq(questions.id, quizAttempts.questionId))
      .where(and(eq(quizAttempts.sessionId, sessionId), eq(quizAttempts.userId, userId)))
      .groupBy(questions.categorySlug)
      .orderBy(asc(questions.categorySlug))
    return quizResultsSchema.parse({
      correct: rows.reduce((sum, row) => sum + row.correct, 0),
      total: rows.reduce((sum, row) => sum + row.total, 0),
      categories: rows,
    })
  }
}
