import { redirect } from "next/navigation"
import type { JSX } from "react"

import { AdminModerationQueue } from "@/components/admin-moderation-queue"
import { getCurrentUser, getPendingUsers } from "@/lib/server-api"

export const dynamic = "force-dynamic"

export default async function AdminPage(): Promise<JSX.Element> {
  const user = await getCurrentUser()
  if (user === undefined) redirect("/login?next=/admin")
  if (user.role === "pending") redirect("/")
  if (user.role === "reader") redirect("/dashboard")
  const pendingUsers = await getPendingUsers()

  return (
    <div className="shell admin-page">
      <header className="page-header">
        <span className="eyebrow">Access control</span>
        <h1>계정 신청 관리</h1>
        <p className="hero-copy">
          학습 공간에 접근할 사용자의 <span className="whitespace-nowrap">계정 신청</span>을
          검토합니다.
        </p>
      </header>
      <AdminModerationQueue initialUsers={pendingUsers} />
    </div>
  )
}
