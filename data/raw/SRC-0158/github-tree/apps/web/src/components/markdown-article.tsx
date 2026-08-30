export function MarkdownArticle({ html }: { readonly html: string }) {
  return <article className="prose" dangerouslySetInnerHTML={{ __html: html }} />
}
