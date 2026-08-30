## Question

회사에 소프트웨어 엔지니어링에 사용되는 AWS 계정이 있습니다. AWS 계정은 한 쌍의 AWS Direct Connect 연결을 통해 회사의 온프레미스 데이터 센터에 액세스할 수 있습니다. 모든 비 VPC 트래픽은 가상 프라이빗 게이트웨이로 라우팅됩니다.
개발팀은 최근 콘솔을 통해 AWS Lambda 함수를 생성했습니다. 개발 팀은 함수가 회사 데이터 센터의 프라이빗 서브넷에서 실행되는 데이터베이스에 액세스할 수 있도록 허용해야 합니다.
이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. 적절한 보안 그룹을 사용하여 VPC에서 실행되도록 Lambda 함수를 구성합니다.
- [ ] B. AWS에서 데이터 센터로 VPN 연결을 설정합니다. VPN을 통해 Lambda 함수의 트래픽을 라우팅합니다.
- [ ] C. Lambda 함수가 Direct Connect를 통해 온프레미스 데이터 센터에 액세스할 수 있도록 VPC의 라우팅 테이블을 업데이트합니다.
- [ ] D. 탄력적 IP 주소를 생성합니다. 탄력적 네트워크 인터페이스 없이 탄력적 IP 주소를 통해 트래픽을 보내도록 Lambda 함수를 구성합니다.

## Answer

정답: A

## Explanation

Lambda 함수를 VPC에 배치하고 적절한 보안 그룹을 설정하면, 기존 AWS Direct Connect를 통해 on-premises 데이터 센터의 데이터베이스에 접근할 수 있습니다. Lambda를 VPC에 연결하면 VPC의 서브넷에 ENI(Elastic Network Interface)가 생성되어 VPC 내부 리소스 및 Direct Connect를 통한 on-premises 리소스에 접근이 가능합니다. 보안 그룹으로 on-premises DB 포트에 대한 접근을 제어하며, 별도의 네트워크 구성 없이 기존 Direct Connect 연결을 활용할 수 있어 가장 간단한 솔루션입니다.

오답 분석

B: AWS Direct Connect 연결이 이미 존재하므로 별도의 VPN 연결은 불필요한 중복 구성입니다. VPN은 추가 비용과 구성 복잡성을 유발하며, Direct Connect보다 성능이 낮습니다.

C: 라우팅 테이블을 변경하는 것만으로는 Lambda 함수가 VPC 리소스에 접근할 수 없습니다. Lambda 함수는 먼저 VPC에 연결되어야 VPC의 네트워크를 사용할 수 있으며, VPC에 연결하지 않은 Lambda는 AWS 관리형 네트워크에서 실행됩니다.

D: Lambda 함수는 Elastic IP를 직접 할당받을 수 없습니다. Lambda가 고정 IP를 필요로 하는 경우 NAT Gateway를 통해 라우팅해야 하며, 이 시나리오에서는 on-premises DB 접근에 Elastic IP가 필요하지 않습니다.

