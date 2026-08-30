import type { Category, Question, StudyNote } from "@aws-study/shared"
import { certificationCodeSchema, contentAccessSchema } from "@aws-study/shared"
import { z } from "zod"

export const sourceArtifactKindSchema = z.enum([
  "study-note",
  "concept-note",
  "resource-section",
  "linked-pdf",
  "root-pdf",
])

export const sourceArtifactSchema = z.strictObject({
  id: z.string().min(1),
  sourceNamespace: z.string().min(1),
  certificationCode: certificationCodeSchema,
  kind: sourceArtifactKindSchema,
  access: contentAccessSchema,
  title: z.string().min(1),
  markdown: z.string().min(1).nullable(),
  checksum: z.string().regex(/^[a-f0-9]{64}$/),
  sourceIdentity: z.string().min(1),
  parentId: z.string().min(1).optional(),
  order: z.number().int().nonnegative(),
})

export type SourceArtifact = z.infer<typeof sourceArtifactSchema>

export type ContentBundle = {
  readonly categories: readonly Category[]
  readonly studyNotes: readonly StudyNote[]
  readonly questions: readonly Question[]
  readonly sourceArtifacts: readonly SourceArtifact[]
}

export type ContentSourcePaths = {
  readonly saa: string
  readonly clf: string
  readonly aif: string
}

export type CopyrightFinding = {
  readonly rule: string
  readonly excerpt: string
}
