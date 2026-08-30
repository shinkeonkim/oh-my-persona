import { drizzle, type PostgresJsDatabase } from "drizzle-orm/postgres-js"
import postgres from "postgres"

import * as schema from "./schema"

export type Database = PostgresJsDatabase<typeof schema>

export function createDatabase(connectionString: string): Database {
  const client = postgres(connectionString, {
    max: 10,
    idle_timeout: 20,
    connect_timeout: 10,
    prepare: false,
  })
  return drizzle(client, { schema })
}
