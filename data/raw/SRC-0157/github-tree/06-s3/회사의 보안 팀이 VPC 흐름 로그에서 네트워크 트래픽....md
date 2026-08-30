## Question

회사의 보안 팀이 VPC 흐름 로그에서 네트워크 트래픽을 캡처하도록 요청합니다. 로그는 90일 동안 자주 액세스한 후 간헐적으로 액세스합니다.
솔루션 설계자는 로그를 구성할 때 이러한 요구 사항을 충족하기 위해 무엇을 해야 합니까?

- [ ] A. Amazon CloudWatch를 대상으로 사용합니다. CloudWatch 로그 그룹을 90일 만료로 설정합니다.
- [ ] B. Amazon Kinesis를 대상으로 사용합니다. 항상 90일 동안 로그를 유지하도록 Kinesis 스트림을 구성합니다.
- [ ] C. AWS CloudTrail을 대상으로 사용합니다. Amazon S3 버킷에 저장하도록 CloudTrail을 구성하고 S3 Intelligent-Tiering을 활성화합니다.
- [ ] D. Amazon S3를 대상으로 사용합니다. S3 수명 주기 정책을 활성화하여 90일 후에 로그를 S3 Standard-Infrequent Access(S3 Standard-IA)로 전환합니다.

## Answer

정답: D

## Explanation

VPC 흐름 로그를 Amazon S3에 직접 저장하는 것은 AWS가 공식적으로 지원하는 대상 옵션입니다. S3 수명 주기 정책을 활성화하여 90일 후 S3 Standard-IA로 전환하면, 처음 90일간 자주 액세스하는 동안에는 S3 Standard의 높은 성능을 활용하고, 이후 간헐적 액세스 기간에는 S3 Standard-IA의 저렴한 스토리지 비용으로 비용을 최적화할 수 있습니다. S3 Standard-IA는 밀리초 단위의 즉시 접근이 가능하여 필요 시 언제든 로그를 조회할 수 있습니다.

오답 분석

A: CloudWatch를 대상으로 사용하고 90일 만료(retention)를 설정하면 90일 후 로그가 완전히 삭제되므로, 90일 이후에도 간헐적으로 액세스해야 하는 요구 사항을 충족하지 못합니다.

B: Amazon Kinesis Data Streams는 VPC 흐름 로그의 직접 대상으로 지원되지 않습니다. 지원되는 대상은 CloudWatch Logs, S3, Kinesis Data Firehose입니다. 또한 90일간 스트림 보존은 최대 365일까지 가능하지만 비용이 매우 높습니다.

C: AWS CloudTrail은 AWS API 호출을 기록하는 서비스이며, VPC 흐름 로그의 대상으로 사용할 수 없습니다. VPC 흐름 로그와 CloudTrail은 완전히 다른 서비스입니다.

