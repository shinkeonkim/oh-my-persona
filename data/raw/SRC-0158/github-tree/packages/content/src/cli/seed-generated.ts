import { categorySchema, questionSchema, studyNoteSchema } from "@aws-study/shared"
import { z } from "zod"

import { persistContent } from "../persist"
import { sourceArtifactSchema } from "../types"
import { PROJECT_ROOT } from "./paths"

const bundleSchema = z.object({
  categories: z.array(categorySchema),
  studyNotes: z.array(studyNoteSchema),
  questions: z.array(questionSchema),
  sourceArtifacts: z.array(sourceArtifactSchema).default([]),
})
const databaseUrl = z.url().parse(process.env["DATABASE_URL"])
const rawBundle = await Bun.file(`${PROJECT_ROOT}/packages/content/generated/content.json`).json()
const bundle = bundleSchema.parse(rawBundle)

await persistContent(databaseUrl, bundle)
console.info(
  `Seeded ${bundle.categories.length} categories, ${bundle.studyNotes.length} notes, ` +
    `${bundle.questions.length} questions and ${bundle.sourceArtifacts.length} source artifacts`,
)
