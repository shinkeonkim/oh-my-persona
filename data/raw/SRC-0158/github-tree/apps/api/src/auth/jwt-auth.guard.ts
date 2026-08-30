import { type Database, users } from "@aws-study/db"
import type { AuthUser } from "@aws-study/shared"
import {
  type CanActivate,
  type ExecutionContext,
  ForbiddenException,
  Inject,
  Injectable,
  UnauthorizedException,
} from "@nestjs/common"
import { Reflector } from "@nestjs/core"
import { JwtService } from "@nestjs/jwt"
import { eq } from "drizzle-orm"

import { InjectDatabase } from "../database/database.module.js"
import { ALLOW_PENDING_ROUTE } from "./allow-pending.decorator.js"
import { type AuthenticatedRequest, type JwtPayload, jwtPayloadSchema } from "./auth.types.js"
import { PUBLIC_ROUTE } from "./public.decorator.js"

@Injectable()
export class JwtAuthGuard implements CanActivate {
  constructor(
    @Inject(JwtService) private readonly jwtService: JwtService,
    @Inject(Reflector) private readonly reflector: Reflector,
    @InjectDatabase() private readonly database: Database,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const isPublic = this.reflector.getAllAndOverride<boolean>(PUBLIC_ROUTE, [
      context.getHandler(),
      context.getClass(),
    ])
    if (isPublic === true) return true

    const request = context.switchToHttp().getRequest<AuthenticatedRequest>()
    const token = this.extractToken(request)
    if (token === undefined) throw new UnauthorizedException("Authentication required")

    let payload: JwtPayload
    try {
      payload = jwtPayloadSchema.parse(await this.jwtService.verifyAsync(token))
    } catch (cause: unknown) {
      throw new UnauthorizedException("Invalid or expired session", { cause })
    }
    const record = await this.database.query.users.findFirst({ where: eq(users.id, payload.sub) })
    if (record === undefined || !record.enabled) {
      throw new UnauthorizedException("Session user is unavailable")
    }
    if (record.role !== payload.role) {
      throw new UnauthorizedException("Session role changed; sign in again")
    }
    const allowPending = this.reflector.getAllAndOverride<boolean>(ALLOW_PENDING_ROUTE, [
      context.getHandler(),
      context.getClass(),
    ])
    if (record.role === "pending" && allowPending !== true) {
      throw new ForbiddenException("Account approval is pending")
    }
    const user: AuthUser = {
      id: record.id,
      email: record.email,
      displayName: record.displayName,
      role: record.role,
    }
    request.user = user
    return true
  }

  private extractToken(request: AuthenticatedRequest): string | undefined {
    const cookie = request.headers.cookie
      ?.split(";")
      .map((entry) => entry.trim().split("="))
      .find(([name]) => name === "aws_study_session")?.[1]
    if (cookie !== undefined) return cookie
    const [scheme, token] = request.headers.authorization?.split(" ") ?? []
    return scheme === "Bearer" ? token : undefined
  }
}
