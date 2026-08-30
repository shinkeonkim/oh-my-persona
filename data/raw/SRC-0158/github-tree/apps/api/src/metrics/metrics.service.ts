import { Injectable } from "@nestjs/common"
import { collectDefaultMetrics, Registry } from "prom-client"

@Injectable()
export class MetricsService {
  private readonly registry = new Registry()

  constructor() {
    collectDefaultMetrics({ register: this.registry, prefix: "aws_study_" })
  }

  contentType(): string {
    return this.registry.contentType
  }

  metrics(): Promise<string> {
    return this.registry.metrics()
  }
}
