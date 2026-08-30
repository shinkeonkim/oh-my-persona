import { createDatabase, users } from "@aws-study/db"
import { hash } from "@node-rs/argon2"
import { z } from "zod"

const inputSchema = z.object({
  databaseUrl: z.url(),
  email: z.email(),
  password: z.string().min(12),
  displayName: z.string().min(2).max(40),
})

const input = inputSchema.parse({
  databaseUrl: process.env["DATABASE_URL"],
  email: process.env["ADMIN_EMAIL"],
  password: process.env["ADMIN_PASSWORD"],
  displayName: process.env["ADMIN_DISPLAY_NAME"],
})
const database = createDatabase(input.databaseUrl)

await database
  .insert(users)
  .values({
    email: input.email.toLowerCase(),
    displayName: input.displayName,
    passwordHash: await hash(input.password),
    role: "admin",
  })
  .onConflictDoUpdate({
    target: users.email,
    set: {
      displayName: input.displayName,
      passwordHash: await hash(input.password),
      role: "admin",
      enabled: true,
      updatedAt: new Date(),
    },
  })

console.info(`Admin account is ready: ${input.email.toLowerCase()}`)
