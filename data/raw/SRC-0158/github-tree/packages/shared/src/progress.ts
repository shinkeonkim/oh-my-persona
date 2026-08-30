import { z } from "zod"

import { certificationCodeSchema } from "./certifications"

export const progressUpdateSchema = z.object({
  questionId: z.string().uuid(),
  selectedAnswers: z.array(z.string().regex(/^[A-E]$/)).min(1),
  correct: z.boolean(),
})

export const bookmarkInputSchema = z.object({
  contentType: z.enum(["question", "study-note"]),
  contentId: z.string().uuid(),
})

export const progressSummarySchema = z.object({
  certificationCode: certificationCodeSchema,
  attempted: z.number().int().nonnegative(),
  correct: z.number().int().nonnegative(),
  bookmarks: z.number().int().nonnegative(),
  updatedAt: z.string().datetime().nullable(),
})

export type ProgressUpdate = z.infer<typeof progressUpdateSchema>
export type BookmarkInput = z.infer<typeof bookmarkInputSchema>
export type ProgressSummary = z.infer<typeof progressSummarySchema>
