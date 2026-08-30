import { type Database, users } from "@aws-study/db"
import type { AuthSession, AuthUser, LoginInput, RegisterInput } from "@aws-study/shared"
import { ConflictException, Inject, Injectable, UnauthorizedException } from "@nestjs/common"
import { JwtService } from "@nestjs/jwt"
import { hash, verify } from "@node-rs/argon2"
import { eq } from "drizzle-orm"

import { APP_ENVIRONMENT } from "../config/config.module.js"
import type { AppEnvironment } from "../config/env.js"
import { InjectDatabase } from "../database/database.module.js"

@Injectable()
export class AuthService {
  constructor(
    @InjectDatabase() private readonly database: Database,
    @Inject(JwtService) private readonly jwtService: JwtService,
    @Inject(APP_ENVIRONMENT) private readonly environment: AppEnvironment,
  ) {}

  async register(input: RegisterInput): Promise<AuthUser> {
    const existing = await this.database.query.users.findFirst({
      where: eq(users.email, input.email),
    })
    if (existing !== undefined) throw new ConflictException("Email is already registered")

    const [record] = await this.database
      .insert(users)
      .values({ ...input, passwordHash: await hash(input.password) })
      .returning()
    if (record === undefined) throw new TypeError("User insert returned no record")
    return this.toAuthUser(record)
  }

  async login(input: LoginInput): Promise<AuthSession> {
    const record = await this.database.query.users.findFirst({
      where: eq(users.email, input.email),
    })
    if (
      record === undefined ||
      !record.enabled ||
      !(await verify(record.passwordHash, input.password))
    ) {
      throw new UnauthorizedException("Invalid email or password")
    }
    const user = this.toAuthUser(record)
    const accessToken = await this.jwtService.signAsync({
      sub: user.id,
      email: user.email,
      displayName: user.displayName,
      role: user.role,
    })
    return {
      user,
      accessToken,
      expiresAt: new Date(Date.now() + this.environment.JWT_TTL_SECONDS * 1000).toISOString(),
    }
  }

  private toAuthUser(record: typeof users.$inferSelect): AuthUser {
    return {
      id: record.id,
      email: record.email,
      displayName: record.displayName,
      role: record.role,
    }
  }
}
