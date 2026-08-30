import "reflect-metadata"

import { Logger } from "@nestjs/common"
import { NestFactory } from "@nestjs/core"
import { FastifyAdapter, type NestFastifyApplication } from "@nestjs/platform-fastify"
import { DocumentBuilder, SwaggerModule } from "@nestjs/swagger"

import { AppModule } from "./app.module.js"
import { parseEnvironment } from "./config/env.js"

async function bootstrap(): Promise<void> {
  const environment = parseEnvironment(process.env)
  const app = await NestFactory.create<NestFastifyApplication>(
    AppModule,
    new FastifyAdapter({
      logger:
        environment.NODE_ENV === "development" ? { transport: { target: "pino-pretty" } } : true,
    }),
  )

  app.enableCors({
    origin: environment.WEB_ORIGIN,
    credentials: true,
    methods: ["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
  })
  app.setGlobalPrefix("api", { exclude: ["healthz", "readyz"] })

  const swaggerConfig = new DocumentBuilder()
    .setTitle("AWS Study API")
    .setDescription("Authenticated AWS certification study content and progress API")
    .setVersion("0.1.0")
    .addBearerAuth()
    .build()
  SwaggerModule.setup("api/docs", app, SwaggerModule.createDocument(app, swaggerConfig))

  await app.listen(environment.PORT, "0.0.0.0")
  Logger.log(`API listening on port ${environment.PORT}`, "Bootstrap")
}

await bootstrap()
