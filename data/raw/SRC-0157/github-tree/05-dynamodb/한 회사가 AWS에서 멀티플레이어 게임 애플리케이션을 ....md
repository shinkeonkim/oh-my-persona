## Question

한 회사가 AWS에서 멀티플레이어 게임 애플리케이션을 호스팅합니다. 회사는 애플리케이션이 밀리초 미만의 대기 시간으로 데이터를 읽고 기록 데이터에 대해 일회성 쿼리를 실행하기를 원합니다.
최소한의 운영 오버헤드로 이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. 자주 액세스하는 데이터에는 Amazon RDS를 사용합니다. 주기적으로 사용자 지정 스크립트를 실행하여 데이터를 Amazon S3 버킷으로 내보냅니다.
- [ ] B. 데이터를 Amazon S3 버킷에 직접 저장합니다. S3 수명 주기 정책을 구현하여 오래된 데이터를 장기 저장을 위해 S3 Glacier Deep Archive로 이동합니다. Amazon Athena를 사용하여 Amazon S3의 데이터에 대해 일회성 쿼리를 실행합니다.
- [ ] C. 자주 액세스하는 데이터의 경우 DynamoDB Accelerator(DAX)와 함께 Amazon DynamoDB를 사용합니다. DynamoDB 테이블 내보내기를 사용하여 데이터를 Amazon S3 버킷으로 내보냅니다. Amazon Athena를 사용하여 Amazon S3의 데이터에 대해 일회성 쿼리를 실행합니다.
- [ ] D. 자주 액세스하는 데이터에는 Amazon DynamoDB를 사용합니다. Amazon Kinesis Data Streams로 스트리밍을 켭니다. Amazon Kinesis Data Firehose를 사용하여 Kinesis Data Streams에서 데이터를 읽습니다. 레코드를 Amazon S3 버킷에 저장합니다.

## Answer

정답: C

## Explanation

DynamoDB와 DAX(DynamoDB Accelerator)의 조합은 마이크로초 수준의 읽기 지연 시간을 제공하여 밀리초 미만 요구사항을 충족합니다. DAX는 인메모리 캐시로 자주 읽는 데이터에 대해 최대 10배 성능을 향상시킵니다. DynamoDB 테이블 내보내기(Export to S3) 기능은 테이블의 읽기 용량에 영향을 주지 않고 S3로 데이터를 내보내며, Amazon Athena를 사용하면 서버리스 SQL 쿼리로 기록 데이터에 대한 일회성 분석을 수행할 수 있습니다.

오답 분석

A: Amazon RDS는 관계형 데이터베이스로 밀리초 수준의 지연 시간을 제공하지만, DAX와 같은 마이크로초 수준의 캐시 성능을 제공하지 않습니다. 또한 사용자 지정 스크립트로 S3에 내보내는 것은 스크립트 관리, 오류 처리 등의 운영 오버헤드가 높습니다.

B: S3에 직접 데이터를 저장하면 밀리초 미만의 읽기 지연 시간을 제공할 수 없습니다. S3는 객체 스토리지로 GET 요청의 지연 시간이 수십~수백 밀리초이며, 실시간 게임 데이터 읽기에는 적합하지 않습니다.

D: Kinesis Data Streams + Kinesis Data Firehose 파이프라인은 실시간 스트리밍 데이터 처리에는 강력하지만, DynamoDB의 기본 내보내기 기능보다 아키텍처가 복잡하고 운영 오버헤드가 높습니다. 또한 Kinesis 서비스에 대한 추가 비용이 발생합니다.

