export type SizeViolation = {
  readonly path: string
  readonly pureLines: number
  readonly limit: number
}

const DEFAULT_LIMIT = 250
const SOURCE_PATTERN = "**/*.{ts,tsx,mts,cts,js,jsx,mjs,cjs,css,md,yml,yaml}"
const IGNORED_SEGMENTS = [
  "/content-sources/",
  "/node_modules/",
  "/.next/",
  "/dist/",
  "/coverage/",
  "/drizzle/",
] as const

function isCommentOnly(line: string): boolean {
  const trimmed = line.trim()
  return (
    trimmed.startsWith("//") ||
    trimmed.startsWith("#") ||
    trimmed.startsWith("/*") ||
    trimmed.startsWith("*") ||
    trimmed.startsWith("<!--") ||
    trimmed.startsWith("-->")
  )
}

export function countPureLines(source: string): number {
  return source.split("\n").filter((line) => line.trim() !== "" && !isCommentOnly(line)).length
}

export function auditSource(path: string, source: string, limit: number): SizeViolation | null {
  const pureLines = countPureLines(source)
  return pureLines > limit ? { path, pureLines, limit } : null
}

function isIgnored(path: string): boolean {
  const normalized = `/${path.replaceAll("\\", "/")}`
  return IGNORED_SEGMENTS.some((segment) => normalized.includes(segment))
}

async function collectViolations(root: string): Promise<readonly SizeViolation[]> {
  const violations: SizeViolation[] = []
  const glob = new Bun.Glob(SOURCE_PATTERN)

  for await (const path of glob.scan({ cwd: root, onlyFiles: true })) {
    if (isIgnored(path)) continue

    const source = await Bun.file(`${root}/${path}`).text()
    const violation = auditSource(path, source, DEFAULT_LIMIT)
    if (violation !== null) violations.push(violation)
  }

  return violations.sort((left, right) => right.pureLines - left.pureLines)
}

async function main(): Promise<void> {
  const violations = await collectViolations(process.cwd())
  if (violations.length === 0) {
    console.info(`File size check passed: all source files are <= ${DEFAULT_LIMIT} pure LOC`)
    return
  }

  console.error(
    `File size check failed: ${violations.length} file(s) exceed ${DEFAULT_LIMIT} pure LOC`,
  )
  for (const violation of violations) {
    console.error(`- ${violation.path}: ${violation.pureLines} pure LOC`)
  }
  process.exitCode = 1
}

if (import.meta.main) {
  await main()
}
