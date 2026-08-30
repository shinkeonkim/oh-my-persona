## Question

솔루션 설계자는 Windows 인터넷 정보 서비스(IIS) 웹 애플리케이션을 AWS로 마이그레이션해야 합니다. 애플리케이션은 현재 사용자의 온프레미스 NAS(Network-Attached Storage)에서 호스팅되는 파일 공유에 의존합니다. 솔루션 설계자는 IIS 웹 서버를 스토리지 솔루션에 연결된 여러 가용 영역의 Amazon EC2 인스턴스로 마이그레이션하고 인스턴스에 연결된 Elastic Load Balancer를 구성할 것을 제안했습니다.
온프레미스 파일 공유에 대한 어떤 대체가 가장 탄력적이고 내구성이 있습니까?

- [ ] A. 파일 공유를 Amazon RDS로 마이그레이션합니다.
- [ ] B. 파일 공유를 AWS Storage Gateway로 마이그레이션합니다.
- [ ] C. 파일 공유를 Amazon FSx for Windows File Server로 마이그레이션합니다.
- [ ] D. 파일 공유를 Amazon Elastic File System(Amazon EFS)으로 마이그레이션합니다.

## Answer

정답: C

## Explanation

Amazon FSx for Windows File Server는 Windows IIS 웹 애플리케이션의 온프레미스 NAS 파일 공유를 대체하기에 가장 적합한 솔루션입니다. SMB 프로토콜을 기본 지원하여 IIS 애플리케이션이 코드 변경 없이 파일에 접근할 수 있으며, Multi-AZ 배포로 높은 복원력과 내구성을 제공합니다. 여러 AZ의 EC2 인스턴스에서 동시에 마운트할 수 있어 ELB 뒤의 다중 인스턴스 아키텍처와 호환됩니다.

오답 분석

A: Amazon RDS는 관계형 데이터베이스 서비스이며, 파일 공유를 제공하는 스토리지 솔루션이 아닙니다. IIS 웹 애플리케이션의 정적 파일, 이미지, 문서 등의 파일 공유를 대체할 수 없습니다.

B: AWS Storage Gateway는 온프레미스와 AWS 간 하이브리드 스토리지 연결을 위한 서비스입니다. AWS 클라우드 내에서 EC2 인스턴스 간 파일 공유를 직접 제공하는 것이 아니므로, FSx for Windows File Server가 더 직접적이고 복원력 있는 솔루션입니다.

D: Amazon EFS는 NFS 프로토콜만 지원하며, Windows IIS 애플리케이션에 필요한 SMB 프로토콜을 지원하지 않습니다. IIS가 SMB 파일 공유에 의존하므로 EFS는 프로토콜 호환성 문제로 부적합합니다.

