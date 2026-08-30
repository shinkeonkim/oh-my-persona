import { selectCopyrightAuditNotes } from "../audit-targets"
import { auditStudyNote } from "../copyright-filter"
import { loadAllContent } from "../source-loader"
import { contentSourcePaths, PROJECT_ROOT } from "./paths"

const bundle = await loadAllContent(contentSourcePaths(PROJECT_ROOT))
const auditNotes = selectCopyrightAuditNotes(bundle.studyNotes)
const failures = auditNotes.flatMap((note) =>
  auditStudyNote(note.markdown).map((finding) => ({
    certificationCode: note.certificationCode,
    slug: note.slug,
    ...finding,
  })),
)

if (failures.length > 0) {
  console.error(`Copyright audit failed with ${failures.length} finding(s)`)
  for (const failure of failures.slice(0, 20)) {
    console.error(
      `- ${failure.certificationCode}/${failure.slug} [${failure.rule}]: ${failure.excerpt}`,
    )
  }
  process.exitCode = 1
} else {
  console.info(`Copyright audit passed for ${auditNotes.length} sanitized source study notes`)
}
