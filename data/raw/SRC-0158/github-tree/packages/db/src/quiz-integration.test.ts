import { afterAll, beforeAll, describe, expect, it } from "bun:test"
import { rmSync } from "node:fs"
import { migrate } from "drizzle-orm/postgres-js/migrator"
import postgres from "postgres"

import { createDatabase } from "./client"
import {
  connectionUrl,
  createDb,
  execSql,
  expectConstraintViolation,
  makeMigrationDir,
  queryTableNames,
  removeContainerIfExists,
  startContainer,
} from "./test-helpers"

const CONTAINER = "task6-test-postgres"
const PORT = 5434
const PASSWORD = "task6test"
const DATABASE = "task6"
const INCREMENTAL_DATABASE = "task6_incremental"
const MIGRATIONS = new URL("../drizzle", import.meta.url).pathname
const PRE_QUIZ_MIGRATIONS = ["0000_nifty_infant_terrible", "0001_plain_stardust"] as const
const USER_1 = "10000000-0000-4000-8000-000000000001"
const USER_2 = "10000000-0000-4000-8000-000000000002"
const QUESTION_1 = "20000000-0000-4000-8000-000000000001"
const QUESTION_2 = "20000000-0000-4000-8000-000000000002"
const SESSION_1 = "30000000-0000-4000-8000-000000000001"
const tempDirectories: string[] = []

function url(database: string): string {
  return connectionUrl(PORT, PASSWORD, database)
}

async function seedIdentityAndQuestions(): Promise<void> {
  await execSql(
    url(DATABASE),
    `INSERT INTO users (id, email, display_name, password_hash, role)
     VALUES ('${USER_1}', 'reader1@example.com', 'Reader 1', 'hash', 'reader'),
            ('${USER_2}', 'reader2@example.com', 'Reader 2', 'hash', 'reader');
     INSERT INTO questions
       (id, source_id, certification_code, category_slug, prompt, options, answers, explanation)
     VALUES
       ('${QUESTION_1}', 'task6-q1', 'saa', 'storage', 'Q1', '[{"key":"A","text":"S3"},{"key":"B","text":"EC2"}]', '["A"]', 'E1'),
       ('${QUESTION_2}', 'task6-q2', 'saa', 'compute', 'Q2', '[{"key":"A","text":"S3"},{"key":"B","text":"EC2"}]', '["B"]', 'E2');
     INSERT INTO quiz_sessions
       (id, user_id, certification_code, mode, "order", category_slugs)
     VALUES ('${SESSION_1}', '${USER_1}', 'saa', 'all', 'sequential', '["storage"]');
     INSERT INTO quiz_queue (session_id, position, question_id)
     VALUES ('${SESSION_1}', 0, '${QUESTION_1}');`,
  )
}

describe("quiz persistence integration", () => {
  beforeAll(async () => {
    await removeContainerIfExists(CONTAINER)
    await startContainer(CONTAINER, PORT, PASSWORD)
    await createDb(url("postgres"), DATABASE)
    await createDb(url("postgres"), INCREMENTAL_DATABASE)
    await migrate(createDatabase(url(DATABASE)), { migrationsFolder: MIGRATIONS })
    await seedIdentityAndQuestions()
  }, 60_000)

  afterAll(async () => {
    for (const directory of tempDirectories) {
      rmSync(directory, { recursive: true, force: true })
    }
    await removeContainerIfExists(CONTAINER)
  })

  it("migrates all quiz persistence tables", async () => {
    const names = await queryTableNames(url(DATABASE))
    for (const table of ["quiz_sessions", "quiz_queue", "quiz_attempts", "quiz_preferences"]) {
      expect(names).toContain(table)
    }
  })

  it("applies post-0001 migrations without harming resource rows", async () => {
    const preQuizDirectory = makeMigrationDir(PRE_QUIZ_MIGRATIONS)
    tempDirectories.push(preQuizDirectory)
    await migrate(createDatabase(url(INCREMENTAL_DATABASE)), {
      migrationsFolder: preQuizDirectory,
    })
    await execSql(
      url(INCREMENTAL_DATABASE),
      `INSERT INTO resources (slug, title, summary, difficulty, "order")
       VALUES ('amazon-s3', 'Amazon S3', 'Object storage', 'foundation', 1)`,
    )
    await migrate(createDatabase(url(INCREMENTAL_DATABASE)), { migrationsFolder: MIGRATIONS })
    const client = postgres(url(INCREMENTAL_DATABASE), { max: 1 })
    try {
      const resources = await client`SELECT slug FROM resources WHERE slug = 'amazon-s3'`
      expect(resources).toHaveLength(1)
      expect(await queryTableNames(url(INCREMENTAL_DATABASE))).toContain("quiz_sessions")
    } finally {
      await client.end()
    }
  })

  it("rejects duplicate queue positions and repeated session questions", async () => {
    expect(
      await expectConstraintViolation(
        url(DATABASE),
        `INSERT INTO quiz_queue (session_id, position, question_id)
         VALUES ('${SESSION_1}', 0, '${QUESTION_2}')`,
      ),
    ).toBe("23505")
    expect(
      await expectConstraintViolation(
        url(DATABASE),
        `INSERT INTO quiz_queue (session_id, position, question_id)
         VALUES ('${SESSION_1}', 1, '${QUESTION_1}')`,
      ),
    ).toBe("23505")
  })

  it("rejects wrong-user and unqueued-question attempts", async () => {
    expect(
      await expectConstraintViolation(
        url(DATABASE),
        `INSERT INTO quiz_attempts (session_id, user_id, question_id, selected_answers, correct)
         VALUES ('${SESSION_1}', '${USER_2}', '${QUESTION_1}', '["A"]', true)`,
      ),
    ).toBe("23503")
    expect(
      await expectConstraintViolation(
        url(DATABASE),
        `INSERT INTO quiz_attempts (session_id, user_id, question_id, selected_answers, correct)
         VALUES ('${SESSION_1}', '${USER_1}', '${QUESTION_2}', '["B"]', true)`,
      ),
    ).toBe("23503")
  })

  it("keeps attempts append-only", async () => {
    const attemptId = "40000000-0000-4000-8000-000000000001"
    await execSql(
      url(DATABASE),
      `INSERT INTO quiz_attempts (id, session_id, user_id, question_id, selected_answers, correct)
       VALUES ('${attemptId}', '${SESSION_1}', '${USER_1}', '${QUESTION_1}', '["A"]', true)`,
    )
    expect(
      await expectConstraintViolation(
        url(DATABASE),
        `INSERT INTO quiz_attempts (session_id, user_id, question_id, selected_answers, correct)
         VALUES ('${SESSION_1}', '${USER_1}', '${QUESTION_1}', '["A"]', true)`,
      ),
    ).toBe("23505")
    expect(
      await expectConstraintViolation(
        url(DATABASE),
        `UPDATE quiz_attempts SET correct = false WHERE id = '${attemptId}'`,
      ),
    ).toBe("55000")
    expect(
      await expectConstraintViolation(
        url(DATABASE),
        `DELETE FROM quiz_attempts WHERE id = '${attemptId}'`,
      ),
    ).toBe("55000")
  })

  it("allows same-user restart and rejects cross-user parent links", async () => {
    await execSql(
      url(DATABASE),
      `INSERT INTO quiz_sessions
       (id, user_id, parent_session_id, certification_code, mode, "order", category_slugs)
       VALUES ('30000000-0000-4000-8000-000000000002', '${USER_1}', '${SESSION_1}', 'saa', 'all', 'sequential', '["storage"]')`,
    )
    expect(
      await expectConstraintViolation(
        url(DATABASE),
        `INSERT INTO quiz_sessions
         (id, user_id, parent_session_id, certification_code, mode, "order", category_slugs)
         VALUES ('30000000-0000-4000-8000-000000000003', '${USER_2}', '${SESSION_1}', 'saa', 'all', 'sequential', '["storage"]')`,
      ),
    ).toBe("23503")
  })

  it("isolates preferences by user and certification", async () => {
    await execSql(
      url(DATABASE),
      `INSERT INTO quiz_preferences
       (user_id, certification_code, mode, "order", question_limit, category_slugs)
       VALUES ('${USER_1}', 'saa', 'wrong', 'sequential', 25, '["storage"]'),
              ('${USER_2}', 'saa', 'all', 'random', NULL, '["compute"]'),
              ('${USER_1}', 'clf', 'unseen', 'random', 10, '["security"]')`,
    )
    expect(
      await expectConstraintViolation(
        url(DATABASE),
        `INSERT INTO quiz_preferences
         (user_id, certification_code, mode, "order", category_slugs)
         VALUES ('${USER_1}', 'saa', 'all', 'random', '["compute"]')`,
      ),
    ).toBe("23505")
    const client = postgres(url(DATABASE), { max: 1 })
    try {
      const rows = await client`SELECT user_id, certification_code FROM quiz_preferences`
      expect(rows).toHaveLength(3)
    } finally {
      await client.end()
    }
  })

  it("rejects non-positive limits and queue positions", async () => {
    expect(
      await expectConstraintViolation(
        url(DATABASE),
        `INSERT INTO quiz_preferences
         (user_id, certification_code, mode, "order", question_limit, category_slugs)
         VALUES ('${USER_2}', 'clf', 'all', 'random', 0, '["compute"]')`,
      ),
    ).toBe("23514")
    expect(
      await expectConstraintViolation(
        url(DATABASE),
        `INSERT INTO quiz_queue (session_id, position, question_id)
         VALUES ('${SESSION_1}', -1, '${QUESTION_2}')`,
      ),
    ).toBe("23514")
  })
})
