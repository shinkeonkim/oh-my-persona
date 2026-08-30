import {
  categories,
  type Database,
  questionProgress,
  questions,
  quizAttempts,
  quizPreferences,
  quizQueue,
  quizSessions,
} from "@aws-study/db"
import {
  type QuizAttemptInput,
  type QuizAttemptResult,
  type QuizSessionStartInput,
  type QuizSessionState,
  quizAttemptResultSchema,
  quizSessionStateSchema,
} from "@aws-study/shared"
import {
  BadRequestException,
  ConflictException,
  Injectable,
  NotFoundException,
} from "@nestjs/common"
import { and, asc, count, eq, inArray, isNull, sql } from "drizzle-orm"

import { InjectDatabase } from "../database/database.module.js"

@Injectable()
export class QuizSessionService {
  constructor(@InjectDatabase() private readonly database: Database) {}

  async start(userId: string, input: QuizSessionStartInput): Promise<QuizSessionState> {
    const state = await this.database.transaction(async (tx) => {
      const validCategories = await tx
        .select({ slug: categories.slug })
        .from(categories)
        .where(
          and(
            eq(categories.certificationCode, input.certificationCode),
            inArray(categories.slug, input.categorySlugs),
          ),
        )
      if (validCategories.length !== input.categorySlugs.length) {
        throw new BadRequestException("Unknown quiz category")
      }
      if (input.parentSessionId !== null) {
        const parent = await tx
          .select({ id: quizSessions.id })
          .from(quizSessions)
          .where(
            and(
              eq(quizSessions.id, input.parentSessionId),
              eq(quizSessions.userId, userId),
              eq(quizSessions.certificationCode, input.certificationCode),
            ),
          )
          .limit(1)
        if (parent[0] === undefined) throw new BadRequestException("Invalid parent quiz session")
      }
      const progressJoin = and(
        eq(questionProgress.questionId, questions.id),
        eq(questionProgress.userId, userId),
      )
      const baseWhere = and(
        eq(questions.certificationCode, input.certificationCode),
        inArray(questions.categorySlug, input.categorySlugs),
      )
      let eligibleWhere = baseWhere
      switch (input.mode) {
        case "all":
          break
        case "unseen":
          eligibleWhere = and(baseWhere, isNull(questionProgress.questionId))
          break
        case "wrong":
          eligibleWhere = and(baseWhere, eq(questionProgress.lastCorrect, false))
          break
      }
      const baseQuery = tx
        .select({
          id: questions.id,
          categorySlug: questions.categorySlug,
          prompt: questions.prompt,
          options: questions.options,
          answers: questions.answers,
        })
        .from(questions)
        .leftJoin(questionProgress, progressJoin)
        .where(eligibleWhere)
        .limit(input.questionLimit ?? 10_000)
      const selected =
        input.order === "random"
          ? await baseQuery.orderBy(sql`random()`)
          : await baseQuery.orderBy(asc(questions.categorySlug), asc(questions.sourceId))
      if (selected.length === 0) throw new BadRequestException("No questions match this setup")
      await tx
        .insert(quizPreferences)
        .values({
          userId,
          certificationCode: input.certificationCode,
          mode: input.mode,
          order: input.order,
          questionLimit: input.questionLimit,
          categorySlugs: input.categorySlugs,
        })
        .onConflictDoUpdate({
          target: [quizPreferences.userId, quizPreferences.certificationCode],
          set: {
            mode: input.mode,
            order: input.order,
            questionLimit: input.questionLimit,
            categorySlugs: input.categorySlugs,
            updatedAt: new Date(),
          },
        })
      const sessions = await tx
        .insert(quizSessions)
        .values({ userId, ...input })
        .returning({ id: quizSessions.id })
      const session = sessions[0]
      if (session === undefined) throw new ConflictException("Quiz session was not created")
      await tx.insert(quizQueue).values(
        selected.map((question, position) => ({
          sessionId: session.id,
          position,
          questionId: question.id,
        })),
      )
      const first = selected[0]
      if (first === undefined) throw new ConflictException("Quiz queue was not created")
      return {
        sessionId: session.id,
        status: "active" as const,
        position: 0,
        totalQuestions: selected.length,
        config: {
          certificationCode: input.certificationCode,
          mode: input.mode,
          order: input.order,
          questionLimit: input.questionLimit,
          categorySlugs: input.categorySlugs,
        },
        question: {
          questionId: first.id,
          position: 0,
          categorySlug: first.categorySlug,
          prompt: first.prompt,
          answerCount: first.answers.length,
          options: [...first.options],
        },
        results: null,
      }
    })
    return quizSessionStateSchema.parse(state)
  }

  async attempt(userId: string, input: QuizAttemptInput): Promise<QuizAttemptResult> {
    const result = await this.database.transaction(async (tx) => {
      const sessions = await tx
        .select({ status: quizSessions.status })
        .from(quizSessions)
        .where(and(eq(quizSessions.id, input.sessionId), eq(quizSessions.userId, userId)))
        .limit(1)
      if (sessions[0]?.status !== "active") throw new ConflictException("Quiz session inactive")
      const [queueCount, attemptCount] = await Promise.all([
        tx
          .select({ value: count() })
          .from(quizQueue)
          .where(eq(quizQueue.sessionId, input.sessionId)),
        tx
          .select({ value: count() })
          .from(quizAttempts)
          .where(and(eq(quizAttempts.sessionId, input.sessionId), eq(quizAttempts.userId, userId))),
      ])
      const total = queueCount[0]?.value ?? 0
      const position = attemptCount[0]?.value ?? 0
      const rows = await tx
        .select({
          questionId: questions.id,
          options: questions.options,
          answers: questions.answers,
          explanation: questions.explanation,
        })
        .from(quizQueue)
        .innerJoin(questions, eq(questions.id, quizQueue.questionId))
        .where(and(eq(quizQueue.sessionId, input.sessionId), eq(quizQueue.position, position)))
        .limit(1)
      const question = rows[0]
      if (question === undefined || question.questionId !== input.questionId) {
        throw new ConflictException("Answer is not for the current question")
      }
      const optionKeys = new Set(question.options.map((option) => option.key))
      if (input.selectedAnswers.some((answer) => !optionKeys.has(answer))) {
        throw new BadRequestException("Answer selection is not valid for this question")
      }
      const expected = [...question.answers].sort()
      const submitted = [...input.selectedAnswers].sort()
      const correct =
        expected.length === submitted.length &&
        expected.every((answer, index) => answer === submitted[index])
      await tx.insert(quizAttempts).values({
        sessionId: input.sessionId,
        userId,
        questionId: input.questionId,
        selectedAnswers: input.selectedAnswers,
        correct,
      })
      await tx
        .insert(questionProgress)
        .values({
          userId,
          questionId: input.questionId,
          attempts: 1,
          correctAttempts: correct ? 1 : 0,
          lastCorrect: correct,
          selectedAnswers: input.selectedAnswers,
        })
        .onConflictDoUpdate({
          target: [questionProgress.userId, questionProgress.questionId],
          set: {
            attempts: sql`${questionProgress.attempts} + 1`,
            correctAttempts: sql`${questionProgress.correctAttempts} + ${correct ? 1 : 0}`,
            lastCorrect: correct,
            selectedAnswers: input.selectedAnswers,
            updatedAt: new Date(),
          },
        })
      const completed = position + 1 === total
      if (completed) {
        await tx
          .update(quizSessions)
          .set({ status: "completed", completedAt: new Date() })
          .where(and(eq(quizSessions.id, input.sessionId), eq(quizSessions.userId, userId)))
      }
      return { correct, answers: question.answers, explanation: question.explanation, completed }
    })
    return quizAttemptResultSchema.parse(result)
  }

  async abandon(userId: string, sessionId: string): Promise<void> {
    const rows = await this.database
      .update(quizSessions)
      .set({ status: "abandoned", completedAt: new Date() })
      .where(
        and(
          eq(quizSessions.id, sessionId),
          eq(quizSessions.userId, userId),
          eq(quizSessions.status, "active"),
        ),
      )
      .returning({ id: quizSessions.id })
    if (rows[0] === undefined) throw new NotFoundException("Active quiz session not found")
  }
}
