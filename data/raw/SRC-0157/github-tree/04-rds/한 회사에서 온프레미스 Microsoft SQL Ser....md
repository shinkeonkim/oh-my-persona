## Question

한 회사에서 온프레미스 Microsoft SQL Server Enterprise 에디션 데이터베이스를 AWS로 마이그레이션하려고 합니다. 회사의 온라인 애플리케이션은 데이터베이스를 사용하여 거래를 처리합니다. 데이터 분석 팀은 동일한 프로덕션 데이터베이스를 사용하여 분석 처리를 위한 보고서를 실행합니다. 회사는 가능한 한 관리형 서비스로 전환하여 운영 오버헤드를 줄이고 싶어합니다.
최소한의 운영 오버헤드로 이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. Microsoft SQL Server용 Amazon RDS로 마이그레이션합니다. 보고 목적으로 읽기 복제본을 사용합니다.
- [ ] B. Amazon EC2의 Microsoft SQL Server로 마이그레이션합니다. 보고 목적으로 Always On 읽기 복제본을 사용합니다.
- [ ] C. Amazon DynamoDB로 마이그레이션합니다. 보고 목적으로 DynamoDB 온디맨드 복제본을 사용합니다.
- [ ] D. Amazon Aurora MySQL로 마이그레이션합니다. 보고 목적으로 Aurora 읽기 전용 복제본을 사용합니다.

## Answer

정답: A

## Explanation

Amazon RDS for Microsoft SQL Server로 마이그레이션하면 관리형 서비스로 전환하여 운영 오버헤드를 줄일 수 있습니다. RDS는 패칭, 백업, 장애 조치 등을 자동으로 관리합니다. Amazon RDS for SQL Server Enterprise Edition은 Always On 가용성 그룹을 사용한 읽기 전용 복제본을 지원하며, 이를 통해 보고 쿼리를 분리할 수 있는 읽기 가능한 보조 인스턴스가 생성됩니다. 참고: Multi-AZ 스탠바이 인스턴스는 읽기가 불가능합니다. 분석 팀의 읽기 트래픽을 처리하는 것은 Multi-AZ 스탠바이가 아닌, Always On 가용성 그룹을 통해 별도로 생성된 읽기 전용 복제본입니다.

오답 분석

B: Amazon EC2에 Microsoft SQL Server를 배포하면 관리형 서비스가 아니므로 OS 패칭, 백업, 고가용성 구성 등을 직접 관리해야 하여 운영 오버헤드가 높습니다.

C: Amazon DynamoDB는 NoSQL 데이터베이스로, SQL Server에서 마이그레이션하려면 스키마와 쿼리를 완전히 재설계해야 합니다. 또한 DynamoDB 온디맨드 복제본이라는 기능은 존재하지 않습니다.

D: Amazon Aurora MySQL로 마이그레이션하면 SQL Server에서 MySQL로 데이터베이스 엔진을 변경해야 하므로 애플리케이션 코드 수정이 필요하며, 이는 운영 오버헤드를 크게 증가시킵니다.

