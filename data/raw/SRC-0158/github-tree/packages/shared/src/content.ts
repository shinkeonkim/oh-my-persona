import { z } from "zod"

import { certificationCodeSchema, contentAccessSchema } from "./certifications"

export const categorySchema = z.object({
  slug: z.string().min(1),
  certificationCode: certificationCodeSchema,
  order: z.number().int().nonnegative(),
  title: z.string().min(1),
  summary: z.string(),
})

export const studyNoteSchema = z.object({
  slug: z.string().min(1),
  certificationCode: certificationCodeSchema,
  categorySlug: z.string().min(1),
  title: z.string().min(1),
  markdown: z.string().min(1),
  access: contentAccessSchema,
})

export const questionOptionSchema = z.object({
  key: z.string().regex(/^[A-E]$/),
  text: z.string().min(1),
})

export const questionSchema = z.object({
  sourceId: z.string().min(1),
  certificationCode: certificationCodeSchema,
  categorySlug: z.string().min(1),
  prompt: z.string().min(1),
  options: z.array(questionOptionSchema).min(2).max(5),
  answers: z.array(z.string().regex(/^[A-E]$/)).min(1),
  explanation: z.string().min(1),
  access: contentAccessSchema,
})

export const quizQuerySchema = z.object({
  category: z.string().min(1).optional(),
  page: z.coerce.number().int().min(1).default(1),
  pageSize: z.coerce.number().int().min(1).max(50).default(20),
})

export const questionIdSchema = z.string().uuid()

export const quizQuestionSchema = z.object({
  id: questionIdSchema,
  categorySlug: z.string().min(1),
  prompt: z.string().min(1),
  options: z.array(questionOptionSchema).min(2).max(5),
})

export const quizPaginationSchema = z.object({
  page: z.number().int().min(1),
  pageSize: z.number().int().min(1).max(50),
  totalQuestions: z.number().int().nonnegative(),
  totalPages: z.number().int().nonnegative(),
  category: z.string().nullable(),
})

export const quizResponseSchema = z.object({
  questions: z.array(quizQuestionSchema),
  pagination: quizPaginationSchema,
  categoryCounts: z.record(z.string(), z.number().int().nonnegative()),
})

export const answerInputSchema = z.object({
  selectedAnswers: z.array(z.string().regex(/^[A-E]$/)).min(1),
})

export const answerResultSchema = z.object({
  correct: z.boolean(),
  answers: z.array(z.string().regex(/^[A-E]$/)).min(1),
  explanation: z.string().min(1),
})

export type Category = z.infer<typeof categorySchema>
export type StudyNote = z.infer<typeof studyNoteSchema>
export type Question = z.infer<typeof questionSchema>
export type QuizQuery = z.infer<typeof quizQuerySchema>
export type QuizQuestion = z.infer<typeof quizQuestionSchema>
export type QuizPagination = z.infer<typeof quizPaginationSchema>
export type QuizResponse = z.infer<typeof quizResponseSchema>
export type AnswerInput = z.infer<typeof answerInputSchema>
export type AnswerResult = z.infer<typeof answerResultSchema>
