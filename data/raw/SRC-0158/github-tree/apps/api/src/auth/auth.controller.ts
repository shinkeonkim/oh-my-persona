import {
  type AuthSession,
  type AuthUser,
  loginInputSchema,
  registerInputSchema,
} from "@aws-study/shared"
import { Body, Controller, Get, HttpCode, Inject, Post, Res } from "@nestjs/common"
import type { FastifyReply } from "fastify"

import { AllowPending } from "./allow-pending.decorator.js"
import { AuthService } from "./auth.service.js"
import { CurrentUser } from "./current-user.decorator.js"
import { Public } from "./public.decorator.js"

@Controller("auth")
export class AuthController {
  constructor(@Inject(AuthService) private readonly authService: AuthService) {}

  @Public()
  @Post("register")
  async register(@Body() body: unknown): Promise<AuthUser> {
    return this.authService.register(registerInputSchema.parse(body))
  }

  @Public()
  @HttpCode(200)
  @Post("login")
  async login(
    @Body() body: unknown,
    @Res({ passthrough: true }) reply: FastifyReply,
  ): Promise<AuthSession> {
    const session = await this.authService.login(loginInputSchema.parse(body))
    const secure = process.env["NODE_ENV"] === "production" ? "; Secure" : ""
    reply.header(
      "Set-Cookie",
      `aws_study_session=${session.accessToken}; HttpOnly; SameSite=Strict; Path=/; Expires=${new Date(session.expiresAt).toUTCString()}${secure}`,
    )
    return session
  }

  @AllowPending()
  @Get("me")
  me(@CurrentUser() user: AuthUser): AuthUser {
    return user
  }

  @Public()
  @Post("logout")
  @HttpCode(204)
  logout(@Res({ passthrough: true }) reply: FastifyReply): void {
    reply.header("Set-Cookie", "aws_study_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0")
  }
}
