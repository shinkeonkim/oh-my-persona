## Question

한 회사에서 Auto Scaling 그룹의 클라이언트와 서버 간의 통신에 UDP를 사용하는 실시간 멀티플레이어 게임을 개발하고 있습니다. 하루 동안 수요가 급증할 것으로 예상되므로 게임 서버 플랫폼은 그에 따라 적응해야 합니다. 개발자는 개입 없이 확장되는 데이터베이스 솔루션에 게이머 점수 및 기타 비관계형 데이터를 저장하기를 원합니다.
솔루션 설계자는 어떤 솔루션을 추천해야 합니까?

- [ ] A. 트래픽 분산에는 Amazon Route 53을 사용하고 데이터 저장에는 Amazon Aurora Serverless를 사용합니다.
- [ ] B. 트래픽 분산을 위해 Network Load Balancer를 사용하고 데이터 저장을 위해 Amazon DynamoDB 온디맨드를 사용합니다.
- [ ] C. 트래픽 분산을 위해 Network Load Balancer를 사용하고 데이터 저장을 위해 Amazon Aurora Global Database를 사용합니다.
- [ ] D. 트래픽 분산을 위해 Application Load Balancer를 사용하고 데이터 저장을 위해 Amazon DynamoDB 전역 테이블을 사용합니다.

## Answer

정답: B

## Explanation

Network Load Balancer(NLB)는 OSI 모델 4계층(전송 계층)에서 동작하여 TCP, UDP, TLS 프로토콜을 모두 지원합니다. UDP를 사용하는 실시간 멀티플레이어 게임 트래픽을 처리하는 데 NLB가 유일하게 적합한 로드 밸런서입니다. DynamoDB 온디맨드 모드는 하루 중 수요 급증에 자동으로 대응하며, 비관계형 데이터(게이머 점수)를 관리자 개입 없이 저장하고 확장할 수 있습니다.

오답 분석

A: Amazon Route 53은 DNS 기반 라우팅 서비스로 UDP 게임 트래픽의 실시간 로드 밸런싱에 적합하지 않습니다. DNS TTL로 인한 지연과 세밀한 부하 분산 불가 등의 제한이 있습니다. Aurora Serverless는 관계형 데이터베이스로, 비관계형 게이머 점수 데이터에는 DynamoDB가 더 적합합니다.

C: NLB는 적합하지만, Aurora Global Database는 관계형 데이터베이스로 비관계형 게이머 데이터에 부적합합니다. 또한 '개입 없이 확장되는' 요구사항에서 Aurora는 인스턴스 크기 조정 등의 관리가 필요할 수 있습니다.

D: Application Load Balancer(ALB)는 OSI 7계층(애플리케이션 계층)에서 동작하며 HTTP/HTTPS 프로토콜만 지원합니다. UDP 프로토콜을 처리할 수 없어 실시간 멀티플레이어 게임 트래픽에 사용할 수 없습니다.

