import { Global, Module } from "@nestjs/common"

import { parseEnvironment } from "./env.js"

export const APP_ENVIRONMENT = Symbol("APP_ENVIRONMENT")

@Global()
@Module({
  providers: [{ provide: APP_ENVIRONMENT, useFactory: () => parseEnvironment(process.env) }],
  exports: [APP_ENVIRONMENT],
})
export class ConfigModule {}
