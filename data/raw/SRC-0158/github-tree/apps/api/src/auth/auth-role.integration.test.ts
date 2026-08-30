import { afterAll, beforeAll, describe, expect, it } from "bun:test"
import { createDatabase, users } from "@aws-study/db"
import { authSessionSchema, authUserSchema } from "@aws-study/shared"
import { eq } from "drizzle-orm"
import { migrate } from "drizzle-orm/postgres-js/migrator"

import {
  connectionUrl,
  createDb,
  removeContainerIfExists,
  startContainer,
} from "../../../../packages/db/src/test-helpers"

const CONTAINER = "task12-test-postgres"
const DB_PORT = 5436
const API_PORT = 3012
const PASSWORD = "task12test"
const DATABASE = "task12"
const JWT_SECRET = "task12-secret-that-is-at-least-32-characters-long"
const LOGIN_PASSWORD = "a-secure-password"
const MIGRATIONS = new URL("../../../../packages/db/drizzle", import.meta.url).pathname
const BASE_URL = `http://127.0.0.1:${API_PORT}`
const strictAuthUserSchema = authUserSchema.strict()

function databaseUrl(database: string): string {
  return connectionUrl(DB_PORT, PASSWORD, database)
}

const database = createDatabase(databaseUrl(DATABASE))
let server: ReturnType<typeof Bun.spawn> | undefined

export class ApiTestServerError extends Error {
  constructor(message: string) {
    super(message)
    this.name = "ApiTestServerError"
  }
}

async function waitForApi(): Promise<void> {
  for (let attempt = 0; attempt < 100; attempt++) {
    try {
      const response = await fetch(`${BASE_URL}/healthz`)
      if (response.ok) return
    } catch (error: unknown) {
      if (!(error instanceof Error)) throw error
      if (!/Unable to connect|ConnectionRefused|ECONNREFUSED/.test(error.message)) throw error
    }
    await Bun.sleep(50)
  }
  throw new ApiTestServerError("API did not become ready")
}

async function postJson(path: string, payload: object, token?: string): Promise<Response> {
  return fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      ...(token === undefined ? {} : { cookie: `aws_study_session=${token}` }),
    },
    body: JSON.stringify(payload),
  })
}

async function register(email: string, displayName: string): Promise<string> {
  const response = await postJson("/api/auth/register", {
    email,
    displayName,
    password: LOGIN_PASSWORD,
  })
  expect(response.status).toBe(201)
  return authUserSchema.parse(await response.json()).id
}

async function login(email: string): Promise<string> {
  const response = await postJson("/api/auth/login", { email, password: LOGIN_PASSWORD })
  expect(response.status).toBe(200)
  return authSessionSchema.parse(await response.json()).accessToken
}

async function get(path: string, token?: string): Promise<Response> {
  return fetch(`${BASE_URL}${path}`, {
    headers: token === undefined ? {} : { cookie: `aws_study_session=${token}` },
  })
}

async function approve(id: string, token: string): Promise<Response> {
  return fetch(`${BASE_URL}/api/admin/users/${id}/approve`, {
    method: "PATCH",
    headers: { cookie: `aws_study_session=${token}` },
  })
}

async function reject(id: string, token: string): Promise<Response> {
  return fetch(`${BASE_URL}/api/admin/users/${id}/reject`, {
    method: "PATCH",
    headers: { cookie: `aws_study_session=${token}` },
  })
}

describe("authentication role matrix", () => {
  beforeAll(async () => {
    await removeContainerIfExists(CONTAINER)
    await startContainer(CONTAINER, DB_PORT, PASSWORD)
    await createDb(databaseUrl("postgres"), DATABASE)
    await migrate(database, { migrationsFolder: MIGRATIONS })
    const build = Bun.spawn(["bun", "run", "--filter", "@aws-study/api", "build"], {
      stdout: "pipe",
      stderr: "pipe",
    })
    if ((await build.exited) !== 0) {
      throw new ApiTestServerError(await new Response(build.stderr).text())
    }
    server = Bun.spawn(["bun", "run", "apps/api/dist/main.js"], {
      env: {
        ...process.env,
        NODE_ENV: "test",
        PORT: String(API_PORT),
        DATABASE_URL: databaseUrl(DATABASE),
        JWT_SECRET,
        JWT_TTL_SECONDS: "3600",
        WEB_ORIGIN: "http://localhost:3000",
      },
      stdout: "pipe",
      stderr: "pipe",
    })
    await waitForApi()
  }, 60_000)

  afterAll(async () => {
    server?.kill()
    if (server !== undefined) await server.exited
    await removeContainerIfExists(CONTAINER)
  })

  it("enforces anonymous, pending, reader, admin, and fresh-login transitions", async () => {
    const pendingId = await register("pending@example.com", "Pending")
    const rejectedId = await register("rejected@example.com", "Rejected")
    const readerId = await register("reader@example.com", "Reader")
    const adminId = await register("admin@example.com", "Admin")
    await database.update(users).set({ role: "reader" }).where(eq(users.id, readerId))
    await database.update(users).set({ role: "admin" }).where(eq(users.id, adminId))

    const pendingToken = await login("pending@example.com")
    const rejectedToken = await login("rejected@example.com")
    const readerToken = await login("reader@example.com")
    const adminToken = await login("admin@example.com")

    expect((await get("/api/content/quiz/saa")).status).toBe(401)
    expect((await get("/api/auth/me")).status).toBe(401)
    expect((await get("/api/auth/me", "malformed-token")).status).toBe(401)
    expect((await get("/api/content/quiz/saa", pendingToken)).status).toBe(403)
    expect((await get("/api/content/quiz/saa", readerToken)).status).toBe(200)
    expect((await get("/api/content/quiz/saa", adminToken)).status).toBe(200)
    expect((await get("/api/admin/users/pending", readerToken)).status).toBe(403)
    expect((await approve(pendingId, readerToken)).status).toBe(403)
    expect((await reject(rejectedId, readerToken)).status).toBe(403)
    const pendingList = await get("/api/admin/users/pending", adminToken)
    expect(pendingList.status).toBe(200)
    expect(
      strictAuthUserSchema
        .array()
        .parse(await pendingList.json())
        .map((user) => user.id),
    ).toEqual([pendingId, rejectedId])

    const pendingMe = await get("/api/auth/me", pendingToken)
    expect(pendingMe.status).toBe(200)
    expect(authUserSchema.parse(await pendingMe.json()).role).toBe("pending")
    expect((await postJson("/api/auth/logout", {}, pendingToken)).status).toBe(204)

    const approval = await approve(pendingId, adminToken)
    expect(approval.status).toBe(200)
    expect(authUserSchema.parse(await approval.json()).role).toBe("reader")
    expect((await approve(pendingId, adminToken)).status).toBe(404)
    expect((await get("/api/content/quiz/saa", pendingToken)).status).toBe(401)
    const approvedToken = await login("pending@example.com")
    expect((await get("/api/content/quiz/saa", approvedToken)).status).toBe(200)

    expect((await reject(rejectedId, adminToken)).status).toBe(204)
    expect((await reject(rejectedId, adminToken)).status).toBe(404)
    expect((await reject("not-a-uuid", adminToken)).status).toBe(400)
    expect((await get("/api/auth/me", rejectedToken)).status).toBe(401)
    const remaining = await get("/api/admin/users/pending", adminToken)
    expect(remaining.status).toBe(200)
    expect(strictAuthUserSchema.array().parse(await remaining.json())).toEqual([])

    const concurrentId = await register("concurrent@example.com", "Concurrent")
    const concurrentStatuses = await Promise.all([
      approve(concurrentId, adminToken).then((response) => response.status),
      reject(concurrentId, adminToken).then((response) => response.status),
    ])
    expect(concurrentStatuses.filter((status) => status === 404)).toHaveLength(1)
    expect(concurrentStatuses.some((status) => status === 200 || status === 204)).toBe(true)

    await database.update(users).set({ enabled: false }).where(eq(users.id, readerId))
    expect((await get("/api/progress/summary", readerToken)).status).toBe(401)
  }, 60_000)
})
