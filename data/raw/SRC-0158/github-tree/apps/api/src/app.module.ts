import { Module } from "@nestjs/common"
import { APP_FILTER, APP_GUARD } from "@nestjs/core"
import { ThrottlerGuard, ThrottlerModule } from "@nestjs/throttler"

import { AuthModule } from "./auth/auth.module.js"
import { JwtAuthGuard } from "./auth/jwt-auth.guard.js"
import { RolesGuard } from "./auth/roles.guard.js"
import { ConfigModule } from "./config/config.module.js"
import { ContentModule } from "./content/content.module.js"
import { DatabaseModule } from "./database/database.module.js"
import { HealthModule } from "./health/health.module.js"
import { ZodExceptionFilter } from "./http/zod-exception.filter.js"
import { MetricsModule } from "./metrics/metrics.module.js"
import { ProgressModule } from "./progress/progress.module.js"
import { QuizModule } from "./quiz/quiz.module.js"
import { skipContentReadThrottle } from "./throttle-policy.js"

@Module({
  imports: [
    ConfigModule,
    DatabaseModule,
    ThrottlerModule.forRoot({
      skipIf: skipContentReadThrottle,
      throttlers: [{ ttl: 60_000, limit: 120 }],
    }),
    AuthModule,
    ContentModule,
    ProgressModule,
    QuizModule,
    HealthModule,
    MetricsModule,
  ],
  providers: [
    { provide: APP_FILTER, useClass: ZodExceptionFilter },
    { provide: APP_GUARD, useClass: ThrottlerGuard },
    { provide: APP_GUARD, useClass: JwtAuthGuard },
    { provide: APP_GUARD, useClass: RolesGuard },
  ],
})
export class AppModule {}
