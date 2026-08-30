import type { UserRole } from "@aws-study/shared"

export function loginDestination(role: UserRole, nextPath: string): string {
  return role === "pending" ? "/" : nextPath
}
