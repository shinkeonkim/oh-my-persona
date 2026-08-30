"use client"

import type { QuizLobbyResponse, QuizSessionConfig } from "@aws-study/shared"
import { ArrowCounterClockwise, DownloadSimple, Play, Trash } from "@phosphor-icons/react"

import { eligibleQuestionCount, sessionQuestionCount } from "@/lib/quiz-lobby-state"
import { QuizSettings } from "./quiz-settings"

type QuizLobbyProps = {
  readonly title: string
  readonly lobby: QuizLobbyResponse
  readonly config: QuizSessionConfig
  readonly busy: boolean
  readonly error: string | null
  readonly onChange: (config: QuizSessionConfig) => void
  readonly onStart: () => void
  readonly onResume: () => void
  readonly onExport: () => void
  readonly onReset: () => void
}

export function QuizLobby(props: QuizLobbyProps) {
  const { title, lobby, config, busy, error } = props
  const eligible = eligibleQuestionCount(lobby.categories, config)
  const sessionSize = sessionQuestionCount(eligible, config.questionLimit)
  const allSelected = config.categorySlugs.length === lobby.categories.length
  const attemptedPct =
    lobby.stats.total === 0 ? 0 : (lobby.stats.attempted / lobby.stats.total) * 100
  const accuracy =
    lobby.stats.attempted === 0 ? 0 : (lobby.stats.correct / lobby.stats.attempted) * 100

  function update(patch: Partial<QuizSessionConfig>): void {
    props.onChange({ ...config, ...patch })
  }

  function toggleCategory(slug: string): void {
    const selected = new Set(config.categorySlugs)
    if (selected.has(slug)) selected.delete(slug)
    else selected.add(slug)
    update({
      categorySlugs: lobby.categories
        .map((category) => category.slug)
        .filter((item) => selected.has(item)),
    })
  }

  function startLabel(): string {
    if (eligible === 0) return "조건에 맞는 문항이 없습니다"
    if (config.questionLimit !== null && config.questionLimit < eligible) {
      return `${eligible}문항 중 ${sessionSize}개 세션 시작`
    }
    return `${sessionSize}문항 시작`
  }

  return (
    <div className="quiz-shell quiz-lobby">
      <header className="quiz-page-header">
        <span className="eyebrow">Practice lobby</span>
        <h1>{title} 문제 유형 연습</h1>
        <p className="muted">풀이 조건을 정한 뒤 나만의 연습 세션을 시작하세요.</p>
      </header>

      <section className="quiz-card" aria-labelledby="quiz-progress-title">
        <h2 id="quiz-progress-title">학습 진도</h2>
        <div className="quiz-stats-grid">
          <div>
            <strong>
              {lobby.stats.attempted} / {lobby.stats.total}
            </strong>
            <span>풀이 완료 ({attemptedPct.toFixed(1)}%)</span>
            <span className="quiz-progress-track" aria-hidden="true">
              <span style={{ transform: `scaleX(${attemptedPct / 100})` }} />
            </span>
          </div>
          <div>
            <strong>{accuracy.toFixed(1)}%</strong>
            <span>
              최근 정답률 ({lobby.stats.correct}/{lobby.stats.attempted})
            </span>
          </div>
          <div>
            <strong>{lobby.stats.wrong}</strong>
            <span>현재 오답 (재풀이 대상)</span>
          </div>
        </div>
        <div className="quiz-summary-actions">
          <button
            className="quiz-button quiz-button-ghost quiz-button-sm"
            disabled={busy || lobby.stats.wrong === 0}
            onClick={props.onExport}
            type="button"
          >
            <DownloadSimple aria-hidden="true" size={16} /> 오답 노트 내보내기
          </button>
          <button
            className="quiz-button quiz-button-danger quiz-button-sm"
            disabled={busy || lobby.stats.attempted === 0}
            onClick={props.onReset}
            type="button"
          >
            <Trash aria-hidden="true" size={16} /> 진도 초기화
          </button>
        </div>
      </section>

      {lobby.activeSessionId !== null ? (
        <section className="quiz-resume" aria-label="진행 중인 세션">
          <div>
            <strong>진행 중인 세션이 있습니다</strong>
            <span>마지막으로 풀던 문제부터 이어집니다.</span>
          </div>
          <button
            className="quiz-button quiz-button-ghost"
            disabled={busy}
            onClick={props.onResume}
            type="button"
          >
            <ArrowCounterClockwise aria-hidden="true" size={18} /> 이어 풀기
          </button>
        </section>
      ) : null}

      <QuizSettings config={config} update={update} />

      <section className="quiz-card quiz-category-card" aria-labelledby="quiz-category-title">
        <div className="quiz-section-head">
          <h2 id="quiz-category-title">
            카테고리 · {config.categorySlugs.length}/{lobby.categories.length} 선택됨
          </h2>
          <button
            className="quiz-button quiz-button-ghost quiz-button-sm"
            onClick={() =>
              update({
                categorySlugs: allSelected ? [] : lobby.categories.map((category) => category.slug),
              })
            }
            type="button"
          >
            {allSelected ? "전체 해제" : "전체 선택"}
          </button>
        </div>
        <div className="quiz-category-list">
          {lobby.categories.map((category, index) => {
            const checked = config.categorySlugs.includes(category.slug)
            const pct = category.total === 0 ? 0 : (category.attempted / category.total) * 100
            return (
              <label className="quiz-category-row" data-checked={checked} key={category.slug}>
                <input
                  checked={checked}
                  onChange={() => toggleCategory(category.slug)}
                  type="checkbox"
                />
                <span className="quiz-category-number">{String(index + 1).padStart(2, "0")}</span>
                <span className="quiz-category-name">{category.title}</span>
                <span className="quiz-category-count">
                  {category.attempted}/{category.total} · {Math.round(pct)}%
                </span>
                <span className="quiz-category-track" aria-hidden="true">
                  <span style={{ transform: `scaleX(${pct / 100})` }} />
                </span>
              </label>
            )
          })}
        </div>
      </section>

      {error === null ? null : (
        <p className="quiz-error" role="alert">
          {error}
        </p>
      )}
      <div className="quiz-start-bar">
        <button
          className="quiz-button quiz-button-primary quiz-button-lg"
          disabled={busy || eligible === 0 || config.categorySlugs.length === 0}
          onClick={props.onStart}
          type="button"
        >
          <Play aria-hidden="true" size={20} weight="fill" /> {busy ? "준비 중" : startLabel()}
        </button>
      </div>
    </div>
  )
}
