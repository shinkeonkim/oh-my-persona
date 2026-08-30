import {
  type AuthUser,
  certificationCodeSchema,
  quizAttemptInputSchema,
  quizSessionConfigSchema,
  quizSessionIdSchema,
  quizSessionStartInputSchema,
} from "@aws-study/shared"
import {
  Body,
  Controller,
  Delete,
  Get,
  HttpCode,
  HttpStatus,
  Inject,
  Param,
  Post,
  Put,
} from "@nestjs/common"

import { CurrentUser } from "../auth/current-user.decorator.js"
import { Roles } from "../auth/roles.decorator.js"
import { QuizLobbyService } from "./quiz-lobby.service.js"
import { QuizProgressService } from "./quiz-progress.service.js"
import { QuizSessionService } from "./quiz-session.service.js"
import { QuizStateService } from "./quiz-state.service.js"

@Roles("reader", "admin")
@Controller("quiz")
export class QuizController {
  constructor(
    @Inject(QuizLobbyService) private readonly lobbyService: QuizLobbyService,
    @Inject(QuizProgressService) private readonly progressService: QuizProgressService,
    @Inject(QuizSessionService) private readonly sessionService: QuizSessionService,
    @Inject(QuizStateService) private readonly stateService: QuizStateService,
  ) {}

  @Get("lobby/:code")
  lobby(@CurrentUser() user: AuthUser, @Param("code") code: string) {
    return this.lobbyService.get(user.id, certificationCodeSchema.parse(code))
  }

  @Post("sessions")
  start(@CurrentUser() user: AuthUser, @Body() body: unknown) {
    return this.sessionService.start(user.id, quizSessionStartInputSchema.parse(body))
  }

  @Put("preferences")
  @HttpCode(HttpStatus.NO_CONTENT)
  preference(@CurrentUser() user: AuthUser, @Body() body: unknown): Promise<void> {
    return this.progressService.savePreference(user.id, quizSessionConfigSchema.parse(body))
  }

  @Get("wrong-notes/:code")
  wrongNotes(@CurrentUser() user: AuthUser, @Param("code") code: string) {
    return this.progressService.wrongNotes(user.id, certificationCodeSchema.parse(code))
  }

  @Delete("progress/:code")
  @HttpCode(HttpStatus.NO_CONTENT)
  reset(@CurrentUser() user: AuthUser, @Param("code") code: string): Promise<void> {
    return this.progressService.reset(user.id, certificationCodeSchema.parse(code))
  }

  @Get("sessions/:id")
  state(@CurrentUser() user: AuthUser, @Param("id") id: string) {
    return this.stateService.get(user.id, quizSessionIdSchema.parse(id))
  }

  @Post("attempts")
  attempt(@CurrentUser() user: AuthUser, @Body() body: unknown) {
    return this.sessionService.attempt(user.id, quizAttemptInputSchema.parse(body))
  }

  @Post("sessions/:id/abandon")
  @HttpCode(HttpStatus.NO_CONTENT)
  abandon(@CurrentUser() user: AuthUser, @Param("id") id: string): Promise<void> {
    return this.sessionService.abandon(user.id, quizSessionIdSchema.parse(id))
  }
}
