import type { UserRole } from "@aws-study/shared"
import {
  type CanActivate,
  type ExecutionContext,
  ForbiddenException,
  Inject,
  Injectable,
} from "@nestjs/common"
import { Reflector } from "@nestjs/core"

import type { AuthenticatedRequest } from "./auth.types.js"
import { REQUIRED_ROLES } from "./roles.decorator.js"

@Injectable()
export class RolesGuard implements CanActivate {
  constructor(@Inject(Reflector) private readonly reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const roles = this.reflector.getAllAndOverride<readonly UserRole[]>(REQUIRED_ROLES, [
      context.getHandler(),
      context.getClass(),
    ])
    if (roles === undefined) return true
    const request = context.switchToHttp().getRequest<AuthenticatedRequest>()
    if (request.user === undefined || !roles.includes(request.user.role)) {
      throw new ForbiddenException("Insufficient permissions")
    }
    return true
  }
}
