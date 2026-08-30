import {
  categories,
  createDatabase,
  questions,
  sourceArtifacts as storedSourceArtifacts,
  studyNotes,
} from "@aws-study/db"
import { and, eq, notInArray, sql } from "drizzle-orm"
import type { ContentBundle } from "./types"

export async function persistContent(databaseUrl: string, bundle: ContentBundle): Promise<void> {
  const database = createDatabase(databaseUrl)

  await database.transaction(async (transaction) => {
    if (bundle.categories.length > 0) {
      await transaction
        .insert(categories)
        .values([...bundle.categories])
        .onConflictDoUpdate({
          target: [categories.certificationCode, categories.slug],
          set: {
            title: sql.raw('excluded."title"'),
            summary: sql.raw('excluded."summary"'),
            order: sql.raw('excluded."order"'),
          },
        })
    }
    if (bundle.studyNotes.length > 0) {
      await transaction
        .insert(studyNotes)
        .values([...bundle.studyNotes])
        .onConflictDoUpdate({
          target: [studyNotes.certificationCode, studyNotes.slug],
          set: {
            title: sql.raw('excluded."title"'),
            markdown: sql.raw('excluded."markdown"'),
            categorySlug: sql.raw('excluded."category_slug"'),
            access: sql.raw('excluded."access"'),
          },
        })
    }
    if (bundle.questions.length > 0) {
      await transaction
        .insert(questions)
        .values([...bundle.questions])
        .onConflictDoUpdate({
          target: questions.sourceId,
          set: {
            prompt: sql.raw('excluded."prompt"'),
            options: sql.raw('excluded."options"'),
            answers: sql.raw('excluded."answers"'),
            explanation: sql.raw('excluded."explanation"'),
            categorySlug: sql.raw('excluded."category_slug"'),
            access: sql.raw('excluded."access"'),
          },
        })
    }
    if (bundle.sourceArtifacts.length > 0) {
      await transaction
        .insert(storedSourceArtifacts)
        .values([...bundle.sourceArtifacts])
        .onConflictDoUpdate({
          target: storedSourceArtifacts.id,
          set: {
            sourceNamespace: sql.raw('excluded."source_namespace"'),
            certificationCode: sql.raw('excluded."certification_code"'),
            kind: sql.raw('excluded."kind"'),
            access: sql.raw('excluded."access"'),
            title: sql.raw('excluded."title"'),
            markdown: sql.raw('excluded."markdown"'),
            checksum: sql.raw('excluded."checksum"'),
            sourceIdentity: sql.raw('excluded."source_identity"'),
            parentId: sql.raw('excluded."parent_id"'),
            order: sql.raw('excluded."order"'),
          },
        })

      const namespaces = new Set(bundle.sourceArtifacts.map((artifact) => artifact.sourceNamespace))
      for (const namespace of namespaces) {
        const ids = bundle.sourceArtifacts
          .filter((artifact) => artifact.sourceNamespace === namespace)
          .map((artifact) => artifact.id)
        await transaction
          .delete(storedSourceArtifacts)
          .where(
            and(
              eq(storedSourceArtifacts.sourceNamespace, namespace),
              notInArray(storedSourceArtifacts.id, ids),
            ),
          )
      }
    }
  })
}
