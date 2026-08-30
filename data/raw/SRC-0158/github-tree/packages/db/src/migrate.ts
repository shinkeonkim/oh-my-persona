import { migrate } from "drizzle-orm/postgres-js/migrator"
import { z } from "zod"

import { createDatabase } from "./client"

const databaseUrl = z.string().url().parse(process.env["DATABASE_URL"])
const database = createDatabase(databaseUrl)

await migrate(database, { migrationsFolder: new URL("../drizzle", import.meta.url).pathname })
