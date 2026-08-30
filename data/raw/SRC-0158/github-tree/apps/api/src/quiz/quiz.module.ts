import { Module } from "@nestjs/common"

import { QuizController } from "./quiz.controller.js"
import { QuizLobbyService } from "./quiz-lobby.service.js"
import { QuizProgressService } from "./quiz-progress.service.js"
import { QuizSessionService } from "./quiz-session.service.js"
import { QuizStateService } from "./quiz-state.service.js"

@Module({
  controllers: [QuizController],
  providers: [QuizLobbyService, QuizProgressService, QuizSessionService, QuizStateService],
})
export class QuizModule {}
