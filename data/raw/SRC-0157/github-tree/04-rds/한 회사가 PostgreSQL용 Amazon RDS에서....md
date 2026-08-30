## Question

한 회사가 PostgreSQL용 Amazon RDS에서 데이터베이스를 실행합니다. 회사는 30일마다 비밀번호를 교체하여 마스터 사용자 비밀번호를 관리하는 안전한 솔루션을 원합니다.
최소한의 운영 오버헤드로 이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. Amazon EventBridge를 사용하여 30일마다 암호를 교체하도록 사용자 지정 AWS Lambda 함수를 예약합니다.
- [ ] B. AWS CLI에서 modify-db-instance 명령을 사용하여 비밀번호를 변경합니다.
- [ ] C. AWS Secrets Manager를 PostgreSQL용 Amazon RDS와 통합하여 암호 교체를 자동화합니다.
- [ ] D. AWS Systems Manager Parameter Store를 PostgreSQL용 Amazon RDS와 통합하여 암호 교체를 자동화합니다.

## Answer

정답: C

## Explanation

AWS Secrets Manager를 Amazon RDS for PostgreSQL과 통합하면 마스터 사용자 비밀번호를 30일마다 자동으로 교체할 수 있습니다. Secrets Manager는 RDS와의 네이티브 통합을 통해 관리형 비밀번호 교체를 제공하며, 교체 일정을 설정하면 자동으로 데이터베이스의 마스터 비밀번호를 업데이트합니다. 이는 최소한의 운영 오버헤드로 안전한 비밀번호 관리를 제공합니다.

오답 분석

A: Amazon EventBridge와 사용자 지정 Lambda 함수를 사용하여 비밀번호를 교체하는 것은 가능하지만, Lambda 함수를 직접 작성하고 유지 관리해야 하므로 Secrets Manager의 관리형 교체 기능보다 운영 오버헤드가 큽니다.

B: AWS CLI의 modify-db-instance 명령을 사용하여 수동으로 비밀번호를 변경하는 것은 자동화가 아니며, 30일마다 수동으로 실행해야 하므로 운영 오버헤드가 가장 큽니다.

D: AWS Systems Manager Parameter Store는 RDS와의 네이티브 통합을 통한 비밀번호 자동 교체 기능을 제공하지 않습니다. 이 기능은 Secrets Manager에서만 사용할 수 있습니다.

