## Question

한 회사에서 REST API로 검색할 주문 배송 통계를 제공하는 애플리케이션을 개발하고 있습니다. 회사는 배송 통계를 추출하고 데이터를 읽기 쉬운 HTML 형식으로 구성하고 매일 아침 동시에 여러 이메일 주소로 보고서를 보내려고 합니다.
이러한 요구 사항을 충족하기 위해 솔루션 설계자는 어떤 단계 조합을 수행해야 합니까? (두 가지를 선택하세요.)

- [ ] A. 데이터를 Amazon Kinesis Data Firehose로 보내도록 애플리케이션을 구성합니다.
- [ ] B. Amazon Simple Email Service(Amazon SES)를 사용하여 데이터 형식을 지정하고 이메일로 보고서를 보냅니다.
- [ ] C. 데이터에 대한 애플리케이션의 API를 쿼리하기 위해 AWS Glue 작업을 호출하는 Amazon EventBridge(Amazon CloudWatch Events) 예약 이벤트를 생성합니다.
- [ ] D. 데이터에 대한 애플리케이션의 API를 쿼리하기 위해 AWS Lambda 함수를 호출하는 Amazon EventBridge(Amazon CloudWatch Events) 예약 이벤트를 생성합니다.
- [ ] E. 애플리케이션 데이터를 Amazon S3에 저장합니다. 보고서를 이메일로 보낼 S3 이벤트 대상으로 Amazon Simple Notification Service(Amazon SNS) 주제를 생성합니다.

## Answer

정답: B, D

## Explanation

Amazon EventBridge 예약 이벤트로 매일 아침 AWS Lambda 함수를 트리거하여 REST API에서 배송 통계를 수집하고(D), Amazon SES로 HTML 형식의 이메일 보고서를 여러 수신자에게 동시 발송합니다(B). Lambda는 API 쿼리, 데이터 가공, HTML 포맷팅을 모두 처리할 수 있으며, SES는 대량 이메일 전송에 최적화된 서비스로 HTML 콘텐츠를 지원합니다. 이 조합은 완전 서버리스로 운영 부담이 없고 정기 스케줄링 요구사항을 정확히 충족합니다.

오답 분석

A: Amazon Kinesis Data Firehose는 실시간 스트리밍 데이터를 S3, Redshift 등 대상으로 전달하는 서비스입니다. REST API 쿼리나 이메일 보고서 생성과는 무관하며, 매일 정기 보고서 생성 패턴에 적합하지 않습니다.

C: AWS Glue는 대규모 ETL(Extract, Transform, Load) 작업용 서비스로, 단순한 REST API 쿼리에는 과도합니다. Glue job은 시작 시간이 길고(수 분) 비용이 높아 간단한 데이터 수집 작업에 비효율적입니다.

E: S3 이벤트 알림은 객체 생성/삭제 등 S3 버킷 이벤트에 의해 트리거됩니다. 매일 아침 같은 시간에 실행되는 정기 스케줄링 요구사항에는 부적합하며, SNS는 이메일 전송 시 HTML 형식을 지원하지 않습니다.

