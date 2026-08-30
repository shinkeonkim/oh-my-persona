"use client"

import { type AuthUser, authUserSchema } from "@aws-study/shared"
import { Check, UserMinus } from "@phosphor-icons/react"
import { HTTPError } from "ky"
import { type JSX, useState } from "react"

import { clientApi } from "@/lib/client-api"

type Decision = "approve" | "reject"
type BusyDecision = { readonly userId: string; readonly decision: Decision }

export function AdminModerationQueue({
  initialUsers,
}: {
  readonly initialUsers: readonly AuthUser[]
}): JSX.Element {
  const [users, setUsers] = useState(initialUsers)
  const [busyDecision, setBusyDecision] = useState<BusyDecision>()
  const [status, setStatus] = useState("")
  const [error, setError] = useState("")

  async function refreshQueue(): Promise<boolean> {
    try {
      const json = await clientApi.get("admin/users/pending").json()
      setUsers(authUserSchema.array().parse(json))
      return true
    } catch (cause: unknown) {
      if (!(cause instanceof Error)) throw cause
      return false
    }
  }

  async function decide(user: AuthUser, decision: Decision): Promise<void> {
    setBusyDecision({ userId: user.id, decision })
    setStatus("")
    setError("")
    try {
      await clientApi.patch(`admin/users/${user.id}/${decision}`, { json: {} })
      setUsers((current) => current.filter((candidate) => candidate.id !== user.id))
      setStatus(
        `${user.displayName}님의 신청을 ${decision === "approve" ? "승인" : "거부"} 처리했습니다.`,
      )
    } catch (cause: unknown) {
      if (!(cause instanceof Error)) throw cause
      if (cause instanceof HTTPError && cause.response.status === 404) {
        setUsers((current) => current.filter((candidate) => candidate.id !== user.id))
        setStatus(`${user.displayName}님의 신청은 이미 처리되었습니다.`)
        return
      }
      const refreshed = await refreshQueue()
      setError(
        refreshed
          ? "처리 결과를 확인하지 못해 신청 목록을 새로 고쳤습니다."
          : "처리 결과를 확인하지 못했습니다. 페이지를 새로 고침해 주세요.",
      )
    } finally {
      setBusyDecision(undefined)
    }
  }

  return (
    <section className="moderation-panel" aria-labelledby="moderation-title">
      <div className="moderation-heading">
        <div>
          <h2 id="moderation-title">승인 대기 계정</h2>
          <p className="muted">
            신청 정보를 확인한 뒤 학습 공간 <span className="whitespace-nowrap">접근 여부</span>를
            결정합니다.
          </p>
        </div>
        <span className="moderation-count">{users.length}건</span>
      </div>
      {users.length === 0 ? (
        <div className="moderation-empty">
          <ShieldEmptyState />
          <h3>처리할 신청이 없습니다</h3>
          <p className="muted">새 계정 신청이 들어오면 이 목록에 표시됩니다.</p>
        </div>
      ) : (
        <ul className="moderation-list">
          {users.map((user) => {
            const approving =
              busyDecision?.userId === user.id && busyDecision.decision === "approve"
            const rejecting = busyDecision?.userId === user.id && busyDecision.decision === "reject"
            return (
              <li className="moderation-row" key={user.id}>
                <div className="moderation-identity">
                  <strong>{user.displayName}</strong>
                  <span>{user.email}</span>
                </div>
                <div className="moderation-actions">
                  <button
                    className="button button-primary"
                    type="button"
                    disabled={busyDecision !== undefined}
                    onClick={() => decide(user, "approve")}
                  >
                    <Check size={18} aria-hidden="true" /> {approving ? "처리 중" : "승인"}
                  </button>
                  <button
                    className="button button-danger"
                    type="button"
                    disabled={busyDecision !== undefined}
                    onClick={() => decide(user, "reject")}
                  >
                    <UserMinus size={18} aria-hidden="true" /> {rejecting ? "처리 중" : "거부"}
                  </button>
                </div>
              </li>
            )
          })}
        </ul>
      )}
      <p className="status-message" role="status" aria-live="polite">
        {status}
      </p>
      {error !== "" ? (
        <p className="error-text" role="alert">
          {error}
        </p>
      ) : null}
    </section>
  )
}

function ShieldEmptyState(): JSX.Element {
  return <Check className="moderation-empty-icon" size={28} aria-hidden="true" />
}
