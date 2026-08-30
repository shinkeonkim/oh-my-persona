import { certificationCodeSchema, findCertification } from "@aws-study/shared"
import type { Metadata } from "next"
import { notFound } from "next/navigation"

import { ServiceMap } from "@/components/service-map"
import { AIF_SERVICE_GROUPS, AIF_TOTAL_NODES } from "@/data/aif-service-map"

type PageProps = { readonly params: Promise<{ readonly cert: string }> }

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const parsed = certificationCodeSchema.safeParse((await params).cert)
  return parsed.success
    ? { title: `${findCertification(parsed.data).shortTitle} 서비스 지도` }
    : { title: "Not found" }
}

export default async function ServicesPage({ params }: PageProps) {
  const parsed = certificationCodeSchema.safeParse((await params).cert)
  if (!parsed.success) notFound()

  const certification = findCertification(parsed.data)

  // Currently only AIF has a service map
  if (parsed.data !== "aif") notFound()

  return (
    <div className="shell">
      <header className="page-header">
        <span className="eyebrow">{certification.examCode}</span>
        <h1>{certification.shortTitle} 서비스 지도</h1>
        <p className="hero-copy">
          AIF-C01 시험 범위의 {AIF_TOTAL_NODES}개 핵심 서비스와 개념을 5개 그룹으로 정리했습니다. 각
          노드를 선택하면 관련 학습 노트로 이동합니다.
        </p>
      </header>
      <ServiceMap certCode={parsed.data} groups={AIF_SERVICE_GROUPS} />
    </div>
  )
}
