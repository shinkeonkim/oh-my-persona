## Question

한 회사가 외부 웹사이트를 Amazon EC2 인스턴스와 온프레미스 가상화 서버에서 운영해야 합니다. AWS 환경에는 데이터 센터와 1GB AWS Direct Connect 연결이 있습니다. 애플리케이션의 IP 주소는 변경되지 않습니다. 온프레미스 서버와 AWS 서버는 장애 발생 시 동일한 IP 주소를 유지하면서 자동으로 재시작할 수 있습니다. 일부 웹사이트 사용자는 공급업체를 허용 목록에 추가해야 하므로 솔루션에 고정 IP 주소가 필요합니다. 이 회사는 이러한 분할 트래픽을 처리할 수 있는 운영 오버헤드가 가장 낮은 솔루션이 필요합니다.
솔루션 아키텍트는 이러한 요구 사항을 충족하기 위해 무엇을 해야 합니까?

- [ ] A. 온프레미스 및 AWS IP 주소를 가리키는 규칙을 사용하여 Amazon Route 53 Resolver를 배포합니다.
- [ ] B. AWS에 Network Load Balancer를 배포합니다. 온프레미스 및 AWS IP 주소에 대한 대상 그룹을 생성합니다.
- [ ] C. AWS에 Application Load Balancer를 배포합니다. 온프레미스 및 AWS IP 주소를 대상 그룹에 등록합니다.
- [ ] D. 요청 헤더를 기반으로 온프레미스 및 AWS IP 주소로 트래픽을 전달하도록 Amazon API Gateway를 배포합니다.

## Answer

정답: B

## Explanation

Network Load Balancer(NLB)는 고정 IP 주소를 제공하고, IP 주소 기반의 대상 그룹을 통해 AWS와 on-premises 서버 모두를 대상으로 트래픽을 분산할 수 있습니다. Direct Connect를 통해 on-premises 서버에 연결하므로 운영 오버헤드가 가장 적습니다.

오답 분석

A: Route 53 Resolver는 DNS 쿼리 해석을 위한 서비스이며, 트래픽 로드 밸런싱 기능을 제공하지 않습니다.

C: ALB는 고정 IP 주소를 직접 제공하지 않으며, 사용자가 벤더를 허용 목록에 추가해야 하는 요구사항을 충족하지 못합니다.

D: API Gateway는 HTTP/HTTPS API 관리에 적합하지만, 웹사이트 트래픽을 on-premises와 AWS 간에 분산하는 로드 밸런서 역할에는 적합하지 않습니다.

