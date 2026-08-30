import { z } from "zod"

export const certificationCodeSchema = z.enum(["aif", "clf", "saa"])
export const contentAccessSchema = z.enum(["public", "protected"])

export const certificationSchema = z.object({
  code: certificationCodeSchema,
  examCode: z.string().min(1),
  title: z.string().min(1),
  shortTitle: z.string().min(1),
  description: z.string().min(1),
})

export type CertificationCode = z.infer<typeof certificationCodeSchema>
export type ContentAccess = z.infer<typeof contentAccessSchema>
export type Certification = z.infer<typeof certificationSchema>

export const CERTIFICATIONS = [
  {
    code: "aif",
    examCode: "AIF-C01",
    title: "AWS Certified AI Practitioner",
    shortTitle: "AI Practitioner",
    description: "AI/ML 기초부터 Bedrock, SageMaker, 책임 있는 AI까지 학습합니다.",
  },
  {
    code: "clf",
    examCode: "CLF-C02",
    title: "AWS Certified Cloud Practitioner",
    shortTitle: "Cloud Practitioner",
    description: "클라우드 개념, 핵심 서비스, 보안, 비용 관리의 기반을 다집니다.",
  },
  {
    code: "saa",
    examCode: "SAA-C03",
    title: "AWS Certified Solutions Architect - Associate",
    shortTitle: "Solutions Architect",
    description: "가용성, 보안, 성능, 비용을 아우르는 아키텍처 패턴을 학습합니다.",
  },
] as const satisfies readonly Certification[]

export function findCertification(code: CertificationCode): Certification {
  const certification = CERTIFICATIONS.find((candidate) => candidate.code === code)
  if (certification === undefined) {
    throw new RangeError(`Unknown certification code: ${code}`)
  }
  return certification
}
