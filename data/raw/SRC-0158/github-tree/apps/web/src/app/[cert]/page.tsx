import { certificationCodeSchema, findCertification } from "@aws-study/shared"
import { ArrowRight, LockKey } from "@phosphor-icons/react/dist/ssr"
import type { Metadata } from "next"
import Link from "next/link"
import { notFound } from "next/navigation"

import { getCategories } from "@/lib/server-api"

export const dynamic = "force-dynamic"

type PageProps = { readonly params: Promise<{ readonly cert: string }> }

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const parsed = certificationCodeSchema.safeParse((await params).cert)
  return parsed.success
    ? { title: findCertification(parsed.data).shortTitle }
    : { title: "Not found" }
}

export default async function CertificationPage({ params }: PageProps) {
  const parsed = certificationCodeSchema.safeParse((await params).cert)
  if (!parsed.success) notFound()
  const certification = findCertification(parsed.data)
  const categories = await getCategories(parsed.data)
  return (
    <div className="shell">
      <header className="page-header">
        <span className="eyebrow">{certification.examCode}</span>
        <h1>{certification.title}</h1>
        <p className="hero-copy">{certification.description}</p>
        <div className="button-row">
          <Link className="button button-primary" href={`/${certification.code}/quiz`}>
            문제 유형 연습 <ArrowRight size={18} aria-hidden="true" />
          </Link>
          <span className="cert-meta inline-flex items-center gap-2">
            <LockKey size={18} aria-hidden="true" /> 문제 풀이는 로그인 후 제공
          </span>
        </div>
      </header>
      <section aria-labelledby="category-title">
        <div className="section-heading">
          <span className="eyebrow">Study map</span>
          <h2 id="category-title">카테고리별 학습 노트</h2>
        </div>
        <div className="category-grid">
          {categories.map((category) => (
            <Link
              className="category-link"
              href={`/${certification.code}/study/${category.slug}`}
              key={category.slug}
            >
              <span>
                <span className="cert-meta">{String(category.order).padStart(2, "0")}</span>
                <strong className="block">{category.title}</strong>
              </span>
              <ArrowRight size={18} aria-hidden="true" />
            </Link>
          ))}
        </div>
      </section>
    </div>
  )
}
