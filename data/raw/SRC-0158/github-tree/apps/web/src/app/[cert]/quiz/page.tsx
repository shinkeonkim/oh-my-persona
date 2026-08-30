import { certificationCodeSchema, findCertification } from "@aws-study/shared"
import { notFound, redirect } from "next/navigation"
import type { JSX } from "react"

import { PendingApprovalNotice } from "@/components/pending-approval-notice"
import { QuizExperience } from "@/components/quiz-experience"
import { getCurrentUser, getQuizLobby } from "@/lib/server-api"

export const dynamic = "force-dynamic"

type PageProps = {
  readonly params: Promise<{ readonly cert: string }>
}

export default async function QuizPage({ params }: PageProps): Promise<JSX.Element> {
  const parsed = certificationCodeSchema.safeParse((await params).cert)
  if (!parsed.success) notFound()
  const user = await getCurrentUser()
  if (user === undefined) redirect(`/login?next=/${parsed.data}/quiz`)
  if (user.role === "pending") return <PendingApprovalNotice />

  const certification = findCertification(parsed.data)
  const lobby = await getQuizLobby(parsed.data)

  return (
    <QuizExperience
      certificationCode={parsed.data}
      certificationTitle={certification.shortTitle}
      initialLobby={lobby}
    />
  )
}
