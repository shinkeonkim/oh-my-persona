import { HourglassMedium } from "@phosphor-icons/react/dist/ssr"
import Link from "next/link"
import type { JSX } from "react"

export function PendingApprovalNotice(): JSX.Element {
  return (
    <div className="shell approval-shell">
      <section className="approval-panel" aria-labelledby="approval-title">
        <HourglassMedium className="approval-icon" size={32} weight="duotone" aria-hidden="true" />
        <span className="eyebrow">Approval pending</span>
        <h1 id="approval-title">
          계정 승인을 <span className="whitespace-nowrap">기다리고 있습니다</span>
        </h1>
        <p className="muted">
          관리자가 계정 신청을 검토 중입니다. 승인되면 대시보드와 문제 풀이를 이용할 수 있습니다.
        </p>
        <Link className="button button-secondary" href="/">
          공개 학습 자료로 돌아가기
        </Link>
      </section>
    </div>
  )
}
