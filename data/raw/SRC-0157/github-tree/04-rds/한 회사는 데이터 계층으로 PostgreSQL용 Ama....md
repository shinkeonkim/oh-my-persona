## Question

한 회사는 데이터 계층으로 PostgreSQL용 Amazon RDS 데이터베이스를 사용합니다. 회사는 데이터베이스에 대한 비밀번호 교체를 구현해야 합니다.
최소한의 운영 오버헤드로 이 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. AWS Secrets Manager에 비밀번호를 저장합니다. 보안 비밀에 대한 자동 교체를 활성화합니다.
- [ ] B. AWS Systems Manager Parameter Store에 비밀번호를 저장합니다. 매개변수에 대한 자동 교체를 활성화합니다.
- [ ] C. AWS Systems Manager Parameter Store에 비밀번호를 저장합니다. 비밀번호를 교체하는 AWS Lambda 함수를 작성합니다.
- [ ] D. AWS Key Management Service(AWS KMS)에 비밀번호를 저장합니다. AWS KMS 키에서 자동 교체를 활성화합니다.

## Answer

정답: A

## Explanation

AWS Secrets Manager에 비밀번호를 저장하고 자동 교체를 활성화하면 최소한의 운영 오버헤드로 RDS for PostgreSQL 데이터베이스의 비밀번호 교체를 구현할 수 있습니다. Secrets Manager는 RDS 데이터베이스와 네이티브 통합을 제공하며, 관리형 교체 기능을 통해 별도의 코드 작성 없이 자동으로 비밀번호를 교체합니다.

오답 분석

B: AWS Systems Manager Parameter Store는 자동 교체(automatic rotation) 기능을 기본적으로 지원하지 않습니다. Parameter Store의 SecureString 파라미터에 대한 자동 교체는 별도의 구현이 필요합니다.

C: Systems Manager Parameter Store에 비밀번호를 저장하고 별도의 Lambda 함수를 작성하여 교체하는 것은 가능하지만, 직접 Lambda 함수를 작성하고 관리해야 하므로 운영 오버헤드가 증가합니다.

D: AWS KMS는 암호화 키를 관리하는 서비스이며, 비밀번호를 저장하는 용도가 아닙니다. KMS 키의 자동 교체는 암호화 키 자체를 교체하는 것이지 데이터베이스 비밀번호를 교체하는 것이 아닙니다.

