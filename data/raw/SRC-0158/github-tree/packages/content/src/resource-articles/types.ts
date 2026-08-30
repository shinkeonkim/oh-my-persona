import { canonicalSlugSchema, difficultySchema } from "@aws-study/shared"
import { z } from "zod"

export const resourceArticleSchema = z.strictObject({
  slug: canonicalSlugSchema,
  title: z.string().min(1),
  difficulty: difficultySchema,
  markdown: z.string().min(1),
  officialUrl: z.string().url(),
  readingMinutes: z.number().int().min(3).max(8),
})

export type ResourceArticle = z.infer<typeof resourceArticleSchema>
