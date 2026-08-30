export * from "./catalog/index"
export {
  type CoverageResponse,
  coverageResponseSchema,
  type ResourceDetail,
  type ResourceGraphResponse,
  type ResourceListItem,
  type ResourceListResponse,
  resourceDetailSchema,
  resourceGraphResponseSchema,
  resourceListItemSchema,
  resourceListResponseSchema,
} from "./resource-api"
export {
  type AssetKind,
  assetKindSchema,
  type ContentAsset,
  contentAssetSchema,
} from "./resource-assets"
export { type ResourceBundle, resourceBundleSchema } from "./resource-bundle"
export {
  type CertDomain,
  type CertResourceRelevance,
  type CoverageClassification,
  type CoverageManifest,
  type CurriculumEntry,
  certDomainSchema,
  certResourceRelevanceSchema,
  coverageClassificationSchema,
  coverageManifestSchema,
  curriculumEntrySchema,
} from "./resource-curriculum"
export {
  type AliasTarget,
  aliasTargetSchema,
  type ChildFeature,
  childFeatureSchema,
  type EdgeType,
  edgeTypeSchema,
  type ResourceEdge,
  resourceEdgeSchema,
} from "./resource-relations"
export {
  type CanonicalResource,
  type CanonicalSlug,
  canonicalResourceSchema,
  canonicalSlugSchema,
  type Difficulty,
  difficultySchema,
} from "./resource-root"
