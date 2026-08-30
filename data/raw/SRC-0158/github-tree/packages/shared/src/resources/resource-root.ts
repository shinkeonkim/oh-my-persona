import { z } from "zod"

/** Slug: lowercase alphanumeric + hyphens, 2-80 chars. */
export const canonicalSlugSchema = z.string().regex(/^[a-z0-9][a-z0-9-]{0,78}[a-z0-9]$/, {
  message: "Slug must be 2-80 lowercase alphanumeric/hyphen characters",
})

export const difficultySchema = z.enum(["foundation", "advanced", "applied"])

export const canonicalResourceSchema = z.object({
  slug: canonicalSlugSchema,
  title: z.string().min(1).max(200),
  summary: z.string().min(1).max(1000),
  difficulty: difficultySchema,
  order: z.number().int().nonnegative(),
  prerequisites: z.array(canonicalSlugSchema).readonly(),
})

export type CanonicalSlug = z.infer<typeof canonicalSlugSchema>
export type Difficulty = z.infer<typeof difficultySchema>
export type CanonicalResource = z.infer<typeof canonicalResourceSchema>
