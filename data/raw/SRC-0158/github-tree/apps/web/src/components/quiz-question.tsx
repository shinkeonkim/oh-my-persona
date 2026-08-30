"use client"

import type { QuizAttemptResult, QuizSessionState } from "@aws-study/shared"
import { ArrowLeft, ArrowRight, Check, X } from "@phosphor-icons/react"
import { useEffect } from "react"

type ActiveQuizState = Extract<QuizSessionState, { readonly status: "active" }>

type QuizQuestionProps = {
  readonly state: ActiveQuizState
  readonly selected: readonly string[]
  readonly feedback: QuizAttemptResult | null
  readonly busy: boolean
  readonly error: string | null
  readonly onSelect: (key: string) => void
  readonly onSubmit: () => void
  readonly onNext: () => void
  readonly onQuit: () => void
}

export function QuizQuestion(props: QuizQuestionProps) {
  const { state, selected, feedback, busy, error } = props
  const { question } = state
  const selectedSet = new Set(selected)
  const answerSet = new Set(feedback?.answers ?? [])
  const progress = state.position / state.totalQuestions

  useEffect(() => {
    function handleKey(event: KeyboardEvent): void {
      if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement)
        return
      if (event.key === "Escape") {
        event.preventDefault()
        props.onQuit()
        return
      }
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault()
        if (feedback !== null) props.onNext()
        else if (selected.length > 0) props.onSubmit()
        return
      }
      const letterIndex = /^[a-e]$/i.test(event.key)
        ? event.key.toUpperCase().charCodeAt(0) - 65
        : -1
      const numberIndex = /^[1-5]$/.test(event.key) ? Number(event.key) - 1 : -1
      const option = question.options[letterIndex >= 0 ? letterIndex : numberIndex]
      if (option !== undefined && feedback === null) {
        event.preventDefault()
        props.onSelect(option.key)
      }
    }
    window.addEventListener("keydown", handleKey)
    return () => window.removeEventListener("keydown", handleKey)
  }, [feedback, props, question.options, selected.length])

  function optionState(key: string): string {
    if (feedback === null) return selectedSet.has(key) ? "selected" : "idle"
    if (answerSet.has(key)) return selectedSet.has(key) ? "correct" : "missed"
    return selectedSet.has(key) ? "wrong" : "idle"
  }

  return (
    <div className="quiz-shell quiz-active">
      <header className="quiz-session-header">
        <button className="quiz-button quiz-button-ghost" onClick={props.onQuit} type="button">
          <ArrowLeft aria-hidden="true" size={18} /> 로비
        </button>
        <strong>
          <span className="sr-only">문제 위치 </span>
          {state.position + 1} / {state.totalQuestions}
        </strong>
        <span className="quiz-session-progress" aria-hidden="true">
          <span style={{ transform: `scaleX(${progress})` }} />
        </span>
      </header>

      <main className="quiz-question-main">
        <div className="quiz-question-id">
          <span>{question.categorySlug}</span>
          {question.answerCount > 1 ? (
            <span className="quiz-answer-count">{question.answerCount}개 선택</span>
          ) : null}
        </div>
        <h1>{question.prompt}</h1>
        <div className="quiz-options" role={question.answerCount > 1 ? "group" : "radiogroup"}>
          {question.options.map((option, index) => (
            <label className="quiz-option" data-state={optionState(option.key)} key={option.key}>
              <input
                checked={selectedSet.has(option.key)}
                disabled={feedback !== null}
                name="quiz-answer"
                onChange={() => props.onSelect(option.key)}
                type={question.answerCount > 1 ? "checkbox" : "radio"}
              />
              <strong>{option.key}</strong>
              <span>{option.text}</span>
              <kbd>{index + 1}</kbd>
            </label>
          ))}
        </div>

        <div className="quiz-submit-bar">
          {feedback === null ? (
            <button
              className="quiz-button quiz-button-primary quiz-button-lg"
              disabled={busy || selected.length === 0}
              onClick={props.onSubmit}
              type="button"
            >
              {busy
                ? "채점 중"
                : question.answerCount > 1
                  ? `정답 확인 (${selected.length}/${question.answerCount} 선택됨)`
                  : "정답 확인"}
            </button>
          ) : (
            <>
              <div className="quiz-result-badge" data-correct={feedback.correct} aria-live="polite">
                {feedback.correct ? (
                  <Check aria-hidden="true" size={20} weight="bold" />
                ) : (
                  <X aria-hidden="true" size={20} weight="bold" />
                )}
                {feedback.correct ? "정답" : "오답"}
              </div>
              <button
                className="quiz-button quiz-button-primary quiz-button-lg"
                disabled={busy}
                onClick={props.onNext}
                type="button"
              >
                {feedback.completed ? "결과 보기" : "다음 문항"}{" "}
                <ArrowRight aria-hidden="true" size={18} />
              </button>
            </>
          )}
        </div>

        {error === null ? null : (
          <p className="quiz-error" role="alert">
            {error}
          </p>
        )}
        {feedback === null ? null : (
          <section className="quiz-explanation" aria-live="polite">
            <div>
              <span>제출</span>
              <strong>{selected.join(", ")}</strong>
              <span>정답</span>
              <strong>{feedback.answers.join(", ")}</strong>
            </div>
            <h2>해설</h2>
            <p>{feedback.explanation}</p>
          </section>
        )}
      </main>
    </div>
  )
}
