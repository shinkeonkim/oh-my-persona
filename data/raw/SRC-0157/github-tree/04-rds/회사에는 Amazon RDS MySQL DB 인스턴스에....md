## Question

회사에는 Amazon RDS MySQL DB 인스턴스에서 정보를 검색하는 자격 증명이 내장된 사용자 지정 애플리케이션이 있습니다. 경영진은 최소한의 프로그래밍 노력으로 애플리케이션을 더 안전하게 만들어야 한다고 말합니다.
솔루션 설계자는 이러한 요구 사항을 충족하기 위해 무엇을 해야 합니까?

- [ ] A. AWS Key Management Service(AWS KMS)를 사용하여 키를 생성합니다. AWS KMS에서 데이터베이스 자격 증명을 로드하도록 애플리케이션을 구성합니다. 자동 키 순환을 활성화합니다.
- [ ] B. 애플리케이션 사용자를 위해 RDS for MySQL 데이터베이스에서 자격 증명을 생성하고 자격 증명을 AWS Secrets Manager에 저장합니다. Secrets Manager에서 데이터베이스 자격 증명을 로드하도록 애플리케이션을 구성합니다. Secrets Manager에서 자격 증명을 교체하는 AWS Lambda 함수를 생성합니다.
- [ ] C. 애플리케이션 사용자를 위해 RDS for MySQL 데이터베이스에서 자격 증명을 생성하고 자격 증명을 AWS Secrets Manager에 저장합니다. Secrets Manager에서 데이터베이스 자격 증명을 로드하도록 애플리케이션을 구성합니다. Secrets Manager를 사용하여 RDS for MySQL 데이터베이스에서 애플리케이션 사용자의 자격 증명 교체 일정을 설정합니다.
- [ ] D. 애플리케이션 사용자를 위해 RDS for MySQL 데이터베이스에서 자격 증명을 생성하고 자격 증명을 AWS Systems Manager Parameter Store에 저장합니다. Parameter Store에서 데이터베이스 자격 증명을 로드하도록 애플리케이션을 구성합니다. Parameter Store를 사용하여 RDS for MySQL 데이터베이스에서 애플리케이션 사용자에 대한 자격 증명 교체 일정을 설정합니다.

## Answer

정답: C

## Explanation

RDS for MySQL 데이터베이스에서 애플리케이션 사용자의 자격 증명을 생성하고 AWS Secrets Manager에 저장한 후, Secrets Manager의 자격 증명 교체 일정을 설정하는 것이 가장 적합한 솔루션입니다. Secrets Manager는 RDS와 네이티브 통합을 제공하여 자동으로 데이터베이스 자격 증명을 교체할 수 있으며, 별도의 Lambda 함수를 직접 작성할 필요 없이 관리형 교체 기능을 사용할 수 있습니다. 이는 최소한의 프로그래밍 노력으로 보안을 강화합니다.

오답 분석

A: AWS KMS는 암호화 키를 관리하는 서비스이며, 데이터베이스 자격 증명을 저장하는 용도로 설계되지 않았습니다. KMS 키 교체는 암호화 키 교체이지 데이터베이스 비밀번호 교체가 아닙니다.

B: Secrets Manager에 자격 증명을 저장하는 것은 올바르지만, 별도의 Lambda 함수를 생성하여 자격 증명을 교체하는 것은 Secrets Manager의 기본 관리형 교체 기능을 사용하는 것보다 프로그래밍 노력이 더 필요합니다.

D: AWS Systems Manager Parameter Store는 자격 증명을 저장할 수 있지만, 자격 증명 교체 일정 설정을 기본적으로 지원하지 않으며, 교체를 위해 별도의 구현이 필요합니다.

