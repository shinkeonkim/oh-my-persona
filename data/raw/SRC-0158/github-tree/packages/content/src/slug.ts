export function stripMarkdownExtension(filename: string): string {
  return filename.replace(/\.md$/i, "")
}

export function categorySlug(directoryName: string): string {
  return directoryName.replace(/^\d{2}-/, "")
}

export function categoryOrder(directoryName: string): number {
  const prefix = directoryName.match(/^(\d{2})-/)?.[1]
  return prefix === undefined ? 0 : Number.parseInt(prefix, 10)
}

export function noteTitle(markdown: string, fallback: string): string {
  const heading = markdown.match(/^#\s+(.+)$/m)?.[1]?.trim()
  return heading ?? fallback
}
