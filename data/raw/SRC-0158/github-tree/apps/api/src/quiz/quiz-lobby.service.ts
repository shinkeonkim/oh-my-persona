import {
  categories,
  type Database,
  questionProgress,
  questions,
  quizPreferences,
  quizSessions,
} from "@aws-study/db"
import {
  type CertificationCode,
  type QuizLobbyResponse,
  quizLobbyResponseSchema,
} from "@aws-study/shared"
import { Injectable } from "@nestjs/common"
import { and, asc, count, desc, eq, sql } from "drizzle-orm"

import { InjectDatabase } from "../database/database.module.js"

@Injectable()
export class QuizLobbyService {
  constructor(@InjectDatabase() private readonly database: Database) {}

  async get(userId: string, code: CertificationCode): Promise<QuizLobbyResponse> {
    const [rows, saved, active] = await Promise.all([
      this.database
        .select({
          slug: categories.slug,
          title: categories.title,
          total: count(questions.id),
          attempted: sql<number>`count(${questionProgress.questionId})::int`,
          correct: sql<number>`count(${questionProgress.questionId}) filter (where ${questionProgress.lastCorrect})::int`,
        })
        .from(categories)
        .leftJoin(
          questions,
          and(
            eq(questions.certificationCode, categories.certificationCode),
            eq(questions.categorySlug, categories.slug),
          ),
        )
        .leftJoin(
          questionProgress,
          and(eq(questionProgress.questionId, questions.id), eq(questionProgress.userId, userId)),
        )
        .where(eq(categories.certificationCode, code))
        .groupBy(categories.slug, categories.title, categories.order)
        .orderBy(asc(categories.order)),
      this.database
        .select()
        .from(quizPreferences)
        .where(and(eq(quizPreferences.userId, userId), eq(quizPreferences.certificationCode, code)))
        .limit(1),
      this.database
        .select({ id: quizSessions.id })
        .from(quizSessions)
        .where(
          and(
            eq(quizSessions.userId, userId),
            eq(quizSessions.certificationCode, code),
            eq(quizSessions.status, "active"),
          ),
        )
        .orderBy(desc(quizSessions.createdAt))
        .limit(1),
    ])
    const categoryStats = rows.map((row) => ({ ...row, wrong: row.attempted - row.correct }))
    const stats = categoryStats.reduce(
      (sum, row) => ({
        total: sum.total + row.total,
        attempted: sum.attempted + row.attempted,
        correct: sum.correct + row.correct,
        wrong: sum.wrong + row.wrong,
      }),
      { total: 0, attempted: 0, correct: 0, wrong: 0 },
    )
    const preference = saved[0] ?? {
      certificationCode: code,
      mode: "all" as const,
      order: "random" as const,
      questionLimit: null,
      categorySlugs: categoryStats.map((row) => row.slug),
    }
    return quizLobbyResponseSchema.parse({
      stats,
      categories: categoryStats,
      preference: {
        certificationCode: preference.certificationCode,
        mode: preference.mode,
        order: preference.order,
        questionLimit: preference.questionLimit,
        categorySlugs: preference.categorySlugs,
      },
      activeSessionId: active[0]?.id ?? null,
    })
  }
}
