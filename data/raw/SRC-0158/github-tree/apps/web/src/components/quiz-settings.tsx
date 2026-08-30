"use client"

import type { QuizSessionConfig } from "@aws-study/shared"

type QuizSettingsProps = {
  readonly config: QuizSessionConfig
  readonly update: (patch: Partial<QuizSessionConfig>) => void
}

const STANDARD_LIMITS = [null, 10, 25, 65] as const

function isStandardLimit(limit: number | null): boolean {
  return limit === null || limit === 10 || limit === 25 || limit === 65
}

export function QuizSettings({ config, update }: QuizSettingsProps) {
  const customLimit =
    config.questionLimit !== null && !isStandardLimit(config.questionLimit)
      ? config.questionLimit
      : 30
  return (
    <div className="quiz-settings-grid">
      <fieldset className="quiz-card">
        <legend>모드</legend>
        <div className="quiz-segment">
          {(["all", "unseen", "wrong"] as const).map((mode) => (
            <label key={mode}>
              <input
                checked={config.mode === mode}
                name="quiz-mode"
                onChange={() => update({ mode })}
                type="radio"
              />
              <span>{mode === "all" ? "전체" : mode === "unseen" ? "미풀이만" : "오답만"}</span>
            </label>
          ))}
        </div>
      </fieldset>
      <fieldset className="quiz-card">
        <legend>순서</legend>
        <div className="quiz-segment">
          {(["random", "sequential"] as const).map((order) => (
            <label key={order}>
              <input
                checked={config.order === order}
                name="quiz-order"
                onChange={() => update({ order })}
                type="radio"
              />
              <span>{order === "random" ? "랜덤" : "순차"}</span>
            </label>
          ))}
        </div>
      </fieldset>
      <fieldset className="quiz-card quiz-limit-card">
        <legend>세션 문항 수</legend>
        <div className="quiz-segment">
          {STANDARD_LIMITS.map((limit) => (
            <label key={limit ?? "all"}>
              <input
                checked={config.questionLimit === limit}
                name="quiz-limit"
                onChange={() => update({ questionLimit: limit })}
                type="radio"
              />
              <span>{limit === null ? "무제한" : limit === 65 ? "65 · 실전 모의고사" : limit}</span>
            </label>
          ))}
          <label className="quiz-custom-limit">
            <input
              checked={!isStandardLimit(config.questionLimit)}
              name="quiz-limit"
              onChange={() => update({ questionLimit: customLimit })}
              type="radio"
            />
            <span>커스텀</span>
            <input
              aria-label="커스텀 문항 수"
              max={2000}
              min={1}
              onChange={(event) =>
                update({ questionLimit: Math.max(1, Number(event.target.value)) })
              }
              type="number"
              value={customLimit}
            />
          </label>
        </div>
      </fieldset>
    </div>
  )
}
