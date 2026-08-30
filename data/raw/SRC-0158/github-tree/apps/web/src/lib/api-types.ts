import { categorySchema, studyNoteSchema } from "@aws-study/shared"
import { z } from "zod"

export {
  type AnswerResult as AnswerResponse,
  answerResultSchema as answerResponseSchema,
  type QuizAttemptResult,
  type QuizLobbyResponse,
  type QuizQuestion,
  type QuizResponse,
  type QuizSessionConfig,
  type QuizSessionState,
  type QuizWrongNote,
  quizAttemptResultSchema,
  quizLobbyResponseSchema,
  quizQuestionSchema,
  quizResponseSchema,
  quizSessionStateSchema,
  quizWrongNotesSchema,
} from "@aws-study/shared"

export const categoriesResponseSchema = z.array(categorySchema)
export const studyNoteResponseSchema = studyNoteSchema
export const progressResponseSchema = z.array(
  z.object({
    certificationCode: z.enum(["aif", "clf", "saa"]),
    attempted: z.number().int().nonnegative(),
    correct: z.number().int().nonnegative(),
  }),
)
