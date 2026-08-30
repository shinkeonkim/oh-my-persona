import { sql } from "drizzle-orm"
import {
  boolean,
  check,
  foreignKey,
  index,
  integer,
  jsonb,
  pgTable,
  primaryKey,
  timestamp,
  unique,
  uuid,
} from "drizzle-orm/pg-core"

import { questions } from "./content"
import { certificationCodeEnum, quizModeEnum, quizOrderEnum, quizSessionStatusEnum } from "./enums"
import { users } from "./identity"

export const quizSessions = pgTable(
  "quiz_sessions",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    userId: uuid("user_id")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    parentSessionId: uuid("parent_session_id"),
    certificationCode: certificationCodeEnum("certification_code").notNull(),
    mode: quizModeEnum("mode").notNull(),
    order: quizOrderEnum("order").notNull(),
    questionLimit: integer("question_limit"),
    categorySlugs: jsonb("category_slugs").$type<readonly string[]>().notNull(),
    status: quizSessionStatusEnum("status").notNull().default("active"),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
    completedAt: timestamp("completed_at", { withTimezone: true }),
  },
  (table) => [
    unique("quiz_sessions_id_user_unique").on(table.id, table.userId),
    foreignKey({
      columns: [table.parentSessionId, table.userId],
      foreignColumns: [table.id, table.userId],
      name: "quiz_sessions_parent_user_fk",
    }),
    check(
      "quiz_sessions_limit_check",
      sql`${table.questionLimit} IS NULL OR ${table.questionLimit} > 0`,
    ),
    check(
      "quiz_sessions_categories_check",
      sql`jsonb_typeof(${table.categorySlugs}) = 'array' AND jsonb_array_length(${table.categorySlugs}) > 0`,
    ),
    index("quiz_sessions_user_cert_created_idx").on(
      table.userId,
      table.certificationCode,
      table.createdAt,
    ),
  ],
)

export const quizQueue = pgTable(
  "quiz_queue",
  {
    sessionId: uuid("session_id")
      .notNull()
      .references(() => quizSessions.id, { onDelete: "cascade" }),
    position: integer("position").notNull(),
    questionId: uuid("question_id")
      .notNull()
      .references(() => questions.id, { onDelete: "restrict" }),
  },
  (table) => [
    primaryKey({ name: "quiz_queue_pk", columns: [table.sessionId, table.position] }),
    unique("quiz_queue_session_question_unique").on(table.sessionId, table.questionId),
    check("quiz_queue_position_check", sql`${table.position} >= 0`),
  ],
)

export const quizAttempts = pgTable(
  "quiz_attempts",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    sessionId: uuid("session_id").notNull(),
    userId: uuid("user_id").notNull(),
    questionId: uuid("question_id").notNull(),
    selectedAnswers: jsonb("selected_answers").$type<readonly string[]>().notNull(),
    correct: boolean("correct").notNull(),
    attemptedAt: timestamp("attempted_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    foreignKey({
      columns: [table.sessionId, table.userId],
      foreignColumns: [quizSessions.id, quizSessions.userId],
      name: "quiz_attempts_session_user_fk",
    }).onDelete("cascade"),
    foreignKey({
      columns: [table.sessionId, table.questionId],
      foreignColumns: [quizQueue.sessionId, quizQueue.questionId],
      name: "quiz_attempts_queued_question_fk",
    }).onDelete("restrict"),
    unique("quiz_attempts_session_question_unique").on(table.sessionId, table.questionId),
    check(
      "quiz_attempts_answers_check",
      sql`jsonb_typeof(${table.selectedAnswers}) = 'array' AND jsonb_array_length(${table.selectedAnswers}) > 0`,
    ),
    index("quiz_attempts_user_attempted_idx").on(table.userId, table.attemptedAt),
    index("quiz_attempts_session_idx").on(table.sessionId, table.attemptedAt),
  ],
)

export const quizPreferences = pgTable(
  "quiz_preferences",
  {
    userId: uuid("user_id")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    certificationCode: certificationCodeEnum("certification_code").notNull(),
    mode: quizModeEnum("mode").notNull(),
    order: quizOrderEnum("order").notNull(),
    questionLimit: integer("question_limit"),
    categorySlugs: jsonb("category_slugs").$type<readonly string[]>().notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    primaryKey({ name: "quiz_preferences_pk", columns: [table.userId, table.certificationCode] }),
    check(
      "quiz_preferences_limit_check",
      sql`${table.questionLimit} IS NULL OR ${table.questionLimit} > 0`,
    ),
    check(
      "quiz_preferences_categories_check",
      sql`jsonb_typeof(${table.categorySlugs}) = 'array' AND jsonb_array_length(${table.categorySlugs}) > 0`,
    ),
  ],
)

export type QuizSessionRecord = typeof quizSessions.$inferSelect
export type QuizQueueRecord = typeof quizQueue.$inferSelect
export type QuizAttemptRecord = typeof quizAttempts.$inferSelect
export type QuizPreferenceRecord = typeof quizPreferences.$inferSelect
