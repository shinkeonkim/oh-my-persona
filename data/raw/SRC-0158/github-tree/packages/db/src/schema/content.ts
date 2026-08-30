import { index, integer, jsonb, pgTable, text, uniqueIndex, uuid } from "drizzle-orm/pg-core"

import { certificationCodeEnum, contentAccessEnum } from "./enums"

export type StoredQuestionOption = {
  readonly key: string
  readonly text: string
}

export const categories = pgTable(
  "categories",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    certificationCode: certificationCodeEnum("certification_code").notNull(),
    slug: text("slug").notNull(),
    order: integer("order").notNull(),
    title: text("title").notNull(),
    summary: text("summary").notNull().default(""),
  },
  (table) => [
    uniqueIndex("categories_cert_slug_uidx").on(table.certificationCode, table.slug),
    index("categories_cert_order_idx").on(table.certificationCode, table.order),
  ],
)

export const studyNotes = pgTable(
  "study_notes",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    certificationCode: certificationCodeEnum("certification_code").notNull(),
    categorySlug: text("category_slug").notNull(),
    slug: text("slug").notNull(),
    title: text("title").notNull(),
    markdown: text("markdown").notNull(),
    access: contentAccessEnum("access").notNull(),
  },
  (table) => [
    uniqueIndex("study_notes_cert_slug_uidx").on(table.certificationCode, table.slug),
    index("study_notes_category_idx").on(table.certificationCode, table.categorySlug),
  ],
)

export const questions = pgTable(
  "questions",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    sourceId: text("source_id").notNull().unique(),
    certificationCode: certificationCodeEnum("certification_code").notNull(),
    categorySlug: text("category_slug").notNull(),
    prompt: text("prompt").notNull(),
    options: jsonb("options").$type<readonly StoredQuestionOption[]>().notNull(),
    answers: jsonb("answers").$type<readonly string[]>().notNull(),
    explanation: text("explanation").notNull(),
    access: contentAccessEnum("access").notNull().default("protected"),
  },
  (table) => [index("questions_category_idx").on(table.certificationCode, table.categorySlug)],
)
