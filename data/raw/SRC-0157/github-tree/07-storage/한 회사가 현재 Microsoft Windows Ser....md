## Question

한 회사가 현재 Microsoft Windows Server를 사용하여 온프레미스 주식 거래 애플리케이션을 실행하고 있습니다. 이 회사는 애플리케이션을 AWS 클라우드로 마이그레이션하려고 합니다. 이 회사는 여러 가용성 영역에 걸쳐 블록 스토리지에 대한 저지연 액세스를 제공하는 고가용성 솔루션을 설계해야 합니다. 어떤 솔루션이 최소한의 구현 노력으로 이러한 요구 사항을 충족할까요?

- [ ] A. Amazon EC2 인스턴스에서 두 개의 가용성 영역에 걸쳐 있는 Windows Server 클러스터를 구성합니다. 두 클러스터 노드에 애플리케이션을 설치합니다. 두 클러스터 노드 간의 공유 스토리지로 Amazon FSx for Windows File Server를 사용합니다.
- [ ] B. Amazon EC2 인스턴스에서 두 개의 가용성 영역에 걸쳐 있는 Windows Server 클러스터를 구성합니다. 두 클러스터 노드에 애플리케이션을 설치합니다. EC2 인스턴스에 연결된 스토리지로 Amazon Elastic Block Store(Amazon EBS) General Purpose SSD(gp3) 볼륨을 사용합니다. 애플리케이션 수준 복제를 설정하여 한 가용성 영역의 한 EBS 볼륨에서 두 번째 가용성 영역의 다른 EBS 볼륨으로 데이터를 동기화합니다.
- [ ] C. 두 개의 가용성 영역에 있는 Amazon EC2 인스턴스에 애플리케이션을 배포합니다. 한 EC2 인스턴스를 활성 모드로 구성하고 두 번째 EC2 인스턴스를 대기 모드로 구성합니다. Amazon FSx for NetApp ONTAP Multi-AZ 파일 시스템을 사용하여 iSCSI(Internet Small Computer Systems Interface) 프로토콜을 사용하여 데이터에 액세스합니다.
- [ ] D. 두 개의 가용성 영역에 있는 Amazon EC2 인스턴스에 애플리케이션을 배포합니다. 한 EC2 인스턴스를 활성 모드로 구성하고 두 번째 EC2 인스턴스를 대기 모드로 구성합니다. Amazon Elastic Block Store(Amazon EBS) Provisioned IOPS SSD(io2) 볼륨을 EC2 인스턴스에 연결된 스토리지로 사용합니다. Amazon EBS 수준 복제를 설정하여 한 가용성 영역의 한 io2 볼륨에서 두 번째 가용성 영역의 다른 io2 볼륨으로 데이터를 동기화합니다.

## Answer

정답: A

## Explanation

Amazon FSx for Windows File Server를 공유 스토리지로 사용하는 Windows Server 클러스터를 두 개의 가용 영역에 걸쳐 구성하면, 고가용성과 저지연 공유 파일 스토리지 접근을 모두 제공합니다. FSx for Windows는 Windows 네이티브 호환성과 SMB 프로토콜을 지원하며, Multi-AZ 배포가 가능합니다.

오답 분석

B: EBS gp3 볼륨은 단일 가용 영역에 바인딩되어 AZ 간 공유가 불가능하며, 애플리케이션 수준 복제는 구현 노력이 더 큽니다.

C: FSx for NetApp ONTAP의 iSCSI는 블록 스토리지를 제공하지만, 액티브-스탠바이 구성은 FSx for Windows Server의 Windows 클러스터보다 구현 노력이 더 큽니다.

D: EBS io2 볼륨은 AZ 간 자동 복제를 지원하지 않으며, EBS 수준 복제는 존재하지 않는 기능입니다.

