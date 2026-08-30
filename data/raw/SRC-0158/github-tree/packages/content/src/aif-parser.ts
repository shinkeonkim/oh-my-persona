import { type Question, questionSchema } from "@aws-study/shared"
import { z } from "zod"

const aifOptionSchema = z.object({
  key: z.string(),
  kr: z.string().min(1),
})

const aifQuestionSchema = z.object({
  id: z.string().min(1),
  domain: z.number().int().min(1).max(5),
  question_kr: z.string().min(1),
  options: z.array(aifOptionSchema).min(2),
  answer: z.array(z.string()).min(1),
  explanation_kr: z.string().min(1),
})

const aifBankSchema = z.object({ questions: z.array(aifQuestionSchema) })

export function parseAifQuestionBank(json: string): readonly Question[] {
  const bank = aifBankSchema.parse(JSON.parse(json))
  return bank.questions.map((question) =>
    questionSchema.parse({
      sourceId: `aif:${question.id}`,
      certificationCode: "aif",
      categorySlug: `domain-${question.domain}`,
      prompt: question.question_kr,
      options: question.options.map((option) => ({ key: option.key, text: option.kr })),
      answers: question.answer,
      explanation: question.explanation_kr,
      access: "protected",
    }),
  )
}
