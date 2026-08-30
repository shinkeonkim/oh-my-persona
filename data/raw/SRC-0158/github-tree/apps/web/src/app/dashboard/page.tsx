import { redirect } from "next/navigation"
import type { JSX } from "react"

import { PendingApprovalNotice } from "@/components/pending-approval-notice"
import { getCurrentUser, getProgressSummary } from "@/lib/server-api"

export const dynamic = "force-dynamic"

export default async function DashboardPage(): Promise<JSX.Element> {
  const user = await getCurrentUser()
  if (user === undefined) redirect("/login?next=/dashboard")
  if (user.role === "pending") return <PendingApprovalNotice />
  const summaries = await getProgressSummary()
  const attempted = summaries.reduce((total, item) => total + item.attempted, 0)
  const correct = summaries.reduce((total, item) => total + item.correct, 0)
  const accuracy = attempted === 0 ? 0 : Math.round((correct / attempted) * 100)
  return (
    <div className="shell">
      <header className="page-header">
        <span className="eyebrow">Learning record</span>
        <h1>개인 학습 대시보드</h1>
        <p className="hero-copy">서버에 저장된 풀이 기록을 자격증별로 확인합니다.</p>
      </header>
      <dl className="metric-strip">
        <div className="metric">
          <dt>풀이 기록</dt>
          <dd>{attempted}</dd>
        </div>
        <div className="metric">
          <dt>최근 정답</dt>
          <dd>{correct}</dd>
        </div>
        <div className="metric">
          <dt>정확도</dt>
          <dd>{accuracy}%</dd>
        </div>
      </dl>
      <section className="section">
        <div className="section-heading">
          <span className="eyebrow">By certification</span>
          <h2>자격증별 기록</h2>
        </div>
        <div className="category-grid">
          {summaries.length === 0 ? (
            <div className="panel">
              <h3>아직 기록이 없습니다</h3>
              <p className="muted">자격증 페이지에서 문제 유형 연습을 시작하세요.</p>
            </div>
          ) : (
            summaries.map((summary) => (
              <article className="panel" key={summary.certificationCode}>
                <span className="cert-code">{summary.certificationCode.toUpperCase()}</span>
                <h3 className="mt-2">{summary.attempted}회 풀이</h3>
                <p className="muted">최근 정답 {summary.correct}회</p>
              </article>
            ))
          )}
        </div>
      </section>
    </div>
  )
}
