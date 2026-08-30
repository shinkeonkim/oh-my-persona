import { certificationCodeSchema, findCertification } from "@aws-study/shared"
import Link from "next/link"
import { notFound } from "next/navigation"

import { MarkdownArticle } from "@/components/markdown-article"
import { renderMarkdown } from "@/lib/render-markdown"
import { getCategories, getStudyNote } from "@/lib/server-api"

export const dynamic = "force-dynamic"
type PageProps = { readonly params: Promise<{ readonly cert: string; readonly slug: string }> }

export default async function StudyPage({ params }: PageProps) {
  const route = await params
  const parsed = certificationCodeSchema.safeParse(route.cert)
  if (!parsed.success) notFound()
  const certification = findCertification(parsed.data)
  const [note, categories] = await Promise.all([
    getStudyNote(parsed.data, route.slug),
    getCategories(parsed.data),
  ])
  const article = renderMarkdown(note.markdown)
  return (
    <div className="shell study-layout">
      <nav className="study-sidebar" aria-label={`${certification.shortTitle} 학습 노트`}>
        <span className="eyebrow">{certification.examCode}</span>
        <Link className="study-nav-link" href={`/${certification.code}`}>
          카테고리 홈
        </Link>
        {categories.map((category) => (
          <Link
            className="study-nav-link"
            aria-current={category.slug === route.slug ? "page" : undefined}
            href={`/${certification.code}/study/${category.slug}`}
            key={category.slug}
          >
            {category.title}
          </Link>
        ))}
      </nav>
      <MarkdownArticle html={article.html} />
      <aside className="study-toc" aria-label="페이지 목차">
        <strong className="block text-[var(--text)]">목차</strong>
        <nav className="study-toc-nav" aria-label={`${note.title} 목차`}>
          {article.headings.map((heading) => (
            <a
              className="study-toc-link"
              data-level={heading.level}
              href={`#${heading.id}`}
              key={heading.id}
            >
              {heading.label}
            </a>
          ))}
        </nav>
        <Link className="study-nav-link mt-4" href={`/${certification.code}/quiz`}>
          문제 유형 연습
        </Link>
      </aside>
    </div>
  )
}
