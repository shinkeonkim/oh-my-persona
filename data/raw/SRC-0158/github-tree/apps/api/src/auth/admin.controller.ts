import { type Database, users } from "@aws-study/db"
import type { AuthUser } from "@aws-study/shared"
import { Controller, Get, HttpCode, NotFoundException, Param, Patch } from "@nestjs/common"
import { and, asc, eq } from "drizzle-orm"
import { z } from "zod"

import { InjectDatabase } from "../database/database.module.js"
import { Roles } from "./roles.decorator.js"

@Roles("admin")
@Controller("admin/users")
export class AdminController {
  constructor(@InjectDatabase() private readonly database: Database) {}

  @Get("pending")
  async pending(): Promise<readonly AuthUser[]> {
    const records = await this.database.query.users.findMany({
      where: and(eq(users.role, "pending"), eq(users.enabled, true)),
      orderBy: asc(users.createdAt),
    })
    return records.map((record) => ({
      id: record.id,
      email: record.email,
      displayName: record.displayName,
      role: record.role,
    }))
  }

  @Patch(":id/approve")
  async approve(@Param("id") rawId: string): Promise<AuthUser> {
    const id = z.string().uuid().parse(rawId)
    const [record] = await this.database
      .update(users)
      .set({ role: "reader", updatedAt: new Date() })
      .where(and(eq(users.id, id), eq(users.role, "pending"), eq(users.enabled, true)))
      .returning()
    if (record === undefined) throw new NotFoundException("Pending account request was not found")
    return {
      id: record.id,
      email: record.email,
      displayName: record.displayName,
      role: record.role,
    }
  }

  @Patch(":id/reject")
  @HttpCode(204)
  async reject(@Param("id") rawId: string): Promise<void> {
    const id = z.string().uuid().parse(rawId)
    const [record] = await this.database
      .update(users)
      .set({ enabled: false, updatedAt: new Date() })
      .where(and(eq(users.id, id), eq(users.role, "pending"), eq(users.enabled, true)))
      .returning({ id: users.id })
    if (record === undefined) throw new NotFoundException("Pending account request was not found")
  }
}
