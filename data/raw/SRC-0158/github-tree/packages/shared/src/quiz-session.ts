import { z } from "zod"

import { certificationCodeSchema } from "./certifications"
import { questionIdSchema, questionOptionSchema } from "./content"

export const quizFilterModeSchema = z.enum(["all", "unseen", "wrong"])
export const quizOrderSchema = z.enum(["random", "sequential"])
export const quizSessionStatusSchema = z.enum(["active", "completed", "abandoned"])
export const quizSessionIdSchema = z.string().uuid()

const categorySlugsSchema = z
  .array(z.string().min(1).max(100))
  .min(1)
  .refine((slugs) => new Set(slugs).size === slugs.length, "Duplicate category slugs")
  .readonly()

const selectedAnswersSchema = z
  .array(z.string().regex(/^[A-E]$/))
  .min(1)
  .max(5)
  .refine((answers) => new Set(answers).size === answers.length, "Duplicate answers")
  .readonly()

const configShape = {
  certificationCode: certificationCodeSchema,
  mode: quizFilterModeSchema,
  order: quizOrderSchema,
  questionLimit: z.number().int().positive().nullable(),
  categorySlugs: categorySlugsSchema,
}

export const quizSessionConfigSchema = z.strictObject(configShape)

export const quizSessionStartInputSchema = quizSessionConfigSchema.extend({
  parentSessionId: z.string().uuid().nullable().default(null),
})

export const quizQueueItemSchema = z.strictObject({
  questionId: questionIdSchema,
  position: z.number().int().nonnegative(),
  categorySlug: z.string().min(1).max(100),
  prompt: z.string().min(1),
  answerCount: z.number().int().min(1).max(5),
  options: z.array(questionOptionSchema).min(2).max(5).readonly(),
})

export const quizAttemptInputSchema = z.strictObject({
  sessionId: quizSessionIdSchema,
  questionId: questionIdSchema,
  selectedAnswers: selectedAnswersSchema,
})

export const quizPreferenceSchema = z.strictObject({
  userId: z.string().uuid(),
  ...configShape,
})

export const quizSessionSchema = z.strictObject({
  id: quizSessionIdSchema,
  userId: z.string().uuid(),
  parentSessionId: z.string().uuid().nullable(),
  ...configShape,
  status: quizSessionStatusSchema,
  createdAt: z.string().datetime(),
  completedAt: z.string().datetime().nullable(),
})

const quizProgressStatsSchema = z.strictObject({
  total: z.number().int().nonnegative(),
  attempted: z.number().int().nonnegative(),
  correct: z.number().int().nonnegative(),
  wrong: z.number().int().nonnegative(),
})

export const quizCategoryProgressSchema = quizProgressStatsSchema.extend({
  slug: z.string().min(1),
  title: z.string().min(1),
})

export const quizLobbyResponseSchema = z.strictObject({
  stats: quizProgressStatsSchema,
  categories: z.array(quizCategoryProgressSchema),
  preference: quizSessionConfigSchema,
  activeSessionId: z.string().uuid().nullable(),
})

export const quizCategoryResultSchema = z.strictObject({
  slug: z.string().min(1),
  correct: z.number().int().nonnegative(),
  total: z.number().int().nonnegative(),
})

export const quizResultsSchema = z.strictObject({
  correct: z.number().int().nonnegative(),
  total: z.number().int().nonnegative(),
  categories: z.array(quizCategoryResultSchema),
})

const quizSessionStateBase = {
  sessionId: quizSessionIdSchema,
  position: z.number().int().nonnegative(),
  totalQuestions: z.number().int().positive(),
  config: quizSessionConfigSchema,
}

export const quizSessionStateSchema = z.discriminatedUnion("status", [
  z.strictObject({
    ...quizSessionStateBase,
    status: z.literal("active"),
    question: quizQueueItemSchema,
    results: z.null(),
  }),
  z.strictObject({
    ...quizSessionStateBase,
    status: z.literal("completed"),
    question: z.null(),
    results: quizResultsSchema,
  }),
])

export const quizAttemptResultSchema = z.strictObject({
  correct: z.boolean(),
  answers: selectedAnswersSchema,
  explanation: z.string().min(1),
  completed: z.boolean(),
})

export const quizWrongNoteSchema = z.strictObject({
  questionId: questionIdSchema,
  categorySlug: z.string().min(1),
  prompt: z.string().min(1),
  options: z.array(questionOptionSchema).min(2).max(5).readonly(),
  answers: selectedAnswersSchema,
  explanation: z.string().min(1),
  selectedAnswers: selectedAnswersSchema,
  updatedAt: z.string().datetime(),
})

export const quizWrongNotesSchema = z.array(quizWrongNoteSchema)

export type QuizFilterMode = z.infer<typeof quizFilterModeSchema>
export type QuizOrder = z.infer<typeof quizOrderSchema>
export type QuizSessionStatus = z.infer<typeof quizSessionStatusSchema>
export type QuizSessionConfig = z.infer<typeof quizSessionConfigSchema>
export type QuizSessionStartInput = z.infer<typeof quizSessionStartInputSchema>
export type QuizQueueItem = z.infer<typeof quizQueueItemSchema>
export type QuizAttemptInput = z.infer<typeof quizAttemptInputSchema>
export type QuizPreference = z.infer<typeof quizPreferenceSchema>
export type QuizSession = z.infer<typeof quizSessionSchema>
export type QuizCategoryProgress = z.infer<typeof quizCategoryProgressSchema>
export type QuizLobbyResponse = z.infer<typeof quizLobbyResponseSchema>
export type QuizResults = z.infer<typeof quizResultsSchema>
export type QuizSessionState = z.infer<typeof quizSessionStateSchema>
export type QuizAttemptResult = z.infer<typeof quizAttemptResultSchema>
export type QuizWrongNote = z.infer<typeof quizWrongNoteSchema>
