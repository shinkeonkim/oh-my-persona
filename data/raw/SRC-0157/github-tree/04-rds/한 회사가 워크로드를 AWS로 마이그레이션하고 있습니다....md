## Question

한 회사가 워크로드를 AWS로 마이그레이션하고 있습니다. 회사는 SQL Server 인스턴스에서 실행되는 온프레미스 관계형 데이터베이스에 민감하고 중요한 데이터를 보유하고 있습니다.
회사는 AWS 클라우드를 사용하여 보안을 강화하고 데이터베이스의 운영 오버헤드를 줄이고 싶어합니다.
이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. 데이터베이스를 Amazon EC2 인스턴스로 마이그레이션합니다. 암호화를 위해 AWS Key Management Service(AWS KMS) AWS 관리형 키를 사용합니다.
- [ ] B. 데이터베이스를 다중 AZ Amazon RDS for SQL Server DB 인스턴스로 마이그레이션합니다. 암호화를 위해 AWS Key Management Service(AWS KMS) AWS 관리형 키를 사용합니다.
- [ ] C. 데이터를 Amazon S3 버킷으로 마이그레이션합니다. Amazon Macie를 사용하여 데이터 보안을 보장합니다.
- [ ] D. 데이터베이스를 Amazon DynamoDB 테이블로 마이그레이션합니다. Amazon CloudWatch Logs를 사용하여 데이터 보안을 보장합니다.

## Answer

정답: B

## Explanation

Amazon RDS for SQL Server의 Multi-AZ 배포에 AWS KMS 관리형 키를 사용한 암호화를 적용하면, 보안과 운영 오버헤드 감소를 모두 달성할 수 있습니다. RDS는 완전 관리형 서비스로 패치, 백업, 장애 조치를 자동으로 처리하여 운영 오버헤드를 줄이며, Multi-AZ는 고가용성을 제공합니다. KMS를 통한 암호화는 저장 데이터(data at rest)를 보호하여 민감한 데이터의 보안을 강화합니다.

오답 분석

A: Amazon EC2에 데이터베이스를 마이그레이션하면 OS 패치, 백업, 복제 등을 직접 관리해야 하므로 운영 오버헤드가 줄어들지 않습니다.

C: 관계형 데이터베이스를 S3로 마이그레이션하는 것은 적절하지 않습니다. Amazon Macie는 S3의 민감한 데이터를 검색하는 서비스이지 데이터베이스 보안 솔루션이 아닙니다.

D: CloudWatch Logs는 로그 모니터링 서비스이며, 데이터 보안 및 보호를 제공하지 않습니다. DynamoDB로의 마이그레이션은 SQL Server에서의 스키마 변환이 필요합니다.

