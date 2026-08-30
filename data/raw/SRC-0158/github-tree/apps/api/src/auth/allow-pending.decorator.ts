import { SetMetadata } from "@nestjs/common"

export const ALLOW_PENDING_ROUTE = "allow-pending-route"
export const AllowPending = (): MethodDecorator & ClassDecorator =>
  SetMetadata(ALLOW_PENDING_ROUTE, true)
