import { bookmarks, type Database, questionProgress, questions } from "@aws-study/db"
import type { AuthUser, BookmarkInput, ProgressUpdate } from "@aws-study/shared"
import { Injectable } from "@nestjs/common"
import { and, count, eq, sql } from "drizzle-orm"

import { InjectDatabase } from "../database/database.module.js"

@Injectable()
export class ProgressService {
  constructor(@InjectDatabase() private readonly database: Database) {}

  async record(user: AuthUser, input: ProgressUpdate): Promise<void> {
    await this.database
      .insert(questionProgress)
      .values({
        userId: user.id,
        questionId: input.questionId,
        attempts: 1,
        correctAttempts: input.correct ? 1 : 0,
        lastCorrect: input.correct,
        selectedAnswers: input.selectedAnswers,
      })
      .onConflictDoUpdate({
        target: [questionProgress.userId, questionProgress.questionId],
        set: {
          attempts: sql`${questionProgress.attempts} + 1`,
          correctAttempts: sql`${questionProgress.correctAttempts} + ${input.correct ? 1 : 0}`,
          lastCorrect: input.correct,
          selectedAnswers: input.selectedAnswers,
          updatedAt: new Date(),
        },
      })
  }

  async summary(user: AuthUser) {
    return this.database
      .select({
        certificationCode: questions.certificationCode,
        attempted: count(questionProgress.questionId),
        correct: sql<number>`sum(case when ${questionProgress.lastCorrect} then 1 else 0 end)::int`,
      })
      .from(questionProgress)
      .innerJoin(questions, eq(questionProgress.questionId, questions.id))
      .where(eq(questionProgress.userId, user.id))
      .groupBy(questions.certificationCode)
  }

  async toggleBookmark(
    user: AuthUser,
    input: BookmarkInput,
    certificationCode: "aif" | "clf" | "saa",
  ) {
    const where = and(
      eq(bookmarks.userId, user.id),
      eq(bookmarks.contentType, input.contentType),
      eq(bookmarks.contentId, input.contentId),
    )
    const [existing] = await this.database.select().from(bookmarks).where(where).limit(1)
    if (existing !== undefined) {
      await this.database.delete(bookmarks).where(where)
      return { bookmarked: false }
    }
    await this.database.insert(bookmarks).values({ userId: user.id, ...input, certificationCode })
    return { bookmarked: true }
  }
}
