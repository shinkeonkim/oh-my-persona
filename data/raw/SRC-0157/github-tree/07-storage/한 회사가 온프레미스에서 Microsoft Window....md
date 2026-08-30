## Question

한 회사가 온프레미스에서 Microsoft Windows SMB 파일 공유를 실행하여 애플리케이션을 지원합니다. 이 회사는 애플리케이션을 AWS로 마이그레이션하려고 합니다. 이 회사는 여러 Amazon EC2 인스턴스에서 스토리지를 공유하려고 합니다.
어떤 솔루션이 최소한의 운영 오버헤드로 이러한 요구 사항을 충족할까요? (두 가지 선택)

- [ ] A. 탄력적 처리량을 갖춘 Amazon Elastic File System(Amazon EFS) 파일 시스템을 만듭니다.
- [ ] B. Amazon FSx for NetApp ONTAP 파일 시스템을 만듭니다.
- [ ] C. Amazon Elastic Block Store(Amazon EBS)를 사용하여 인스턴스에서 자체 관리형 Windows 파일 공유를 만듭니다.
- [ ] D. Amazon FSx for Windows File Server 파일 시스템을 만듭니다.
- [ ] E. Amazon FSx for OpenZFS 파일 시스템을 만듭니다.

## Answer

정답: B, D

## Explanation

B(Amazon FSx for NetApp ONTAP)와 D(Amazon FSx for Windows File Server)가 정답입니다. FSx for Windows File Server는 Windows SMB 프로토콜을 기본 지원하는 완전 관리형 서비스이며, FSx for NetApp ONTAP도 SMB 및 NFS 프로토콜을 모두 지원합니다. 두 서비스 모두 여러 EC2 인스턴스에서 동시에 마운트하여 공유 스토리지로 사용할 수 있어 최소 운영 오버헤드로 요구사항을 충족합니다.

오답 분석

A: Amazon EFS는 NFS 프로토콜만 지원하며, Windows SMB 파일 공유 프로토콜과는 호환되지 않습니다.

C: EC2 인스턴스에서 EBS 볼륨으로 자체 관리형 Windows 파일 공유를 구성하면 서버 관리, 패치, 백업 등 운영 오버헤드가 크며, 관리형 서비스가 아닙니다.

E: FSx for OpenZFS는 NFS 프로토콜을 지원하며, Windows SMB 파일 공유 프로토콜을 기본 지원하지 않아 적합하지 않습니다.

