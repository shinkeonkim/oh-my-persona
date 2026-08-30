## Question

한 회사가 Oracle Database Enterprise Edition에서 애플리케이션을 실행하고 있습니다. 회사는 애플리케이션과 데이터베이스를 AWS로 마이그레이션해야 합니다. 회사는 AWS로 마이그레이션하는 동안 BYOL(Bring Your Own License) 모델을 사용할 수 있습니다. 애플리케이션은 권한 있는 액세스가 필요한 타사 데이터베이스 기능을 사용합니다.
솔루션 설계자는 데이터베이스 마이그레이션을 위한 솔루션을 설계해야 합니다.
이러한 요구 사항을 가장 비용 효율적으로 충족하는 솔루션은 무엇입니까?

- [ ] A. 기본 도구를 사용하여 데이터베이스를 Oracle용 Amazon RDS로 마이그레이션합니다. 타사 기능을 AWS Lambda로 대체합니다.
- [ ] B. 기본 도구를 사용하여 데이터베이스를 Oracle용 Amazon RDS Custom으로 마이그레이션합니다. 타사 기능을 지원하도록 새 데이터베이스 설정을 사용자 정의합니다.
- [ ] C. AWS Database Migration Service(AWS DMS)를 사용하여 데이터베이스를 Amazon DynamoDB로 마이그레이션합니다. 타사 기능을 지원하도록 새 데이터베이스 설정을 사용자 정의합니다.
- [ ] D. AWS Database Migration Service(AWS DMS)를 사용하여 PostgreSQL용 Amazon RDS로 데이터베이스를 마이그레이션합니다. 타사 기능에 대한 종속성을 제거하려면 애플리케이션 코드를 다시 작성합니다.

## Answer

정답: B

## Explanation

Amazon RDS Custom for Oracle은 BYOL(Bring Your Own License) 모델을 지원하면서 OS 및 데이터베이스에 대한 권한 있는 액세스를 제공하는 관리형 서비스입니다. 타사 데이터베이스 기능이 권한 있는 액세스를 요구하는 경우, RDS Custom을 사용하면 데이터베이스 설정을 사용자 정의하여 이러한 기능을 지원할 수 있습니다. 동시에 자동 백업, 모니터링 등 RDS의 관리형 기능을 활용하여 운영 오버헤드를 줄일 수 있습니다.

오답 분석

A: Amazon RDS for Oracle은 관리형 서비스이지만 OS 및 데이터베이스에 대한 권한 있는 액세스를 제공하지 않습니다. 타사 기능을 AWS Lambda로 대체하는 것은 복잡한 데이터베이스 기능에는 적합하지 않으며, 애플리케이션 재설계가 필요합니다.

C: Amazon DynamoDB는 NoSQL 데이터베이스로, Oracle 데이터베이스에서의 마이그레이션에 적합하지 않습니다. 스키마 변환이 필요하며, Oracle 타사 기능을 DynamoDB에서 지원할 수 없습니다.

D: PostgreSQL용 Amazon RDS로 마이그레이션하려면 Oracle에서 PostgreSQL로 데이터베이스 엔진을 변경해야 하므로 애플리케이션 코드를 다시 작성해야 합니다. 이는 비용 효율적이지 않으며 운영 오버헤드가 크게 증가합니다.

