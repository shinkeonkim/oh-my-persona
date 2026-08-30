import {
  type AuthUser,
  bookmarkInputSchema,
  certificationCodeSchema,
  progressUpdateSchema,
} from "@aws-study/shared"
import { Body, Controller, Get, Inject, Post, Query } from "@nestjs/common"

import { CurrentUser } from "../auth/current-user.decorator.js"
import { Roles } from "../auth/roles.decorator.js"
import { ProgressService } from "./progress.service.js"

@Roles("reader", "admin")
@Controller("progress")
export class ProgressController {
  constructor(@Inject(ProgressService) private readonly progressService: ProgressService) {}

  @Get("summary")
  summary(@CurrentUser() user: AuthUser) {
    return this.progressService.summary(user)
  }

  @Post("attempts")
  async record(@CurrentUser() user: AuthUser, @Body() body: unknown): Promise<void> {
    await this.progressService.record(user, progressUpdateSchema.parse(body))
  }

  @Post("bookmarks/toggle")
  toggleBookmark(
    @CurrentUser() user: AuthUser,
    @Body() body: unknown,
    @Query("certification") code: string,
  ) {
    return this.progressService.toggleBookmark(
      user,
      bookmarkInputSchema.parse(body),
      certificationCodeSchema.parse(code),
    )
  }
}
