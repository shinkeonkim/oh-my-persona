import {
  type ArgumentsHost,
  Catch,
  type ExceptionFilter,
  HttpStatus,
  Inject,
  Injectable,
} from "@nestjs/common"
import { HttpAdapterHost } from "@nestjs/core"
import { ZodError } from "zod"

@Catch(ZodError)
@Injectable()
export class ZodExceptionFilter implements ExceptionFilter<ZodError> {
  constructor(@Inject(HttpAdapterHost) private readonly httpAdapterHost: HttpAdapterHost) {}

  catch(exception: ZodError, host: ArgumentsHost): void {
    const { httpAdapter } = this.httpAdapterHost
    const context = host.switchToHttp()
    httpAdapter.reply(
      context.getResponse(),
      {
        statusCode: HttpStatus.BAD_REQUEST,
        error: "Bad Request",
        message: exception.issues.map((issue) => issue.message),
      },
      HttpStatus.BAD_REQUEST,
    )
  }
}
