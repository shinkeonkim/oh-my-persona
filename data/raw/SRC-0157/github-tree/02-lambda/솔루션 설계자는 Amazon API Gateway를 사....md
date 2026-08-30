## Question

솔루션 설계자는 Amazon API Gateway를 사용하여 사용자의 요청을 수신할 새 API를 설계하고 있습니다. 요청량은 매우 다양합니다. 단일 요청을 받지 않고 몇 시간이 지날 수 있습니다.
데이터 처리는 비동기식으로 이루어지지만 요청이 이루어진 후 몇 초 이내에 완료되어야 합니다.
최저 비용으로 요구 사항을 제공하기 위해 솔루션 설계자가 API를 호출하도록 해야 하는 컴퓨팅 서비스는 무엇입니까?

- [ ] A. AWS Glue 작업
- [ ] B. AWS Lambda 함수
- [ ] C. Amazon Elastic Kubernetes Service(Amazon EKS)에서 호스팅되는 컨테이너화된 서비스
- [ ] D. Amazon EC2와 함께 Amazon ECS에서 호스팅되는 컨테이너화된 서비스

## Answer

정답: B

## Explanation

AWS Lambda 함수는 매우 가변적인 요청 패턴에 가장 적합한 백엔드입니다. Lambda는 요청이 없으면 비용이 전혀 발생하지 않고(수 시간 무요청 가능), 갑작스러운 요청 증가에도 밀리초 단위로 자동 확장됩니다. Pay-per-request 과금 모델로 사용한 만큼만 비용을 지불하며, 서버 관리가 완전히 불필요합니다. API Gateway와의 네이티브 통합으로 별도 구성 없이 즉시 연동됩니다.

오답 분석

A: AWS Glue는 데이터 ETL(Extract, Transform, Load) 작업을 위한 서비스로, API 요청 처리 백엔드로 사용하도록 설계되지 않았습니다. Glue job 시작에 수 분이 소요되어 API 응답 시간 요구사항에 부적합합니다.

C: Amazon EKS는 Kubernetes 클러스터를 관리해야 하며, 최소 하나의 노드 그룹이 항상 실행되어야 합니다. 수 시간 동안 요청이 없는 패턴에서 유휴 비용이 지속적으로 발생하고, 클러스터 관리 오버헤드가 큽니다.

D: Amazon ECS + EC2는 EC2 인스턴스가 항상 실행되어야 하므로 유휴 비용이 발생합니다. Auto Scaling으로 인스턴스 수를 조절할 수 있지만, 최소 인스턴스 비용과 확장/축소 시간이 Lambda 대비 비효율적입니다.

