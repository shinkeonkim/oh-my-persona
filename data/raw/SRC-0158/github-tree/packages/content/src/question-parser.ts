import {
  type CertificationCode,
  type ContentAccess,
  type Question,
  questionSchema,
} from "@aws-study/shared"

export type QuestionParseInput = {
  readonly sourceId: string
  readonly certificationCode: CertificationCode
  readonly categorySlug: string
  readonly markdown: string
  readonly access: ContentAccess
}

function section(markdown: string, name: string, nextName?: string): string {
  const end = nextName === undefined ? "$" : `(?=\\n##\\s+${nextName})`
  const expression = new RegExp(`##\\s+${name}\\s*\\n([\\s\\S]*?)${end}`, "i")
  return markdown.match(expression)?.[1]?.trim() ?? ""
}

export function parseQuestion(input: QuestionParseInput): Question {
  const promptSection = section(input.markdown, "Question", "Answer")
  const answerSection = section(input.markdown, "Answer", "Explanation")
  const explanation = section(input.markdown, "Explanation")
  const optionExpression = /^- \[ \] ([A-E])\.\s+(.+)$/gm
  const options = Array.from(promptSection.matchAll(optionExpression), (match) => ({
    key: match[1] ?? "",
    text: match[2]?.trim() ?? "",
  }))
  const prompt = promptSection.replace(optionExpression, "").trim()
  const answers = (answerSection.match(/정답:\s*([A-E](?:\s*,\s*[A-E])*)/i)?.[1] ?? "")
    .split(",")
    .map((answer) => answer.trim())
    .filter((answer) => answer !== "")

  return questionSchema.parse({ ...input, prompt, options, answers, explanation })
}
