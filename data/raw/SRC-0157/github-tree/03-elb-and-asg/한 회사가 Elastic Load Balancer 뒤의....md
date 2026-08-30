## Question

한 회사가 Elastic Load Balancer 뒤의 Amazon EC2 인스턴스에서 실행될 새로운 웹 서비스를 설계하고 있습니다. 그러나 많은 웹 서비스 클라이언트는 방화벽에 허용된 IP 주소에만 접근할 수 있습니다.
솔루션 아키텍트는 고객의 요구 사항을 충족하기 위해 무엇을 권장해야 합니까?

- [ ] A. 탄력적 IP 주소가 연결된 Network Load Balancer
- [ ] B. 탄력적 IP 주소가 연결된 Application Load Balancer
- [ ] C. 탄력적 IP 주소를 가리키는 Amazon Route 53 호스팅 영역의 A 레코드
- [ ] D. 로드 밸런서 앞에서 프록시로 실행되는 퍼블릭 IP 주소가 있는 EC2 인스턴스

## Answer

정답: A

## Explanation

Network Load Balancer(NLB)는 AWS 로드 밸런서 중 유일하게 고정 Elastic IP 주소를 각 가용 영역에 연결할 수 있습니다. 방화벽에서 특정 IP 주소만 허용(화이트리스트)하는 클라이언트의 경우, NLB에 연결된 고정 Elastic IP를 제공하면 해당 IP를 방화벽 규칙에 등록하여 안정적으로 접근할 수 있습니다. NLB는 가용 영역당 하나의 Elastic IP를 할당할 수 있어, 최소한의 IP 주소로 로드 밸런싱을 제공합니다.

오답 분석

B: Application Load Balancer(ALB)는 Elastic IP 주소를 직접 연결할 수 없습니다. ALB의 IP 주소는 AWS가 관리하며 동적으로 변경될 수 있어, 방화벽에서 고정 IP를 화이트리스트에 등록해야 하는 클라이언트 요구 사항을 충족하지 못합니다.

C: Route 53의 A 레코드가 Elastic IP를 가리키도록 설정할 수 있지만, 이것만으로는 단일 IP/인스턴스에 대한 DNS 레코드일 뿐 여러 EC2 인스턴스에 대한 로드 밸런싱 기능을 제공하지 않습니다. 고가용성과 부하 분산을 위해서는 로드 밸런서가 필요합니다.

D: EC2 인스턴스를 로드 밸런서 앞에 프록시로 실행하면 단일 장애 지점(Single Point of Failure)이 됩니다. 해당 인스턴스에 장애가 발생하면 전체 서비스가 중단되며, 수동 관리 오버헤드가 크고 확장성이 떨어집니다.

