import { z } from "zod"

import { contentAccessSchema } from "../certifications"
import { canonicalSlugSchema } from "./resource-root"

export const assetKindSchema = z.enum(["pdf", "markdown", "image", "video"])

export const contentAssetSchema = z.object({
  id: z.string().min(1).max(200),
  resourceSlug: canonicalSlugSchema,
  kind: assetKindSchema,
  access: contentAccessSchema,
  title: z.string().min(1).max(200),
  checksum: z.string().regex(/^sha256:[a-f0-9]{64}$/, {
    message: "Checksum must be sha256:<64 hex chars>",
  }),
  sourceIdentity: z.string().min(1).max(500),
})

export type AssetKind = z.infer<typeof assetKindSchema>
export type ContentAsset = z.infer<typeof contentAssetSchema>
