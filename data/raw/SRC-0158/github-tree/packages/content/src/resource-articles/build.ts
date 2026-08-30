import { buildCatalogBundle } from "@aws-study/shared"

import { estimateReadingMinutes, renderResourceArticle } from "./render"
import { type ResourceArticle, resourceArticleSchema } from "./types"

export function buildResourceArticles(): readonly ResourceArticle[] {
  const bundle = buildCatalogBundle()
  const titles = new Map(bundle.resources.map((resource) => [resource.slug, resource.title]))
  return bundle.resources.map((resource) => {
    const officialUrl = `https://docs.aws.amazon.com/search/doc-search.html?searchPath=documentation&searchQuery=${encodeURIComponent(resource.title)}`
    const markdown = renderResourceArticle({
      resource,
      features: bundle.features.filter((feature) => feature.parentSlug === resource.slug),
      outgoing: bundle.edges.filter((edge) => edge.from === resource.slug),
      incoming: bundle.edges.filter((edge) => edge.to === resource.slug),
      titles,
      officialUrl,
    })
    return resourceArticleSchema.parse({
      slug: resource.slug,
      title: resource.title,
      difficulty: resource.difficulty,
      markdown,
      officialUrl,
      readingMinutes: estimateReadingMinutes(markdown),
    })
  })
}
