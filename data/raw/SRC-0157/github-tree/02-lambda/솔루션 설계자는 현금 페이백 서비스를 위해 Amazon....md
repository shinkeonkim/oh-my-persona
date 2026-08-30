## Question

솔루션 설계자는 현금 페이백 서비스를 위해 Amazon API Gateway에서 REST API를 설계하고 있습니다. 애플리케이션에는 컴퓨팅 리소스를 위해 1GB의 메모리와 2GB의 스토리지가 필요합니다. 애플리케이션은 데이터가 관계형 형식이어야 합니다.
최소한의 관리 노력으로 이러한 요구 사항을 충족하는 추가 AWS 서비스 조합은 무엇입니까? (두 가지를 선택하세요.)

- [ ] A. Amazon EC2
- [ ] B. AWS Lambda
- [ ] C. Amazon RDS
- [ ] D. Amazon DynamoDB
- [ ] E. Amazon Elastic Kubernetes Service (Amazon EKS)

## Answer

정답: B, C

## Explanation

AWS Lambda는 최대 10GB 메모리와 10GB 임시 스토리지(/tmp)를 지원하므로 1GB 메모리와 2GB 스토리지 요구사항을 충분히 충족합니다(B). Lambda는 API Gateway와 직접 통합되어 REST API 백엔드로 최적이며, 서버 관리가 불필요하여 관리 오버헤드가 최소화됩니다. Amazon RDS는 관계형 데이터베이스로 현금 페이백 서비스의 트랜잭션 데이터를 ACID 속성으로 안정적으로 저장할 수 있습니다(C). RDS는 관리형 서비스로 백업, 패칭, 복제 등을 자동으로 처리합니다.

오답 분석

A: Amazon EC2 인스턴스는 OS 패칭, 보안 업데이트, 용량 관리 등 인프라 관리가 필요하여 Lambda 대비 운영 오버헤드가 큽니다. 관리 오버헤드 최소화 요구사항에 부합하지 않습니다.

D: Amazon DynamoDB는 NoSQL 데이터베이스로 key-value 접근에 최적화되어 있습니다. 금융 서비스인 cash payback의 복잡한 트랜잭션 처리, 조인 쿼리, ACID 트랜잭션에는 관계형 데이터베이스(RDS)가 더 적합합니다.

E: Amazon EKS는 Kubernetes 클러스터 관리, 노드 프로비저닝, pod 스케줄링 등 가장 높은 운영 복잡성을 수반합니다. 단일 마이크로서비스에 컨테이너 오케스트레이션 플랫폼은 과도합니다.

