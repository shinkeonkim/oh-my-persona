import { pgEnum } from "drizzle-orm/pg-core"

export const certificationCodeEnum = pgEnum("certification_code", ["aif", "clf", "saa"])
export const contentAccessEnum = pgEnum("content_access", ["public", "protected"])
export const userRoleEnum = pgEnum("user_role", ["pending", "reader", "admin"])
export const bookmarkTypeEnum = pgEnum("bookmark_type", ["question", "study-note"])
export const difficultyEnum = pgEnum("difficulty", ["foundation", "advanced", "applied"])
export const edgeTypeEnum = pgEnum("edge_type", [
  "uses",
  "integrates-with",
  "secures",
  "observes",
  "stores",
  "computes",
  "delivers",
  "orchestrates",
])
export const assetKindEnum = pgEnum("asset_kind", ["pdf", "markdown", "image", "video"])
export const quizModeEnum = pgEnum("quiz_mode", ["all", "unseen", "wrong"])
export const quizOrderEnum = pgEnum("quiz_order", ["random", "sequential"])
export const quizSessionStatusEnum = pgEnum("quiz_session_status", [
  "active",
  "completed",
  "abandoned",
])
export const sourceArtifactKindEnum = pgEnum("source_artifact_kind", [
  "study-note",
  "concept-note",
  "resource-section",
  "linked-pdf",
  "root-pdf",
])
