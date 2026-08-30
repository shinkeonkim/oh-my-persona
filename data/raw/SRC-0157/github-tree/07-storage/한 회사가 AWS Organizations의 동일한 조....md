## Question

한 회사가 AWS Organizations의 동일한 조직 내 여러 AWS 계정에서 여러 애플리케이션을 실행합니다. 콘텐츠 관리 시스템(CMS)은 VPC의 Amazon EC2 인스턴스에서 실행됩니다. CMS는 별도의 AWS 계정에 배포된 Amazon Elastic File System(Amazon EFS) 파일 시스템에서 공유 파일에 액세스해야 합니다. EFS 계정은 별도의 VPC에 있습니다.
이 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. EFS Elastic IP 주소를 사용하여 EC2 인스턴스에 EFS 파일 시스템을 마운트합니다.
- [ ] B. 두 계정 간의 VPC 공유를 활성화합니다. EFS 마운트 도우미를 사용하여 EC2 인스턴스에 파일 시스템을 마운트합니다. 공유 서브넷에 EFS 파일 시스템을 다시 배포합니다.
- [ ] C. EC2 인스턴스에 EFS 파일 시스템을 마운트하도록 AWS Systems Manager Run Command를 구성합니다.
- [ ] D. EC2 인스턴스에 amazon-efs-utils 패키지를 설치합니다. efs-config 파일에 마운트 대상을 추가합니다. EFS 액세스 포인트를 사용하여 EFS 파일 시스템을 마운트합니다.

## Answer

정답: D

## Explanation

교차 계정 Amazon EFS 접근을 구현하려면 클라이언트 측에서 다음과 같은 구성이 필요합니다. EC2 인스턴스에 amazon-efs-utils 패키지를 설치하면 EFS 마운트 헬퍼(mount.efs)를 사용할 수 있으며, 이는 교차 계정 마운트 시 필수적인 도구입니다. 교차 계정 시나리오에서는 DNS 기반 자동 해석이 되지 않으므로 efs-utils.conf 파일에 다른 계정의 EFS 마운트 대상 IP 주소를 수동으로 지정해야 합니다. EFS 액세스 포인트를 사용하여 마운트하면 애플리케이션별로 POSIX 사용자/그룹 및 루트 디렉터리를 적용하여 세분화된 접근 제어가 가능합니다. 이를 위한 전제 조건으로 두 VPC 간 네트워크 연결(VPC 피어링 또는 Transit Gateway)과 EFS 파일 시스템 리소스 정책에서의 타 계정 접근 허용 설정이 필요합니다.

오답 분석

A: EFS는 Elastic IP 주소를 지원하지 않습니다. EFS 마운트 대상은 프라이빗 IP 주소만 가지며, Elastic IP를 연결하는 것은 불가능합니다.

B: AWS RAM을 통한 VPC 서브넷 공유 자체는 가능하지만, EFS를 공유 서브넷에 재배포하는 것은 데이터 마이그레이션이 필요하고 불필요한 복잡성과 데이터 손실 위험을 초래합니다.

C: AWS Systems Manager Run Command는 원격 명령 실행 도구일 뿐, 교차 계정 네트워크 연결이나 EFS 인증/권한 부여 문제를 해결하지 못합니다. VPC 간 네트워크 경로와 교차 계정 권한이 없으면 마운트 명령을 실행하더라도 마운트 자체가 실패합니다.

