import { marked, Parser, Renderer, TextRenderer, type Tokens } from "marked"
import sanitizeHtml from "sanitize-html"

export type StudyHeadingLevel = 1 | 2 | 3 | 4

export type StudyHeading = {
  readonly id: string
  readonly label: string
  readonly level: StudyHeadingLevel
}

export type RenderedMarkdown = {
  readonly headings: readonly StudyHeading[]
  readonly html: string
}

type RenderedHeading = {
  readonly id: string
  readonly label: string
  readonly depth: number
}

function headingLabel(tokens: Tokens.Heading["tokens"]): string {
  return new Parser().parseInline(tokens, new TextRenderer()).trim()
}

function headingSlug(label: string): string {
  return (
    label
      .normalize("NFKC")
      .toLocaleLowerCase("ko")
      .replace(/[^\p{Letter}\p{Number}]+/gu, "-")
      .replace(/^-+|-+$/g, "") || "section"
  )
}

function createHeadings(tokens: readonly Tokens.Heading[]): readonly RenderedHeading[] {
  const occurrences = new Map<string, number>()
  return tokens.map((token) => {
    const label = headingLabel(token.tokens)
    const slug = headingSlug(label)
    const occurrence = (occurrences.get(slug) ?? 0) + 1
    occurrences.set(slug, occurrence)
    return {
      id: occurrence === 1 ? slug : `${slug}-${occurrence}`,
      label,
      depth: token.depth,
    }
  })
}

function isStudyHeadingLevel(depth: number): depth is StudyHeadingLevel {
  return depth >= 1 && depth <= 4
}

export function renderMarkdown(markdown: string): RenderedMarkdown {
  const tokens = marked.lexer(markdown)
  const headingTokens = tokens.filter((token): token is Tokens.Heading => token.type === "heading")
  const renderedHeadings = createHeadings(headingTokens)
  const renderer = new Renderer()
  let headingIndex = 0

  renderer.heading = ({ tokens: inlineTokens, depth }) => {
    const heading = renderedHeadings[headingIndex]
    headingIndex += 1
    const id = heading?.id ?? `section-${headingIndex}`
    return `<h${depth} id="${id}">${Parser.parseInline(inlineTokens)}</h${depth}>\n`
  }

  const rawHtml = marked.parser(tokens, { renderer })
  const html = sanitizeHtml(rawHtml, {
    allowedTags: sanitizeHtml.defaults.allowedTags.concat(["img"]),
    allowedAttributes: { ...sanitizeHtml.defaults.allowedAttributes, "*": ["id"] },
    allowedSchemes: ["http", "https", "mailto"],
  })
  const headings = renderedHeadings.flatMap(({ id, label, depth }) =>
    isStudyHeadingLevel(depth) ? [{ id, label, level: depth }] : [],
  )

  return { headings, html }
}
