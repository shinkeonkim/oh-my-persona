"use client"

import type { QuizSessionState } from "@aws-study/shared"
import { ArrowCounterClockwise, House } from "@phosphor-icons/react"

type CompletedQuizState = Extract<QuizSessionState, { readonly status: "completed" }>

type QuizResultsProps = {
  readonly state: CompletedQuizState
  readonly busy: boolean
  readonly error: string | null
  readonly onRestart: () => void
  readonly onHome: () => void
}

export function QuizResults({ state, busy, error, onRestart, onHome }: QuizResultsProps) {
  const percentage =
    state.results.total === 0 ? 0 : (state.results.correct / state.results.total) * 100
  return (
    <div className="quiz-shell quiz-results">
      <header className="quiz-page-header">
        <span className="eyebrow">Session complete</span>
        <h1>세션 완료</h1>
      </header>
      <section className="quiz-card quiz-score-card" aria-label="전체 점수">
        <strong>
          {state.results.correct} / {state.results.total}
        </strong>
        <span>{percentage.toFixed(1)}%</span>
      </section>
      <section className="quiz-card">
        <h2>카테고리별 결과</h2>
        <div className="quiz-result-table-wrap">
          <table className="quiz-result-table">
            <thead>
              <tr>
                <th scope="col">카테고리</th>
                <th scope="col">정답</th>
                <th scope="col">정답률</th>
              </tr>
            </thead>
            <tbody>
              {state.results.categories.map((category) => (
                <tr key={category.slug}>
                  <th scope="row">{category.slug}</th>
                  <td>
                    {category.correct}/{category.total}
                  </td>
                  <td>
                    {(category.total === 0 ? 0 : (category.correct / category.total) * 100).toFixed(
                      0,
                    )}
                    %
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      {error === null ? null : (
        <p className="quiz-error" role="alert">
          {error}
        </p>
      )}
      <div className="quiz-result-actions">
        <button
          className="quiz-button quiz-button-primary quiz-button-lg"
          disabled={busy}
          onClick={onRestart}
          type="button"
        >
          <ArrowCounterClockwise aria-hidden="true" size={19} /> 같은 조건으로 다시
        </button>
        <button
          className="quiz-button quiz-button-ghost quiz-button-lg"
          disabled={busy}
          onClick={onHome}
          type="button"
        >
          <House aria-hidden="true" size={19} /> 로비로
        </button>
      </div>
    </div>
  )
}
