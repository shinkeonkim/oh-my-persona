## Question

회사에서 AWS 인프라에 대한 월별 유지 관리를 수행합니다. 이러한 유지 관리 활동 중에 회사는 여러 AWS 리전에서 Amazon RDS for MySQL 데이터베이스에 대한 자격 증명을 교체해야 합니다.
최소한의 운영 오버헤드로 이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. 자격 증명을 AWS Secrets Manager에 비밀로 저장합니다. 필요한 리전에 대해 다중 리전 비밀 복제를 사용합니다. 일정에 따라 비밀을 교체하도록 Secrets Manager를 구성합니다.
- [ ] B. 보안 문자열 파라미터를 생성하여 AWS Systems Manager에 자격 증명을 비밀로 저장합니다. 필요한 리전에 대해 다중 리전 비밀 복제를 사용합니다. 일정에 따라 암호를 교체하도록 Systems Manager를 구성합니다.
- [ ] C. 서버 측 암호화(SSE)가 활성화된 Amazon S3 버킷에 자격 증명을 저장합니다. Amazon EventBridge(Amazon CloudWatch Events)를 사용하여 AWS Lambda 함수를 호출하여 자격 증명을 교체합니다.
- [ ] D. AWS Key Management Service(AWS KMS) 다중 리전 고객 관리 키를 사용하여 자격 증명을 비밀로 암호화합니다. Amazon DynamoDB 전역 테이블에 비밀을 저장합니다. AWS Lambda 함수를 사용하여 DynamoDB에서 비밀을 검색합니다. RDS API를 사용하여 비밀을 교체합니다.

## Answer

정답: A

## Explanation

AWS Secrets Manager는 데이터베이스 자격 증명을 안전하게 저장하고, 다중 리전 비밀 복제 기능을 통해 여러 AWS 리전에 자격 증명을 자동으로 복제할 수 있습니다. 또한 일정에 따른 자동 비밀 교체 기능을 기본적으로 제공하여 최소한의 운영 오버헤드로 RDS for MySQL 데이터베이스의 자격 증명을 관리하고 교체할 수 있습니다. Secrets Manager는 RDS와의 네이티브 통합을 제공합니다.

오답 분석

B: AWS Systems Manager Parameter Store는 보안 문자열 파라미터를 지원하지만, 기본적인 자동 비밀 교체 기능이 없으며 다중 리전 비밀 복제 기능도 제공하지 않습니다. 교체를 위해서는 별도의 Lambda 함수를 구현해야 합니다.

C: Amazon S3에 자격 증명을 저장하고 EventBridge와 Lambda를 사용하여 교체하는 것은 수동으로 모든 것을 구현해야 하므로 운영 오버헤드가 큽니다.

D: KMS 다중 리전 키와 DynamoDB 전역 테이블, Lambda 함수를 조합하는 방식은 매우 복잡하며 운영 오버헤드가 가장 큽니다. Secrets Manager가 이 모든 기능을 내장하고 있습니다.

