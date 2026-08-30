import { Module } from "@nestjs/common"
import { JwtModule } from "@nestjs/jwt"

import { APP_ENVIRONMENT } from "../config/config.module.js"
import type { AppEnvironment } from "../config/env.js"
import { AdminController } from "./admin.controller.js"
import { AuthController } from "./auth.controller.js"
import { AuthService } from "./auth.service.js"

@Module({
  imports: [
    JwtModule.registerAsync({
      inject: [APP_ENVIRONMENT],
      useFactory: (environment: AppEnvironment) => ({
        secret: environment.JWT_SECRET,
        signOptions: { expiresIn: environment.JWT_TTL_SECONDS },
      }),
    }),
  ],
  controllers: [AuthController, AdminController],
  providers: [AuthService],
  exports: [JwtModule],
})
export class AuthModule {}
