import { copyFileSync, mkdirSync, readFileSync, writeFileSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import postgres from "postgres"
import { z } from "zod"

const DRIZZLE_DIR = new URL("../drizzle", import.meta.url).pathname
const migrationJournalSchema = z.object({
  version: z.string(),
  dialect: z.literal("postgresql"),
  entries: z.array(
    z.object({
      idx: z.number().int().nonnegative(),
      version: z.string(),
      when: z.number().int().nonnegative(),
      tag: z.string().min(1),
      breakpoints: z.boolean(),
    }),
  ),
})

export class DockerError extends Error {
  constructor(
    readonly exitCode: number,
    message: string,
  ) {
    super(message)
    this.name = "DockerError"
  }
}

export class ConstraintExpectationError extends Error {
  constructor() {
    super("Expected constraint violation but query succeeded")
    this.name = "ConstraintExpectationError"
  }
}

export class MigrationFixtureError extends Error {
  constructor() {
    super("Requested migration tag is absent from the Drizzle journal")
    this.name = "MigrationFixtureError"
  }
}

export function connectionUrl(port: number, password: string, db: string): string {
  return `postgresql://postgres:${password}@localhost:${port}/${db}`
}

export async function execSql(url: string, sql: string): Promise<void> {
  const client = postgres(url, { max: 1 })
  try {
    await client.unsafe(sql)
  } finally {
    await client.end()
  }
}

export async function expectConstraintViolation(url: string, sql: string): Promise<string> {
  const client = postgres(url, { max: 1 })
  try {
    await client.unsafe(sql)
    throw new ConstraintExpectationError()
  } catch (error: unknown) {
    if (error instanceof postgres.PostgresError) {
      return error.code
    }
    throw error
  } finally {
    await client.end()
  }
}

export async function runDocker(args: readonly string[]): Promise<void> {
  const proc = Bun.spawn(["docker", ...args], { stderr: "pipe" })
  const exitCode = await proc.exited
  if (exitCode !== 0) {
    const stderr = await new Response(proc.stderr).text()
    throw new DockerError(exitCode, `docker ${args[0]} failed (exit ${exitCode}): ${stderr.trim()}`)
  }
}

export async function removeContainerIfExists(name: string): Promise<void> {
  const proc = Bun.spawn(["docker", "rm", "-f", name], { stderr: "pipe" })
  const exitCode = await proc.exited
  if (exitCode !== 0) {
    const stderr = await new Response(proc.stderr).text()
    if (!stderr.includes("No such container")) {
      throw new DockerError(exitCode, `docker rm -f failed (exit ${exitCode}): ${stderr.trim()}`)
    }
  }
}

export async function startContainer(name: string, port: number, password: string): Promise<void> {
  await runDocker([
    "run",
    "-d",
    "--name",
    name,
    "-e",
    `POSTGRES_PASSWORD=${password}`,
    "-p",
    `${port}:5432`,
    "--health-cmd",
    "pg_isready -U postgres",
    "--health-interval=2s",
    "--health-timeout=2s",
    "--health-retries=15",
    "postgres:16.8-alpine",
  ])

  for (let i = 0; i < 30; i++) {
    const check = Bun.spawn(["docker", "inspect", "--format", "{{.State.Health.Status}}", name])
    const output = await new Response(check.stdout).text()
    if (output.trim() === "healthy") return
    await Bun.sleep(1000)
  }
  throw new DockerError(1, "Container failed to become healthy within 30s")
}

export async function createDb(adminUrl: string, name: string): Promise<void> {
  const client = postgres(adminUrl, { max: 1 })
  try {
    await client.unsafe(`DROP DATABASE IF EXISTS ${name}`)
    await client.unsafe(`CREATE DATABASE ${name}`)
  } finally {
    await client.end()
  }
}

export function makeMigrationDir(tags: readonly string[]): string {
  const dir = join(
    tmpdir(),
    `task3-drizzle-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
  )
  mkdirSync(join(dir, "meta"), { recursive: true })

  const rawJournal: unknown = JSON.parse(
    readFileSync(join(DRIZZLE_DIR, "meta", "_journal.json"), "utf8"),
  )
  const journal = migrationJournalSchema.parse(rawJournal)
  const entries = journal.entries.filter((entry) => tags.includes(entry.tag))
  if (entries.length !== tags.length) {
    throw new MigrationFixtureError()
  }
  writeFileSync(
    join(dir, "meta", "_journal.json"),
    `${JSON.stringify({ version: journal.version, dialect: journal.dialect, entries })}\n`,
  )

  for (const tag of tags) {
    copyFileSync(join(DRIZZLE_DIR, `${tag}.sql`), join(dir, `${tag}.sql`))
  }
  return dir
}

export async function queryTableNames(url: string): Promise<readonly string[]> {
  const client = postgres(url, { max: 1 })
  try {
    const rows = await client`
      SELECT table_name FROM information_schema.tables
      WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
      ORDER BY table_name
    `
    return rows.map((r) => String(r["table_name"]))
  } finally {
    await client.end()
  }
}
