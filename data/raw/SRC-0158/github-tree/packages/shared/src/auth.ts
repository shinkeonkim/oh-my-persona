import { z } from "zod"

export const userRoleSchema = z.enum(["pending", "reader", "admin"])

export const loginInputSchema = z.object({
  email: z.string().trim().toLowerCase().email(),
  password: z.string().min(12).max(128),
})

export const registerInputSchema = loginInputSchema.extend({
  displayName: z.string().trim().min(2).max(40),
})

export const authUserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  displayName: z.string().min(1),
  role: userRoleSchema,
})

export const authSessionSchema = z.object({
  user: authUserSchema,
  accessToken: z.string().min(1),
  expiresAt: z.string().datetime(),
})

export type UserRole = z.infer<typeof userRoleSchema>
export type LoginInput = z.infer<typeof loginInputSchema>
export type RegisterInput = z.infer<typeof registerInputSchema>
export type AuthUser = z.infer<typeof authUserSchema>
export type AuthSession = z.infer<typeof authSessionSchema>
