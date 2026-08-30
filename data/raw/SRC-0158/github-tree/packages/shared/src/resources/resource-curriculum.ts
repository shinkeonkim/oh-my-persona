import { z } from "zod"

import { certificationCodeSchema } from "../certifications"
import { canonicalSlugSchema, difficultySchema } from "./resource-root"

export const certDomainSchema = z.object({
  certificationCode: certificationCodeSchema,
  domainCode: z.string().min(1).max(20),
  domainTitle: z.string().min(1).max(200),
  weight: z.number().int().min(1).max(100),
})

export const certResourceRelevanceSchema = z.object({
  resourceSlug: canonicalSlugSchema,
  certificationCode: certificationCodeSchema,
  domainCode: z.string().min(1).max(20),
})

export const curriculumEntrySchema = z.object({
  slug: canonicalSlugSchema,
  difficulty: difficultySchema,
  order: z.number().int().nonnegative(),
  certRelevance: z.array(certResourceRelevanceSchema).readonly(),
})

export const coverageClassificationSchema = z.enum([
  "study-note",
  "concept-view",
  "resource-section",
  "question",
  "linked-pdf",
  "root-pdf",
])

export const coverageManifestSchema = z.object({
  certificationCode: certificationCodeSchema,
  counts: z.record(coverageClassificationSchema, z.number().int().nonnegative()),
  totalSources: z.number().int().nonnegative(),
  totalDerived: z.number().int().nonnegative(),
})

export type CertDomain = z.infer<typeof certDomainSchema>
export type CertResourceRelevance = z.infer<typeof certResourceRelevanceSchema>
export type CurriculumEntry = z.infer<typeof curriculumEntrySchema>
export type CoverageClassification = z.infer<typeof coverageClassificationSchema>
export type CoverageManifest = z.infer<typeof coverageManifestSchema>
