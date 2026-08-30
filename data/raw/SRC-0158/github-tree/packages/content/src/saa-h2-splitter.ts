/**
 * H2-level section splitter for the SAA resource completeness note.
 * Mirrors the split_by_h2() logic in the original build_notes.py.
 */

const H2_RE = /^##\s+(.+)$/gm

export type H2Section = {
  readonly slug: string
  readonly title: string
  readonly order: number
  readonly markdown: string
}

function slugifyH2(title: string, ordinal: number): string {
  const numbered = title.match(/^(\d+)[.)]\s+/)
  if (numbered?.[1]) {
    return `section-${String(Number.parseInt(numbered[1], 10)).padStart(2, "0")}`
  }
  return `section-${String(ordinal).padStart(2, "0")}`
}

export function splitByH2(markdown: string): readonly H2Section[] {
  const matches = [...markdown.matchAll(H2_RE)]
  if (matches.length === 0) return []

  const sections: H2Section[] = []
  for (let i = 0; i < matches.length; i++) {
    const match = matches[i]
    if (!match) continue
    const title = match[1]?.trim() ?? ""
    const start = match.index
    const end = i + 1 < matches.length ? matches[i + 1]?.index : markdown.length
    if (start === undefined || end === undefined) continue
    const sectionMd = `${markdown.slice(start, end).trimEnd()}\n`
    const ordinal = i + 1
    sections.push({
      slug: slugifyH2(title, ordinal),
      title,
      order: ordinal,
      markdown: sectionMd,
    })
  }
  return sections
}
