import type { CertDomain } from "../resource-curriculum"

/** AIF-C01 exam domains with official weights (v1.1). */
export const AIF_DOMAINS: readonly CertDomain[] = [
  {
    certificationCode: "aif",
    domainCode: "D1",
    domainTitle: "Fundamentals of AI and ML",
    weight: 20,
  },
  {
    certificationCode: "aif",
    domainCode: "D2",
    domainTitle: "Fundamentals of Generative AI",
    weight: 24,
  },
  {
    certificationCode: "aif",
    domainCode: "D3",
    domainTitle: "Applications of Foundation Models",
    weight: 28,
  },
  {
    certificationCode: "aif",
    domainCode: "D4",
    domainTitle: "Guidelines for Responsible AI",
    weight: 14,
  },
  {
    certificationCode: "aif",
    domainCode: "D5",
    domainTitle: "Security, Compliance, and Governance for AI Solutions",
    weight: 14,
  },
]

/** CLF-C02 exam domains with official weights. */
export const CLF_DOMAINS: readonly CertDomain[] = [
  { certificationCode: "clf", domainCode: "D1", domainTitle: "Cloud Concepts", weight: 24 },
  {
    certificationCode: "clf",
    domainCode: "D2",
    domainTitle: "Security and Compliance",
    weight: 30,
  },
  {
    certificationCode: "clf",
    domainCode: "D3",
    domainTitle: "Cloud Technology and Services",
    weight: 34,
  },
  {
    certificationCode: "clf",
    domainCode: "D4",
    domainTitle: "Billing, Pricing, and Support",
    weight: 12,
  },
]

/** SAA-C03 exam domains with official weights. */
export const SAA_DOMAINS: readonly CertDomain[] = [
  {
    certificationCode: "saa",
    domainCode: "D1",
    domainTitle: "Design Secure Architectures",
    weight: 30,
  },
  {
    certificationCode: "saa",
    domainCode: "D2",
    domainTitle: "Design Resilient Architectures",
    weight: 26,
  },
  {
    certificationCode: "saa",
    domainCode: "D3",
    domainTitle: "Design High-Performing Architectures",
    weight: 24,
  },
  {
    certificationCode: "saa",
    domainCode: "D4",
    domainTitle: "Design Cost-Optimized Architectures",
    weight: 20,
  },
]

/** All cert domains combined. */
export const ALL_CERT_DOMAINS: readonly CertDomain[] = [
  ...AIF_DOMAINS,
  ...CLF_DOMAINS,
  ...SAA_DOMAINS,
]
