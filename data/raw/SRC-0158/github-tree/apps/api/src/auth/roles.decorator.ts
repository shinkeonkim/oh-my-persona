import type { UserRole } from "@aws-study/shared"
import { SetMetadata } from "@nestjs/common"

export const REQUIRED_ROLES = "required-roles"
export const Roles = (...roles: readonly UserRole[]): MethodDecorator & ClassDecorator =>
  SetMetadata(REQUIRED_ROLES, roles)
