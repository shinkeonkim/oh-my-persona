import { defineConfig } from "drizzle-kit"
import { z } from "zod"

const databaseUrl = z
  .string()
  .url()
  .parse(process.env["DATABASE_URL"] ?? "postgresql://awsstudy:awsstudy@localhost:5432/awsstudy")

export default defineConfig({
  dialect: "postgresql",
  schema: "./src/schema/index.ts",
  out: "./drizzle",
  dbCredentials: { url: databaseUrl },
  strict: true,
  verbose: true,
})
