import {
  answerInputSchema,
  certificationCodeSchema,
  questionIdSchema,
  quizQuerySchema,
} from "@aws-study/shared"
import { Body, Controller, Get, Inject, Param, Post, Query } from "@nestjs/common"

import { Public } from "../auth/public.decorator.js"
import { Roles } from "../auth/roles.decorator.js"
import { ContentService } from "./content.service.js"

@Controller("content")
export class ContentController {
  constructor(@Inject(ContentService) private readonly contentService: ContentService) {}

  @Public()
  @Get("certifications")
  certifications() {
    return this.contentService.certifications()
  }

  @Public()
  @Get("categories/:code")
  categories(@Param("code") rawCode: string) {
    return this.contentService.listCategories(certificationCodeSchema.parse(rawCode))
  }

  @Public()
  @Get("notes/:code/:slug")
  note(@Param("code") rawCode: string, @Param("slug") slug: string) {
    return this.contentService.note(certificationCodeSchema.parse(rawCode), slug)
  }

  @Roles("reader", "admin")
  @Get("quiz/:code")
  quiz(@Param("code") rawCode: string, @Query() query: unknown) {
    const { page, pageSize, category } = quizQuerySchema.parse(query)
    return this.contentService.quiz(
      certificationCodeSchema.parse(rawCode),
      page,
      pageSize,
      category,
    )
  }

  @Roles("reader", "admin")
  @Post("questions/:id/answer")
  answer(@Param("id") rawId: string, @Body() body: unknown) {
    return this.contentService.answer(
      questionIdSchema.parse(rawId),
      answerInputSchema.parse(body).selectedAnswers,
    )
  }
}
