## Question

보고 팀은 매일 Amazon S3 버킷에서 파일을 받습니다. 보고 팀은 Amazon QuickSight에서 사용하기 위해 매일 동시에 이 초기 S3 버킷에서 분석 S3 버킷으로 파일을 수동으로 검토하고 복사합니다. 더 많은 팀이 더 큰 크기의 더 많은 파일을 초기 S3 버킷으로 보내기 시작했습니다. 보고 팀은 파일이 초기 S3 버킷에 들어갈 때 자동으로 파일을 분석 S3 버킷으로 이동하려고 합니다. 보고 팀은 또한 AWS Lambda 함수를 사용하여 복사된 데이터에서 패턴 일치 코드를 실행하려고 합니다. 또한 보고 팀은 데이터 파일을 Amazon SageMaker Pipelines의 파이프라인으로 보내려고 합니다.
최소한의 운영 오버헤드로 이러한 요구 사항을 충족하려면 솔루션 설계자가 무엇을 해야 합니까?

- [ ] A. 분석 S3 버킷에 파일을 복사하는 Lambda 함수를 생성합니다. 분석 S3 버킷에 대한 S3 이벤트 알림을 생성합니다. 이벤트 알림의 대상으로 Lambda 및 SageMaker 파이프라인을 구성합니다. s3:ObjectCreated:Put을 이벤트 유형으로 구성합니다.
- [ ] B. 분석 S3 버킷에 파일을 복사하는 Lambda 함수를 생성합니다. Amazon EventBridge(Amazon CloudWatch Events)에 이벤트 알림을 보내도록 분석 S3 버킷을 구성합니다. EventBridge(CloudWatch 이벤트)에서 ObjectCreated 규칙을 구성합니다. Lambda 및 SageMaker 파이프라인을 규칙의 대상으로 구성합니다.
- [ ] C. S3 버킷 간에 S3 복제를 구성합니다. 분석 S3 버킷에 대한 S3 이벤트 알림을 생성합니다. 이벤트 알림의 대상으로 Lambda 및 SageMaker 파이프라인을 구성합니다. s3:ObjectCreated:Put을 이벤트 유형으로 구성합니다.
- [ ] D. S3 버킷 간에 S3 복제를 구성합니다. Amazon EventBridge(Amazon CloudWatch Events)에 이벤트 알림을 보내도록 분석 S3 버킷을 구성합니다. EventBridge(CloudWatch 이벤트)에서 ObjectCreated 규칙을 구성합니다. Lambda 및 SageMaker 파이프라인을 규칙의 대상으로 구성합니다.

## Answer

정답: D

## Explanation

S3 복제를 사용하면 초기 버킷에 파일이 도착할 때 자동으로 분석 버킷에 복사되어 수동 작업이 필요 없습니다. Amazon EventBridge를 사용하면 단일 이벤트에서 Lambda와 SageMaker Pipelines 등 여러 대상으로 이벤트를 전달할 수 있습니다. S3 이벤트 알림은 직접적으로 SageMaker Pipelines를 대상으로 지원하지 않지만, EventBridge는 다양한 AWS 서비스를 대상으로 설정할 수 있어 운영 오버헤드가 최소화됩니다.

오답 분석

A: Lambda로 파일을 복사하는 것은 가능하지만, S3 이벤트 알림은 SageMaker Pipelines를 직접 대상으로 지원하지 않습니다.

B: Lambda로 파일 복사와 EventBridge 사용은 적절하지만, S3 복제가 파일 복사에 더 효율적이며 운영 오버헤드가 적습니다.

C: S3 복제는 적절하지만, S3 이벤트 알림은 Lambda와 SageMaker Pipelines를 동시에 대상으로 지원하는 데 제한이 있습니다.

