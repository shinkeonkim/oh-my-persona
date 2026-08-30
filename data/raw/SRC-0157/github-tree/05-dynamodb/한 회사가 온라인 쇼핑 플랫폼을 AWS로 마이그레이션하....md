## Question

한 회사가 온라인 쇼핑 플랫폼을 AWS로 마이그레이션하면서 서버리스 아키텍처를 도입하려고 합니다. 이 플랫폼에는 정의된 스키마가 없는 사용자 프로필 및 기본 설정 서비스가 있습니다. 이 플랫폼은 사용자 정의 필드를 허용합니다. 프로필 정보는 매일 여러 번 업데이트됩니다. 회사는 프로필 정보를 내구성 있고 가용성이 높은 솔루션에 저장해야 합니다. 솔루션은 향후 처리를 위해 프로필 데이터의 수정 사항을 캡처해야 합니다.
어떤 솔루션이 이러한 요구 사항을 충족합니까?

- [ ] A. Amazon RDS for PostgreSQL 인스턴스를 사용하여 프로필 데이터를 저장합니다. Amazon CloudWatch Logs의 로그 스트림을 사용하여 수정 사항을 캡처합니다.
- [ ] B. Amazon DynamoDB 테이블을 사용하여 프로필 데이터를 저장합니다. Amazon DynamoDB Streams를 사용하여 수정 사항을 캡처합니다.
- [ ] C. Amazon ElastiCache(Redis OSS) 클러스터를 사용하여 프로필 데이터를 저장합니다. Amazon Kinesis Data Firehose를 사용하여 수정 사항을 캡처합니다.
- [ ] D. Amazon Aurora Serverless v2 클러스터를 사용하여 프로필 데이터를 저장합니다. Amazon CloudWatch Logs의 로그 스트림을 사용하여 수정 사항을 캡처합니다.

## Answer

정답: B

## Explanation

Amazon DynamoDB는 스키마리스(Schemaless) NoSQL 데이터베이스로, 정의된 스키마 없이 사용자 정의 필드를 유연하게 추가할 수 있습니다. 서버리스 아키텍처이므로 서버 관리가 불필요하며, 내장된 내구성(3개 AZ 복제)과 고가용성을 제공합니다. DynamoDB Streams는 프로필 데이터 수정을 실시간으로 캡처하여 후속 처리 파이프라인에 전달합니다.

오답 분석

A: Amazon RDS for PostgreSQL은 관계형 데이터베이스로 사전 정의된 스키마가 필요합니다. 사용자 정의 필드를 유연하게 추가하기 어렵고, 서버리스 요구사항에도 부합하지 않습니다.

C: Amazon ElastiCache(Redis OSS)는 인메모리 캐시로 주요 데이터베이스가 아닌 보조 캐시 용도입니다. 영구 저장소로서의 내구성이 DynamoDB보다 낮으며, Kinesis Firehose는 데이터 변경 캡처에 적합하지 않습니다.

D: Amazon Aurora Serverless v2는 서버리스이지만 관계형 데이터베이스이므로 스키마가 필요합니다. CloudWatch Logs는 애플리케이션 로그를 저장하는 서비스이며 데이터베이스 레코드 변경 캡처에 적합하지 않습니다.

