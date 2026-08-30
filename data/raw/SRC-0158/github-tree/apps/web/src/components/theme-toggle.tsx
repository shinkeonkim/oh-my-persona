"use client"

import { CircleHalf } from "@phosphor-icons/react"

function toggleTheme(): void {
  const root = document.documentElement
  const nextTheme = root.dataset["theme"] === "light" ? "dark" : "light"
  root.dataset["theme"] = nextTheme
  localStorage.setItem("aws-study-theme", nextTheme)
}

export function ThemeToggle() {
  return (
    <button className="icon-button" type="button" onClick={toggleTheme} aria-label="색상 테마 전환">
      <CircleHalf size={20} weight="duotone" aria-hidden="true" />
    </button>
  )
}
