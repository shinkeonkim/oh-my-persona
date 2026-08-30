import {
  boolean,
  index,
  integer,
  jsonb,
  pgTable,
  primaryKey,
  timestamp,
  uuid,
} from "drizzle-orm/pg-core"

import { bookmarkTypeEnum, certificationCodeEnum } from "./enums"
import { users } from "./identity"

export const questionProgress = pgTable(
  "question_progress",
  {
    userId: uuid("user_id")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    questionId: uuid("question_id").notNull(),
    attempts: integer("attempts").notNull().default(0),
    correctAttempts: integer("correct_attempts").notNull().default(0),
    lastCorrect: boolean("last_correct").notNull().default(false),
    selectedAnswers: jsonb("selected_answers").$type<readonly string[]>().notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    primaryKey({ columns: [table.userId, table.questionId] }),
    index("question_progress_user_idx").on(table.userId, table.updatedAt),
  ],
)

export const bookmarks = pgTable(
  "bookmarks",
  {
    userId: uuid("user_id")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    contentType: bookmarkTypeEnum("content_type").notNull(),
    contentId: uuid("content_id").notNull(),
    certificationCode: certificationCodeEnum("certification_code").notNull(),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    primaryKey({ columns: [table.userId, table.contentType, table.contentId] }),
    index("bookmarks_user_idx").on(table.userId, table.createdAt),
  ],
)
