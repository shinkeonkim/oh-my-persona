import { createDatabase, type Database } from "@aws-study/db"
import { Global, Inject, Module, type Provider } from "@nestjs/common"

import { APP_ENVIRONMENT } from "../config/config.module.js"
import type { AppEnvironment } from "../config/env.js"

export const DATABASE = Symbol("DATABASE")

const databaseProvider: Provider = {
  provide: DATABASE,
  inject: [APP_ENVIRONMENT],
  useFactory: (environment: AppEnvironment): Database => createDatabase(environment.DATABASE_URL),
}

@Global()
@Module({ providers: [databaseProvider], exports: [DATABASE] })
export class DatabaseModule {}

export const InjectDatabase = (): ParameterDecorator => Inject(DATABASE)
