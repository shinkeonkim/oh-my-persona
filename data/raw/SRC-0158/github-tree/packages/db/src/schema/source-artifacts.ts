import { index, integer, pgTable, text } from "drizzle-orm/pg-core"

import { certificationCodeEnum, contentAccessEnum, sourceArtifactKindEnum } from "./enums"

export const sourceArtifacts = pgTable(
  "source_artifacts",
  {
    id: text("id").primaryKey(),
    sourceNamespace: text("source_namespace").notNull(),
    certificationCode: certificationCodeEnum("certification_code").notNull(),
    kind: sourceArtifactKindEnum("kind").notNull(),
    access: contentAccessEnum("access").notNull(),
    title: text("title").notNull(),
    markdown: text("markdown"),
    checksum: text("checksum").notNull(),
    sourceIdentity: text("source_identity").notNull(),
    parentId: text("parent_id"),
    order: integer("order").notNull(),
  },
  (table) => [
    index("source_artifacts_namespace_kind_idx").on(table.sourceNamespace, table.kind),
    index("source_artifacts_cert_order_idx").on(table.certificationCode, table.kind, table.order),
    index("source_artifacts_identity_idx").on(table.sourceNamespace, table.sourceIdentity),
  ],
)

export type SourceArtifactRecord = typeof sourceArtifacts.$inferSelect
export type NewSourceArtifactRecord = typeof sourceArtifacts.$inferInsert
