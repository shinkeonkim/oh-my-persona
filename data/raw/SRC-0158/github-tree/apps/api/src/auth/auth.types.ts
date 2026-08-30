import type { AuthUser } from "@aws-study/shared"
import type { FastifyRequest } from "fastify"
import { z } from "zod"

export const jwtPayloadSchema = z.object({
  sub: z.string().uuid(),
  email: z.string().email(),
  displayName: z.string().min(1),
  role: z.enum(["pending", "reader", "admin"]),
})

export type JwtPayload = z.infer<typeof jwtPayloadSchema>

export type AuthenticatedRequest = FastifyRequest & {
  user?: AuthUser
}
