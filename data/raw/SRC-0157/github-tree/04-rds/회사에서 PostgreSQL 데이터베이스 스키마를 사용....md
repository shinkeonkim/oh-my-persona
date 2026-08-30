## Question

회사에서 PostgreSQL 데이터베이스 스키마를 사용하는 소프트웨어를 개발하고 있습니다. 회사는 회사 개발자를 위해 여러 개발 환경과 데이터베이스를 구성해야 합니다. 평균적으로 각 개발 환경은 8시간 근무 시간의 절반을 사용합니다.
이러한 요구 사항을 가장 비용 효율적으로 충족하는 솔루션은 무엇입니까?

- [ ] A. 자체 Amazon Aurora PostgreSQL 데이터베이스로 각 개발 환경 구성
- [ ] B. 자체 Amazon RDS for PostgreSQL 단일 AZ DB 인스턴스로 각 개발 환경 구성
- [ ] C. 자체 Amazon Aurora 온디맨드 PostgreSQL 호환 데이터베이스로 각 개발 환경 구성
- [ ] D. Amazon S3 Object Select를 사용하여 자체 Amazon S3 버킷으로 각 개발 환경 구성

## Answer

정답: C

## Explanation

Amazon Aurora 온디맨드 PostgreSQL 호환 데이터베이스(Aurora Serverless)를 사용하면 각 개발 환경이 평균적으로 8시간 근무 시간 중 절반(4시간)만 사용되므로, 사용하지 않는 시간 동안 자동으로 일시 중지되어 비용을 절감할 수 있습니다. Aurora Serverless는 사용한 만큼만 초 단위로 비용이 청구되므로 간헐적 사용 패턴의 개발 환경에 가장 비용 효율적입니다.

오답 분석

A: Aurora PostgreSQL 프로비저닝 데이터베이스는 고정 인스턴스 비용이 발생하여 사용하지 않는 4시간 동안에도 비용이 청구됩니다. 개발 환경의 간헐적 사용 패턴에는 비용 효율적이지 않습니다.

B: Amazon RDS for PostgreSQL 단일 AZ DB 인스턴스도 고정 인스턴스 비용이 지속적으로 발생합니다. 개발 환경이 근무 시간의 절반만 사용되므로 나머지 시간에 비용이 낭비됩니다.

D: Amazon S3 Object Select는 S3에 저장된 데이터에서 SQL과 유사한 쿼리를 실행하는 기능이지만, PostgreSQL 데이터베이스 스키마를 대체할 수 없으며 트랜잭션 처리를 지원하지 않습니다.

