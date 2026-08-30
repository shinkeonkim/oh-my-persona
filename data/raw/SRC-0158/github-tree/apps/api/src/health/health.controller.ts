import type { Database } from "@aws-study/db"
import { Controller, Get } from "@nestjs/common"
import { sql } from "drizzle-orm"

import { Public } from "../auth/public.decorator.js"
import { InjectDatabase } from "../database/database.module.js"

@Public()
@Controller()
export class HealthController {
  constructor(@InjectDatabase() private readonly database: Database) {}

  @Get("healthz")
  health(): { readonly status: "ok" } {
    return { status: "ok" }
  }

  @Get("readyz")
  async ready(): Promise<{ readonly status: "ready" }> {
    await this.database.execute(sql`select 1`)
    return { status: "ready" }
  }
}
