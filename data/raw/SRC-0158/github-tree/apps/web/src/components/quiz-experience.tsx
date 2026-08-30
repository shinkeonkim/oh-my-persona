"use client"

import type { CertificationCode } from "@aws-study/shared"
import { useEffect, useState } from "react"

import {
  type QuizAttemptResult,
  type QuizLobbyResponse,
  type QuizSessionConfig,
  type QuizSessionState,
  quizAttemptResultSchema,
  quizLobbyResponseSchema,
  quizSessionStateSchema,
  quizWrongNotesSchema,
} from "@/lib/api-types"
import { clientApi } from "@/lib/client-api"
import { buildWrongNotesMarkdown } from "@/lib/quiz-lobby-state"
import { QuizLobby } from "./quiz-lobby"
import { QuizQuestion } from "./quiz-question"
import { QuizResults } from "./quiz-results"
import { useSessionScrollReset } from "./use-session-scroll-reset"

type QuizExperienceProps = {
  readonly certificationCode: CertificationCode
  readonly certificationTitle: string
  readonly initialLobby: QuizLobbyResponse
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "요청을 처리하지 못했습니다. 다시 시도해 주세요."
}

export function QuizExperience({
  certificationCode,
  certificationTitle,
  initialLobby,
}: QuizExperienceProps) {
  const [lobby, setLobby] = useState(initialLobby)
  const [config, setConfig] = useState<QuizSessionConfig>(initialLobby.preference)
  const [session, setSession] = useState<QuizSessionState | null>(null)
  const [selected, setSelected] = useState<readonly string[]>([])
  const [feedback, setFeedback] = useState<QuizAttemptResult | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useSessionScrollReset(session)

  function showSession(next: QuizSessionState): void {
    if (document.activeElement instanceof HTMLElement) document.activeElement.blur()
    window.scrollTo(0, 0)
    setSession(next)
    setSelected([])
    setFeedback(null)
  }

  useEffect(() => {
    if (config.categorySlugs.length === 0) return
    const timer = window.setTimeout(() => {
      void clientApi
        .put("quiz/preferences", { json: config })
        .then(() => setError(null))
        .catch((caught: unknown) => setError(errorMessage(caught)))
    }, 350)
    return () => window.clearTimeout(timer)
  }, [config])

  async function refreshLobby(): Promise<void> {
    const response = quizLobbyResponseSchema.parse(
      await clientApi.get(`quiz/lobby/${certificationCode}`).json(),
    )
    setLobby(response)
    setConfig(response.preference)
  }

  async function start(parentSessionId: string | null = null): Promise<void> {
    if (config.categorySlugs.length === 0) return
    setBusy(true)
    setError(null)
    try {
      const next = quizSessionStateSchema.parse(
        await clientApi.post("quiz/sessions", { json: { ...config, parentSessionId } }).json(),
      )
      showSession(next)
    } catch (caught: unknown) {
      setError(errorMessage(caught))
    } finally {
      setBusy(false)
    }
  }

  async function resume(): Promise<void> {
    if (lobby.activeSessionId === null) return
    setBusy(true)
    setError(null)
    try {
      const next = quizSessionStateSchema.parse(
        await clientApi.get(`quiz/sessions/${lobby.activeSessionId}`).json(),
      )
      setConfig(next.config)
      showSession(next)
    } catch (caught: unknown) {
      setError(errorMessage(caught))
    } finally {
      setBusy(false)
    }
  }

  function selectAnswer(key: string): void {
    if (session?.status !== "active" || feedback !== null) return
    if (session.question.answerCount === 1) {
      setSelected([key])
      return
    }
    setSelected((current) =>
      current.includes(key) ? current.filter((item) => item !== key) : [...current, key],
    )
  }

  async function submit(): Promise<void> {
    if (session?.status !== "active" || selected.length === 0) return
    setBusy(true)
    setError(null)
    try {
      const result = quizAttemptResultSchema.parse(
        await clientApi
          .post("quiz/attempts", {
            json: {
              sessionId: session.sessionId,
              questionId: session.question.questionId,
              selectedAnswers: selected,
            },
          })
          .json(),
      )
      setFeedback(result)
    } catch (caught: unknown) {
      setError(errorMessage(caught))
    } finally {
      setBusy(false)
    }
  }

  async function next(): Promise<void> {
    if (session === null) return
    setBusy(true)
    setError(null)
    try {
      const nextState = quizSessionStateSchema.parse(
        await clientApi.get(`quiz/sessions/${session.sessionId}`).json(),
      )
      showSession(nextState)
    } catch (caught: unknown) {
      setError(errorMessage(caught))
    } finally {
      setBusy(false)
    }
  }

  async function quit(): Promise<void> {
    if (session?.status !== "active") return
    if (!window.confirm("세션을 종료하시겠습니까? 지금까지의 진도는 저장됩니다.")) return
    setBusy(true)
    try {
      await clientApi.post(`quiz/sessions/${session.sessionId}/abandon`)
      await refreshLobby()
      setSession(null)
      setSelected([])
      setFeedback(null)
      setError(null)
    } catch (caught: unknown) {
      setError(errorMessage(caught))
    } finally {
      setBusy(false)
    }
  }

  async function home(): Promise<void> {
    setBusy(true)
    try {
      await refreshLobby()
      setSession(null)
      setError(null)
    } catch (caught: unknown) {
      setError(errorMessage(caught))
    } finally {
      setBusy(false)
    }
  }

  async function exportWrongNotes(): Promise<void> {
    setBusy(true)
    try {
      const notes = quizWrongNotesSchema.parse(
        await clientApi.get(`quiz/wrong-notes/${certificationCode}`).json(),
      )
      const blob = new Blob(
        [buildWrongNotesMarkdown(certificationCode.toUpperCase(), notes, new Date().toISOString())],
        { type: "text/markdown;charset=utf-8" },
      )
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement("a")
      anchor.href = url
      anchor.download = `${certificationCode}-wrong-notes.md`
      anchor.click()
      window.setTimeout(() => URL.revokeObjectURL(url), 1_000)
      setError(null)
    } catch (caught: unknown) {
      setError(errorMessage(caught))
    } finally {
      setBusy(false)
    }
  }

  async function resetProgress(): Promise<void> {
    if (!window.confirm("이 자격증의 진도와 오답 기록을 모두 초기화하시겠습니까?")) return
    setBusy(true)
    try {
      await clientApi.delete(`quiz/progress/${certificationCode}`)
      await refreshLobby()
      setError(null)
    } catch (caught: unknown) {
      setError(errorMessage(caught))
    } finally {
      setBusy(false)
    }
  }

  if (session?.status === "active") {
    return (
      <QuizQuestion
        state={session}
        selected={selected}
        feedback={feedback}
        busy={busy}
        error={error}
        onSelect={selectAnswer}
        onSubmit={submit}
        onNext={next}
        onQuit={quit}
      />
    )
  }
  if (session?.status === "completed") {
    return (
      <QuizResults
        state={session}
        busy={busy}
        error={error}
        onRestart={() => start(session.sessionId)}
        onHome={home}
      />
    )
  }
  return (
    <QuizLobby
      title={certificationTitle}
      lobby={lobby}
      config={config}
      busy={busy}
      error={error}
      onChange={setConfig}
      onStart={() => start()}
      onResume={resume}
      onExport={exportWrongNotes}
      onReset={resetProgress}
    />
  )
}
