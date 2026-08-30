import { mkdir } from "node:fs/promises"

import { z } from "zod"

import { persistContent } from "../persist"
import { loadAllContent } from "../source-loader"
import { contentSourcePaths, PROJECT_ROOT } from "./paths"

const root = PROJECT_ROOT
const bundle = await loadAllContent(contentSourcePaths(root))
const outputDirectory = `${root}/packages/content/generated`

await mkdir(outputDirectory, { recursive: true })
await Bun.write(`${outputDirectory}/content.json`, JSON.stringify(bundle))

const optionalDatabaseUrl = z.string().url().optional().parse(process.env["DATABASE_URL"])
if (optionalDatabaseUrl !== undefined) await persistContent(optionalDatabaseUrl, bundle)

console.info(
  `Built ${bundle.categories.length} categories, ${bundle.studyNotes.length} notes, ` +
    `${bundle.questions.length} questions, ${bundle.sourceArtifacts.length} source artifacts` +
    `${optionalDatabaseUrl === undefined ? "" : " and persisted them"}`,
)
