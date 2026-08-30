import type { AuthUser, CertificationCode, QuizResponse } from "@aws-study/shared"
import { authUserSchema, quizLobbyResponseSchema, quizResponseSchema } from "@aws-study/shared"
import ky, { HTTPError } from "ky"
import { cookies } from "next/headers"

import {
  categoriesResponseSchema,
  progressResponseSchema,
  studyNoteResponseSchema,
} from "./api-types"

const serverApi = ky.create({
  prefix: process.env["API_INTERNAL_URL"] ?? "http://localhost:3001/api",
  timeout: 10_000,
  retry: { limit: 1 },
})

async function sessionHeaders(): Promise<Headers> {
  const session = (await cookies()).get("aws_study_session")
  const headers = new Headers()
  if (session !== undefined) headers.set("cookie", `aws_study_session=${session.value}`)
  return headers
}

export async function getCategories(code: CertificationCode) {
  const json = await serverApi.get(`content/categories/${code}`).json()
  return categoriesResponseSchema.parse(json)
}

export async function getStudyNote(code: CertificationCode, slug: string) {
  const json = await serverApi.get(`content/notes/${code}/${slug}`).json()
  return studyNoteResponseSchema.parse(json)
}

type QuizQueryParams = {
  readonly category?: string
  readonly page?: number
  readonly pageSize?: number
}

export async function getQuiz(
  code: CertificationCode,
  query: QuizQueryParams = {},
): Promise<QuizResponse> {
  const searchParams: Record<string, string | number> = {}
  if (query.page !== undefined) searchParams["page"] = query.page
  if (query.pageSize !== undefined) searchParams["pageSize"] = query.pageSize
  if (query.category !== undefined) searchParams["category"] = query.category
  const json = await serverApi
    .get(`content/quiz/${code}`, { searchParams, headers: await sessionHeaders() })
    .json()
  return quizResponseSchema.parse(json)
}

export async function getProgressSummary() {
  const json = await serverApi.get("progress/summary", { headers: await sessionHeaders() }).json()
  return progressResponseSchema.parse(json)
}

export async function getQuizLobby(code: CertificationCode) {
  const json = await serverApi.get(`quiz/lobby/${code}`, { headers: await sessionHeaders() }).json()
  return quizLobbyResponseSchema.parse(json)
}

export async function getCurrentUser(): Promise<AuthUser | undefined> {
  if (!(await hasSession())) return undefined
  try {
    const json = await serverApi.get("auth/me", { headers: await sessionHeaders() }).json()
    return authUserSchema.parse(json)
  } catch (cause: unknown) {
    if (cause instanceof HTTPError && cause.response.status === 401) return undefined
    throw cause
  }
}

export async function getPendingUsers(): Promise<readonly AuthUser[]> {
  const json = await serverApi
    .get("admin/users/pending", { headers: await sessionHeaders() })
    .json()
  return authUserSchema.array().parse(json)
}

export async function hasSession(): Promise<boolean> {
  return (await cookies()).has("aws_study_session")
}
