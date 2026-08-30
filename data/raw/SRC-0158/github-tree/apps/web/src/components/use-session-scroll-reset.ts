"use client"

import type { QuizSessionState } from "@aws-study/shared"
import { useLayoutEffect } from "react"

export function useSessionScrollReset(session: QuizSessionState | null): void {
  useLayoutEffect(() => {
    if (session === null) return
    window.scrollTo(0, 0)
    const frame = window.requestAnimationFrame(() => window.scrollTo(0, 0))
    return () => window.cancelAnimationFrame(frame)
  }, [session])
}
