import { HourglassMedium } from "@phosphor-icons/react/dist/ssr"
import type { JSX } from "react"

export default function AdminLoading(): JSX.Element {
  return (
    <div className="shell admin-page">
      <header className="page-header">
        <span className="eyebrow">Access control</span>
        <h1>계정 신청 관리</h1>
      </header>
      <section className="moderation-panel" aria-busy="true" aria-label="계정 신청 불러오는 중">
        <div className="moderation-empty">
          <HourglassMedium className="approval-icon" size={28} aria-hidden="true" />
          <h2>신청 목록을 불러오는 중입니다</h2>
          <p className="muted">잠시만 기다려 주세요.</p>
        </div>
      </section>
    </div>
  )
}
