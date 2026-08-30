## Question

한 회사에서는 Amazon EC2 인스턴스의 일상적인 관리 및 패치에 AWS Systems Manager를 사용합니다. EC2 인스턴스는 Application Load Balancer(ALB) 뒤의 IP 주소 유형 대상 그룹에 있습니다. 새로운 보안 프로토콜은 패치 중에 회사에서 EC2 인스턴스를 서비스에서 제거하도록 요구합니다. 회사가 다음 패치 중에 보안 프로토콜을 따르려고 하면 패치 창에서 오류가 발생합니다.
어떤 솔루션 조합이 오류를 해결할 수 있을까요? (두 가지를 선택하세요.)

- [ ] A. 대상 그룹의 대상 유형을 IP 주소 유형에서 인스턴스 유형으로 변경합니다.
- [ ] B. ALB 뒤에 있는 IP 주소 유형 대상 그룹의 인스턴스를 처리하도록 이미 최적화되어 있으므로 기존 Systems Manager 문서를 변경 없이 계속 사용합니다.
- [ ] C. AWSEC2-PatchLoadBalancerInstance Systems Manager Automation 문서를 구현하여 패치 프로세스를 관리합니다.
- [ ] D. Systems Manager Maintenance Windows를 사용하여 인스턴스를 서비스에서 자동으로 제거하여 인스턴스에 패치를 적용합니다.
- [ ] E. Systems Manager State Manager를 구성하여 서비스에서 인스턴스를 제거하고 패치 일정을 관리합니다. ALB 상태 검사를 사용하여 트래픽을 다시 라우팅합니다.

## Answer

정답: C, D

## Explanation

AWSEC2-PatchLoadBalancerInstance Systems Manager Automation 문서는 ALB 뒤의 인스턴스를 패치할 때 자동으로 서비스에서 제거하고 패치 후 다시 등록하는 기능을 제공합니다. Systems Manager Maintenance Windows를 사용하면 패치 일정을 자동화하여 인스턴스를 서비스에서 제거하고 패치할 수 있습니다.

오답 분석

A: 대상 그룹의 유형을 IP에서 인스턴스로 변경하는 것은 패치 프로세스의 오류를 직접적으로 해결하지 않습니다.

B: 기존 Systems Manager 문서가 ALB 뒤의 IP 주소 유형 대상 그룹을 처리하도록 최적화되어 있다는 것은 사실이 아니며, 전용 Automation 문서가 필요합니다.

E: Systems Manager State Manager는 패치 관리에 적합하지 않으며, ALB 헬스 체크만으로는 패치 중 인스턴스를 서비스에서 적절히 제거하고 복원하는 프로세스를 관리할 수 없습니다.

