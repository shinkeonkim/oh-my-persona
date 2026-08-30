## Question

한 회사가 AWS 클라우드의 Auto Scaling 그룹에 속하는 Amazon EC2 인스턴스에서 게임 애플리케이션을 실행하려고 합니다. 애플리케이션은 UDP 패킷을 사용하여 데이터를 전송합니다. 회사는 트래픽이 증가하거나 감소함에 따라 애플리케이션을 확장 및 축소할 수 있기를 원합니다.
솔루션 설계자는 이러한 요구 사항을 충족하기 위해 무엇을 해야 합니까?

- [ ] A. Auto Scaling 그룹에 Network Load Balancer를 연결합니다.
- [ ] B. Auto Scaling 그룹에 Application Load Balancer를 연결합니다.
- [ ] C. 트래픽을 적절하게 라우팅하기 위한 가중치 정책이 포함된 Amazon Route 53 레코드 세트를 배포합니다.
- [ ] D. Auto Scaling 그룹의 EC2 인스턴스에 대한 포트 전달로 구성된 NAT 인스턴스를 배포합니다.

## Answer

정답: A

## Explanation

Network Load Balancer(NLB)는 OSI 모델의 4계층(전송 계층)에서 작동하며, TCP와 UDP 프로토콜 모두를 지원합니다. 게임 애플리케이션이 UDP 패킷을 사용하므로 NLB가 적합한 로드 밸런서입니다. NLB를 Auto Scaling 그룹에 연결하면, Auto Scaling이 트래픽 증감에 따라 인스턴스를 자동으로 추가/제거하고, NLB가 활성 인스턴스에 UDP 트래픽을 분산합니다. NLB는 초당 수백만 개의 요청을 처리할 수 있는 높은 성능과 극히 낮은 지연 시간을 제공합니다.

오답 분석

B: Application Load Balancer(ALB)는 OSI 모델의 7계층(애플리케이션 계층)에서 작동하며, HTTP/HTTPS 트래픽만 지원합니다. UDP 패킷을 처리할 수 없으므로 게임 애플리케이션의 요구사항을 충족하지 못합니다.

C: Route 53 가중(Weighted) 라우팅 정책은 DNS 수준에서 트래픽을 비율에 따라 분배하지만, Auto Scaling 그룹과 직접 통합되지 않습니다. 인스턴스가 추가/제거될 때마다 DNS 레코드를 수동으로 업데이트해야 하며, DNS TTL로 인한 지연이 발생하여 자동 확장/축소에 적합하지 않습니다.

D: NAT 인스턴스는 프라이빗 서브넷의 인스턴스가 인터넷으로 아웃바운드 트래픽을 보내기 위한 것이며, 인바운드 게임 트래픽의 로드 밸런싱 용도가 아닙니다. 포트 전달로 일부 인바운드 트래픽을 처리할 수 있지만, NLB의 자동 부하 분산, 상태 확인, Auto Scaling 통합 기능을 제공하지 않습니다.

