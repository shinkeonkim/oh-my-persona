import { CERTIFICATIONS } from "@aws-study/shared"
import { ArrowRight } from "@phosphor-icons/react/dist/ssr"
import Link from "next/link"

export function CertificationRail() {
  return (
    <nav className="cert-rail" aria-label="AWS 자격증 트랙">
      {CERTIFICATIONS.map((certification) => (
        <Link className="cert-link" href={`/${certification.code}`} key={certification.code}>
          <span className="cert-code">{certification.code.toUpperCase()}</span>
          <span>
            <span className="cert-title block">{certification.shortTitle}</span>
            <span className="cert-meta">{certification.examCode}</span>
          </span>
          <ArrowRight size={16} aria-hidden="true" />
        </Link>
      ))}
    </nav>
  )
}
