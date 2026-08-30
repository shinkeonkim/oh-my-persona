"use client"

import type { AuthUser } from "@aws-study/shared"
import {
  BookOpenText,
  ChartLineUp,
  HourglassMedium,
  List,
  ShieldCheck,
  SignIn,
  SignOut,
  X,
} from "@phosphor-icons/react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { type JSX, useState } from "react"

import { clientApi } from "@/lib/client-api"

import { ThemeToggle } from "./theme-toggle"

const NAVIGATION = [
  { href: "/aif", label: "AIF" },
  { href: "/clf", label: "CLF" },
  { href: "/saa", label: "SAA" },
] as const

function AccountNavigation({
  user,
  onNavigate,
}: {
  readonly user: AuthUser | undefined
  readonly onNavigate: () => void
}): JSX.Element {
  const router = useRouter()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")

  async function logout(): Promise<void> {
    setBusy(true)
    setError("")
    try {
      await clientApi.post("auth/logout", { json: {} })
      onNavigate()
      router.push("/")
      router.refresh()
    } catch (cause: unknown) {
      if (!(cause instanceof Error)) throw cause
      setError("로그아웃하지 못했습니다. 다시 시도해 주세요.")
    } finally {
      setBusy(false)
    }
  }

  if (user === undefined) {
    return (
      <Link className="nav-link" href="/login" onClick={onNavigate}>
        <SignIn size={18} aria-hidden="true" /> 로그인
      </Link>
    )
  }

  return (
    <>
      {user.role === "pending" ? (
        <span className="nav-status">
          <HourglassMedium size={18} aria-hidden="true" /> 승인 대기
        </span>
      ) : (
        <Link className="nav-link" href="/dashboard" onClick={onNavigate}>
          <ChartLineUp size={18} aria-hidden="true" /> 대시보드
        </Link>
      )}
      {user.role === "admin" ? (
        <Link className="nav-link" href="/admin" onClick={onNavigate}>
          <ShieldCheck size={18} aria-hidden="true" /> 관리자
        </Link>
      ) : null}
      <button className="nav-link" type="button" onClick={logout} disabled={busy}>
        <SignOut size={18} aria-hidden="true" /> {busy ? "로그아웃 중" : "로그아웃"}
      </button>
      <span className="sr-only" role="alert">
        {error}
      </span>
    </>
  )
}

export function SiteHeader({ user }: { readonly user: AuthUser | undefined }): JSX.Element {
  const [open, setOpen] = useState(false)
  return (
    <header className="site-header">
      <div className="shell header-inner">
        <Link className="brand" href="/" aria-label="AWS Study 홈">
          <BookOpenText className="brand-mark" weight="duotone" aria-hidden="true" />
          <span>AWS Study</span>
        </Link>
        <nav className="nav-cluster nav-desktop" aria-label="자격증 탐색">
          {NAVIGATION.map((item) => (
            <Link className="nav-link" href={item.href} key={item.href}>
              {item.label}
            </Link>
          ))}
          <AccountNavigation user={user} onNavigate={() => setOpen(false)} />
          <ThemeToggle />
        </nav>
        <button
          className="icon-button mobile-navigation-toggle"
          type="button"
          onClick={() => setOpen((value) => !value)}
          aria-expanded={open}
          aria-controls="mobile-navigation"
          aria-label={open ? "메뉴 닫기" : "메뉴 열기"}
        >
          {open ? <X size={22} aria-hidden="true" /> : <List size={22} aria-hidden="true" />}
        </button>
      </div>
      {open ? (
        <nav id="mobile-navigation" className="shell mobile-navigation" aria-label="모바일 탐색">
          {NAVIGATION.map((item) => (
            <Link
              className="nav-link"
              href={item.href}
              key={item.href}
              onClick={() => setOpen(false)}
            >
              {item.label}
            </Link>
          ))}
          <AccountNavigation user={user} onNavigate={() => setOpen(false)} />
          <ThemeToggle />
        </nav>
      ) : null}
    </header>
  )
}
