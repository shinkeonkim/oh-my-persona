"use client"

import { authSessionSchema } from "@aws-study/shared"
import { HTTPError } from "ky"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { type FormEvent, type JSX, useState } from "react"

import { loginDestination } from "@/lib/auth-destination"
import { clientApi } from "@/lib/client-api"

export function AuthForm({
  mode,
  nextPath = "/dashboard",
}: {
  readonly mode: "login" | "register"
  readonly nextPath?: string
}): JSX.Element {
  const router = useRouter()
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)

  async function submit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault()
    setBusy(true)
    setError("")
    const data = new FormData(event.currentTarget)
    const payload = {
      email: String(data.get("email")),
      password: String(data.get("password")),
      ...(mode === "register" ? { displayName: String(data.get("displayName")) } : {}),
    }
    try {
      const response = await clientApi.post(`auth/${mode}`, { json: payload })
      const destination =
        mode === "login"
          ? loginDestination(authSessionSchema.parse(await response.json()).user.role, nextPath)
          : "/login"
      router.push(destination)
      router.refresh()
    } catch (cause) {
      setError(
        cause instanceof HTTPError
          ? "입력 정보 또는 계정 상태를 확인해 주세요."
          : "서버에 연결할 수 없습니다.",
      )
    } finally {
      setBusy(false)
    }
  }

  const registering = mode === "register"
  return (
    <form className="form-card" method="post" onSubmit={submit}>
      <span className="eyebrow">Private study space</span>
      <h1 className="mt-2 text-3xl font-bold tracking-tight">
        {registering ? "학습 계정 신청" : "학습 공간 로그인"}
      </h1>
      <p className="muted mt-2">
        {registering
          ? "신청 후 관리자의 승인이 필요합니다."
          : "승인된 계정으로 보호된 자료를 이어서 학습합니다."}
      </p>
      {registering ? (
        <div className="field">
          <label htmlFor="displayName">표시 이름</label>
          <input
            id="displayName"
            name="displayName"
            minLength={2}
            maxLength={40}
            required
            autoComplete="name"
          />
        </div>
      ) : null}
      <div className="field">
        <label htmlFor="email">이메일</label>
        <input id="email" name="email" type="email" required autoComplete="email" />
      </div>
      <div className="field">
        <label htmlFor="password">비밀번호</label>
        <input
          id="password"
          name="password"
          type="password"
          minLength={12}
          required
          autoComplete={registering ? "new-password" : "current-password"}
        />
      </div>
      {error !== "" ? (
        <p className="error-text mt-3" role="alert">
          {error}
        </p>
      ) : null}
      <button className="button button-primary mt-6 w-full" type="submit" disabled={busy}>
        {busy ? "처리 중" : registering ? "승인 요청" : "로그인"}
      </button>
      <p className="muted mt-5 text-sm">
        {registering ? (
          <>
            계정이 있나요?{" "}
            <Link className="text-[var(--accent)] underline" href="/login">
              로그인
            </Link>
          </>
        ) : (
          <>
            처음인가요?{" "}
            <Link className="text-[var(--accent)] underline" href="/register">
              계정 신청
            </Link>
          </>
        )}
      </p>
    </form>
  )
}
