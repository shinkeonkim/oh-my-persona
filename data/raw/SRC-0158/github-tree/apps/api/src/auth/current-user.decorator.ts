import type { AuthUser } from "@aws-study/shared"
import { createParamDecorator, type ExecutionContext } from "@nestjs/common"

import type { AuthenticatedRequest } from "./auth.types.js"

export const CurrentUser = createParamDecorator(
  (_data: unknown, context: ExecutionContext): AuthUser => {
    const request = context.switchToHttp().getRequest<AuthenticatedRequest>()
    if (request.user === undefined) throw new TypeError("Authenticated request is missing its user")
    return request.user
  },
)
