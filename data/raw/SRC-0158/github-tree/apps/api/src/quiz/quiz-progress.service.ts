import {
  categories,
  type Database,
  questionProgress,
  questions,
  quizPreferences,
} from "@aws-study/db"
import {
  type CertificationCode,
  type QuizSessionConfig,
  type QuizWrongNote,
  quizWrongNotesSchema,
} from "@aws-study/shared"
import { BadRequestException, Injectable } from "@nestjs/common"
import { and, asc, eq, inArray } from "drizzle-orm"

import { InjectDatabase } from "../database/database.module.js"

@Injectable()
export class QuizProgressService {
  constructor(@InjectDatabase() private readonly database: Database) {}

  async savePreference(userId: string, input: QuizSessionConfig): Promise<void> {
    const rows = await this.database
      .select({ slug: categories.slug })
      .from(categories)
      .where(
        and(
          eq(categories.certificationCode, input.certificationCode),
          inArray(categories.slug, input.categorySlugs),
        ),
      )
    if (rows.length !== input.categorySlugs.length) {
      throw new BadRequestException("Unknown quiz category")
    }
    await this.database
      .insert(quizPreferences)
      .values({ userId, ...input })
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
  }

  async wrongNotes(userId: string, code: CertificationCode): Promise<readonly QuizWrongNote[]> {
    const rows = await this.database
      .select({
        questionId: questions.id,
        categorySlug: questions.categorySlug,
        prompt: questions.prompt,
        options: questions.options,
        answers: questions.answers,
        explanation: questions.explanation,
        selectedAnswers: questionProgress.selectedAnswers,
        updatedAt: questionProgress.updatedAt,
      })
      .from(questionProgress)
      .innerJoin(questions, eq(questions.id, questionProgress.questionId))
      .where(
        and(
          eq(questionProgress.userId, userId),
          eq(questionProgress.lastCorrect, false),
          eq(questions.certificationCode, code),
        ),
      )
      .orderBy(asc(questions.categorySlug), asc(questions.sourceId))
    return quizWrongNotesSchema.parse(
      rows.map((row) => ({ ...row, updatedAt: row.updatedAt.toISOString() })),
    )
  }

  async reset(userId: string, code: CertificationCode): Promise<void> {
    const questionIds = this.database
      .select({ id: questions.id })
      .from(questions)
      .where(eq(questions.certificationCode, code))
    await this.database
      .delete(questionProgress)
      .where(
        and(eq(questionProgress.userId, userId), inArray(questionProgress.questionId, questionIds)),
      )
  }
}
