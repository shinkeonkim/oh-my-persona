import { ArrowRight } from "@phosphor-icons/react/dist/ssr"
import Link from "next/link"

import { CertificationRail } from "@/components/certification-rail"
import { ServiceMap } from "@/components/service-map"
import { AIF_SERVICE_GROUPS } from "@/data/aif-service-map"

export default function HomePage() {
  return (
    <>
      <section className="hero">
        <div className="shell hero-grid">
          <div>
            <h1>AWS Study</h1>
            <div className="button-row">
              <Link className="button button-primary" href="/aif">
                AIF 학습 시작 <ArrowRight size={18} aria-hidden="true" />
              </Link>
              <Link className="button button-secondary" href="/aif/services">
                서비스 지도 보기
              </Link>
            </div>
          </div>
          <CertificationRail />
        </div>
      </section>
      <section className="section shell" aria-labelledby="service-map-heading">
        <h2 id="service-map-heading" className="sr-only">
          AIF 서비스 지도
        </h2>
        <ServiceMap certCode="aif" groups={AIF_SERVICE_GROUPS} compact />
        <div className="button-row mt-8">
          <Link className="button button-secondary" href="/aif/services">
            전체 서비스 지도 보기 <ArrowRight size={18} aria-hidden="true" />
          </Link>
        </div>
      </section>
    </>
  )
}
