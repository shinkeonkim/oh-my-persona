import type { ExecutionContext } from "@nestjs/common"

type HttpRequest = {
  readonly method: string
  readonly url: string
}

export function isContentReadRequest(method: string, url: string): boolean {
  return method === "GET" && url.startsWith("/api/content/")
}

export function skipContentReadThrottle(context: ExecutionContext): boolean {
  const request = context.switchToHttp().getRequest<HttpRequest>()
  return isContentReadRequest(request.method, request.url)
}
