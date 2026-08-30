import { categories, type Database, questions, studyNotes } from "@aws-study/db"
import {
  type AnswerResult,
  CERTIFICATIONS,
  type CertificationCode,
  type QuizResponse,
} from "@aws-study/shared"
import { Injectable, NotFoundException } from "@nestjs/common"
import { and, asc, count, eq } from "drizzle-orm"

import { InjectDatabase } from "../database/database.module.js"

@Injectable()
export class ContentService {
  constructor(@InjectDatabase() private readonly database: Database) {}

  certifications(): typeof CERTIFICATIONS {
    return CERTIFICATIONS
  }

  async listCategories(code: CertificationCode): Promise<
    {
      id: string
      certificationCode: string
      slug: string
      order: number
      title: string
      summary: string
    }[]
  > {
    return this.database
      .select({
        id: categories.id,
        certificationCode: categories.certificationCode,
        slug: categories.slug,
        order: categories.order,
        title: categories.title,
        summary: categories.summary,
      })
      .from(categories)
      .innerJoin(
        studyNotes,
        and(
          eq(studyNotes.certificationCode, categories.certificationCode),
          eq(studyNotes.categorySlug, categories.slug),
        ),
      )
      .where(eq(categories.certificationCode, code))
      .orderBy(asc(categories.order))
  }

  async note(code: CertificationCode, slug: string): Promise<typeof studyNotes.$inferSelect> {
    const [note] = await this.database
      .select()
      .from(studyNotes)
      .where(
        and(
          eq(studyNotes.certificationCode, code),
          eq(studyNotes.slug, slug),
          eq(studyNotes.access, "public"),
        ),
      )
      .limit(1)
    if (note === undefined) throw new NotFoundException("Study note not found")
    return note
  }

  async quiz(
    code: CertificationCode,
    page: number,
    pageSize: number,
    category?: string,
  ): Promise<QuizResponse> {
    const baseWhere = category
      ? and(eq(questions.certificationCode, code), eq(questions.categorySlug, category))
      : eq(questions.certificationCode, code)

    const [totalRow, countRows, rows] = await Promise.all([
      this.database.select({ value: count() }).from(questions).where(baseWhere),
      this.database
        .select({ categorySlug: questions.categorySlug, value: count() })
        .from(questions)
        .where(eq(questions.certificationCode, code))
        .groupBy(questions.categorySlug),
      this.database
        .select({
          id: questions.id,
          categorySlug: questions.categorySlug,
          prompt: questions.prompt,
          options: questions.options,
        })
        .from(questions)
        .where(baseWhere)
        .orderBy(asc(questions.categorySlug), asc(questions.sourceId))
        .limit(pageSize)
        .offset((page - 1) * pageSize),
    ])

    const totalQuestions = totalRow[0]?.value ?? 0
    const totalPages = Math.ceil(totalQuestions / pageSize)
    const categoryCounts: Record<string, number> = {}
    for (const row of countRows) {
      categoryCounts[row.categorySlug] = row.value
    }

    return {
      questions: rows.map((row) => ({
        id: row.id,
        categorySlug: row.categorySlug,
        prompt: row.prompt,
        options: [...row.options],
      })),
      pagination: { page, pageSize, totalQuestions, totalPages, category: category ?? null },
      categoryCounts,
    }
  }

  async answer(questionId: string, selected: readonly string[]): Promise<AnswerResult> {
    const [question] = await this.database
      .select()
      .from(questions)
      .where(eq(questions.id, questionId))
      .limit(1)
    if (question === undefined) throw new NotFoundException("Question not found")
    const expected = [...question.answers].sort()
    const submitted = [...selected].sort()
    return {
      correct:
        expected.length === submitted.length &&
        expected.every((answer, index) => answer === submitted[index]),
      answers: [...question.answers],
      explanation: question.explanation,
    }
  }
}
