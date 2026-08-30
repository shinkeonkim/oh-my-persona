import type { CertificationCode } from "../../certifications"
import type { ExamDomainCode } from "./types"

/**
 * Explicit, reviewed mapping from AWS service category to official exam domain code.
 * Key: `${certCode}:${serviceCategory}` → exam domain code (D1, D2, ...).
 * Every entry is manually reviewed — no keyword inference.
 */
const CATEGORY_DOMAIN_MAP: Readonly<Record<string, ExamDomainCode>> = {
  // --- AIF-C01 (D1-D5) ---
  "aif:analytics": "D1",
  "aif:cloud-financial-mgmt": "D5",
  "aif:compute": "D1",
  "aif:containers": "D1",
  "aif:database": "D1",
  "aif:developer-tools": "D3",
  "aif:machine-learning": "D3",
  "aif:mgmt-governance": "D5",
  "aif:networking-cdn": "D1",
  "aif:security": "D5",
  "aif:storage": "D1",
  "aif:objective-only": "D3",
  // --- CLF-C02 (D1-D4) ---
  "clf:analytics": "D3",
  "clf:app-integration": "D3",
  "clf:business-apps": "D3",
  "clf:cloud-financial-mgmt": "D4",
  "clf:compute": "D3",
  "clf:containers": "D3",
  "clf:customer-enablement": "D4",
  "clf:database": "D3",
  "clf:developer-tools": "D3",
  "clf:end-user-computing": "D3",
  "clf:frontend-web-mobile": "D3",
  "clf:iot": "D3",
  "clf:machine-learning": "D3",
  "clf:mgmt-governance": "D3",
  "clf:migration-transfer": "D3",
  "clf:networking-cdn": "D3",
  "clf:security": "D2",
  "clf:serverless": "D3",
  "clf:storage": "D3",
  // --- SAA-C03 (D1-D4) ---
  "saa:analytics": "D3",
  "saa:app-integration": "D3",
  "saa:cost-management": "D4",
  "saa:compute": "D2",
  "saa:containers": "D2",
  "saa:database": "D2",
  "saa:developer-tools": "D3",
  "saa:frontend-web-mobile": "D3",
  "saa:machine-learning": "D3",
  "saa:mgmt-governance": "D3",
  "saa:media-services": "D3",
  "saa:migration-transfer": "D2",
  "saa:networking-cdn": "D2",
  "saa:security": "D1",
  "saa:serverless": "D3",
  "saa:storage": "D2",
}

export class CatalogDomainMappingError extends Error {
  readonly certificationCode: CertificationCode
  readonly serviceCategory: string

  constructor(certificationCode: CertificationCode, serviceCategory: string) {
    super(`Missing exam-domain mapping for ${certificationCode}:${serviceCategory}`)
    this.name = "CatalogDomainMappingError"
    this.certificationCode = certificationCode
    this.serviceCategory = serviceCategory
  }
}

/** Resolve a service category to an official exam domain code. Returns undefined if unmapped. */
export function resolveExamDomain(
  certCode: CertificationCode,
  serviceCategory: string,
): ExamDomainCode | undefined {
  return CATEGORY_DOMAIN_MAP[`${certCode}:${serviceCategory}`]
}

export function resolveRequiredExamDomain(
  certCode: CertificationCode,
  serviceCategory: string,
): ExamDomainCode {
  const domainCode = resolveExamDomain(certCode, serviceCategory)
  if (domainCode === undefined) {
    throw new CatalogDomainMappingError(certCode, serviceCategory)
  }
  return domainCode
}

/** Get all valid category keys for a cert. */
export function validCategoriesForCert(certCode: CertificationCode): readonly string[] {
  const prefix = `${certCode}:`
  return Object.keys(CATEGORY_DOMAIN_MAP)
    .filter((k) => k.startsWith(prefix))
    .map((k) => k.slice(prefix.length))
}
