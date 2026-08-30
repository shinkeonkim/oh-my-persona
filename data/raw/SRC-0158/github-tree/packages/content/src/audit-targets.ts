import type { StudyNote } from "@aws-study/shared"

export function selectCopyrightAuditNotes(notes: readonly StudyNote[]): readonly StudyNote[] {
  return notes.filter((note) => note.certificationCode !== "aif")
}
