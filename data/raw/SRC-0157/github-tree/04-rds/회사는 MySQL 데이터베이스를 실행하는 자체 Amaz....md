## Question

회사는 MySQL 데이터베이스를 실행하는 자체 Amazon EC2 인스턴스를 관리합니다. 회사는 수요가 증가하거나 감소함에 따라 복제 및 확장을 수동으로 관리하고 있습니다. 회사는 필요에 따라 데이터베이스 계층에서 컴퓨팅 용량을 추가하거나 제거하는 프로세스를 간소화하는 새로운 솔루션이 필요합니다. 또한 솔루션은 최소한의 운영 노력으로 향상된 성능, 확장성 및 내구성을 제공해야 합니다.
어떤 솔루션이 이러한 요구 사항을 충족합니까?

- [ ] A. 데이터베이스를 Aurora MySQL용 Amazon Aurora Serverless로 마이그레이션합니다.
- [ ] B. 데이터베이스를 Aurora PostgreSQL용 Amazon Aurora Serverless로 마이그레이션합니다.
- [ ] C. 데이터베이스를 하나의 더 큰 MySQL 데이터베이스로 결합합니다. 더 큰 EC2 인스턴스에서 더 큰 데이터베이스를 실행합니다.
- [ ] D. 데이터베이스 계층에 대한 EC2 Auto Scaling 그룹을 생성합니다. 기존 데이터베이스를 새 환경으로 마이그레이션합니다.

## Answer

정답: A

## Explanation

Amazon Aurora Serverless for Aurora MySQL은 수요에 따라 자동으로 컴퓨팅 용량을 추가하거나 제거할 수 있는 완전 관리형 서비스입니다. MySQL 호환이므로 기존 MySQL 데이터베이스에서 마이그레이션이 간편하며, 수동으로 복제 및 확장을 관리할 필요가 없습니다. Aurora는 표준 MySQL 대비 최대 5배의 성능 향상, 자동 스토리지 확장, 3개의 가용 영역에 걸친 6방향 복제를 통한 높은 내구성을 제공합니다.

오답 분석

B: Aurora Serverless for Aurora PostgreSQL은 MySQL이 아닌 PostgreSQL 엔진을 사용합니다. 기존 MySQL 데이터베이스에서 마이그레이션하려면 스키마와 쿼리를 PostgreSQL로 변환해야 하므로 운영 노력이 증가합니다.

C: 더 큰 EC2 인스턴스에서 하나의 더 큰 MySQL 데이터베이스를 실행하는 것은 수직 확장(scale up) 방식으로, 자동 확장이 불가능하며 수동 관리가 필요합니다. 또한 관리형 서비스가 아니므로 운영 부담이 큽니다.

D: EC2 Auto Scaling 그룹은 데이터베이스 계층에 적합하지 않습니다. 데이터베이스는 상태를 유지해야 하며(stateful), EC2 Auto Scaling은 상태 비저장(stateless) 애플리케이션에 적합합니다. 데이터 일관성과 복제 관리가 매우 복잡해집니다.

