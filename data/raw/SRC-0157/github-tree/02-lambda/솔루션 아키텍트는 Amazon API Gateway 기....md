## Question

솔루션 아키텍트는 Amazon API Gateway 기반의 새로운 서비스를 설계하고 있습니다. 서비스에 대한 요청 패턴은 예측할 수 없으며 요청이 0개에서 초당 500개 이상으로 갑자기 변경될 수 있습니다. 백엔드 데이터베이스에 유지해야 하는 데이터의 총 크기는 현재 1GB 미만이며 향후 증가를 예측할 수 없습니다. 간단한 키-값 요청을 사용하여 데이터를 쿼리할 수 있습니다.
이러한 요구 사항을 충족하는 AWS 서비스 조합은 무엇입니까? (2개를 선택하세요.)

- [ ] A. AWS Fargate
- [ ] B. AWS Lambda
- [ ] C. Amazon DynamoDB
- [ ] D. Amazon EC2 Auto Scaling
- [ ] E. MySQL 호환 Amazon Aurora

## Answer

정답: B, C

## Explanation

AWS Lambda는 예측 불가능하고 급격히 변하는 요청 패턴에 가장 적합한 컴퓨팅 서비스입니다(B). 밀리초 단위로 자동 확장되며 요청이 없으면 비용이 발생하지 않습니다. Amazon DynamoDB는 key-value 데이터 저장에 최적화된 NoSQL 데이터베이스로, 현재 1GB 미만의 데이터부터 시작하여 사실상 무제한으로 확장 가능합니다(C). DynamoDB on-demand 모드는 읽기/쓰기 용량을 자동 조정하여 트래픽 변동에 탄력적으로 대응하며, 단일 자릿수 밀리초의 일관된 응답 시간을 제공합니다.

오답 분석

A: AWS Fargate는 서버리스 컨테이너 실행 환경이지만, 컨테이너 이미지 관리와 태스크 정의가 필요합니다. 또한 급격한 트래픽 변화에 Lambda보다 확장 속도가 느리며, 최소 태스크 실행 비용이 Lambda의 pay-per-request 대비 높습니다.

D: EC2 Auto Scaling은 새 인스턴스 시작에 수 분이 소요되어 급변하는 트래픽에 즉각적 대응이 어렵습니다. 또한 EC2 인스턴스의 관리 오버헤드가 존재합니다.

E: MySQL 호환 Aurora는 관계형 데이터베이스로 key-value 저장소로는 과도합니다. 또한 인스턴스 기반 비용 모델로 DynamoDB on-demand 대비 트래픽 변동에 탄력적이지 않습니다.

