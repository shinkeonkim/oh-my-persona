import { z } from "zod"

export const envSchema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  PORT: z.coerce.number().int().min(1).max(65535).default(3001),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  JWT_TTL_SECONDS: z.coerce.number().int().min(300).max(86400).default(3600),
  WEB_ORIGIN: z.string().url().default("http://localhost:3000"),
})

export type AppEnvironment = z.infer<typeof envSchema>

export function parseEnvironment(input: NodeJS.ProcessEnv): AppEnvironment {
  return envSchema.parse(input)
}
