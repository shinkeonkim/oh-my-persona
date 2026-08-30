import {
  index,
  integer,
  pgTable,
  primaryKey,
  text,
  timestamp,
  uniqueIndex,
} from "drizzle-orm/pg-core"

import {
  assetKindEnum,
  certificationCodeEnum,
  contentAccessEnum,
  difficultyEnum,
  edgeTypeEnum,
} from "./enums"

export const resources = pgTable(
  "resources",
  {
    slug: text("slug").primaryKey(),
    title: text("title").notNull(),
    summary: text("summary").notNull(),
    difficulty: difficultyEnum("difficulty").notNull(),
    order: integer("order").notNull(),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [index("resources_difficulty_order_idx").on(table.difficulty, table.order)],
)

export const childFeatures = pgTable(
  "child_features",
  {
    slug: text("slug").primaryKey(),
    parentSlug: text("parent_slug")
      .notNull()
      .references(() => resources.slug, { onDelete: "cascade" }),
    title: text("title").notNull(),
    summary: text("summary").notNull(),
    order: integer("order").notNull(),
  },
  (table) => [index("child_features_parent_idx").on(table.parentSlug, table.order)],
)

export const resourceAliases = pgTable("resource_aliases", {
  alias: text("alias").primaryKey(),
  canonicalSlug: text("canonical_slug")
    .notNull()
    .references(() => resources.slug, { onDelete: "cascade" }),
})

export const resourceEdges = pgTable(
  "resource_edges",
  {
    fromSlug: text("from_slug")
      .notNull()
      .references(() => resources.slug, { onDelete: "cascade" }),
    toSlug: text("to_slug")
      .notNull()
      .references(() => resources.slug, { onDelete: "cascade" }),
    edgeType: edgeTypeEnum("edge_type").notNull(),
  },
  (table) => [
    primaryKey({ columns: [table.fromSlug, table.toSlug, table.edgeType] }),
    index("resource_edges_to_idx").on(table.toSlug),
    index("resource_edges_type_idx").on(table.edgeType),
  ],
)

export const certResourceRelevance = pgTable(
  "cert_resource_relevance",
  {
    resourceSlug: text("resource_slug")
      .notNull()
      .references(() => resources.slug, { onDelete: "cascade" }),
    certificationCode: certificationCodeEnum("certification_code").notNull(),
    domainCode: text("domain_code").notNull(),
  },
  (table) => [
    primaryKey({
      name: "cert_relevance_pk",
      columns: [table.resourceSlug, table.certificationCode, table.domainCode],
    }),
    index("cert_relevance_cert_idx").on(table.certificationCode),
  ],
)

export const contentAssets = pgTable(
  "content_assets",
  {
    id: text("id").primaryKey(),
    resourceSlug: text("resource_slug")
      .notNull()
      .references(() => resources.slug, { onDelete: "cascade" }),
    kind: assetKindEnum("kind").notNull(),
    access: contentAccessEnum("access").notNull(),
    title: text("title").notNull(),
    checksum: text("checksum").notNull(),
    sourceIdentity: text("source_identity").notNull(),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    index("content_assets_resource_idx").on(table.resourceSlug),
    uniqueIndex("content_assets_checksum_uidx").on(table.checksum),
  ],
)

export type ResourceRecord = typeof resources.$inferSelect
export type NewResourceRecord = typeof resources.$inferInsert
export type ChildFeatureRecord = typeof childFeatures.$inferSelect
export type ContentAssetRecord = typeof contentAssets.$inferSelect
