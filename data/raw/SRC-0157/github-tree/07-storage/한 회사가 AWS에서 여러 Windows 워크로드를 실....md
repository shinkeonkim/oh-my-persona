## Question

한 회사가 AWS에서 여러 Windows 워크로드를 실행합니다. 회사 직원은 두 개의 Amazon EC2 인스턴스에서 호스팅되는 Windows 파일 공유를 사용합니다. 파일 공유는 서로 간에 데이터를 동기화하고 복제본을 유지합니다. 회사는 사용자가 현재 파일에 액세스하는 방식을 보존하는 가용성이 높고 내구성이 뛰어난 스토리지 솔루션을 원합니다.
솔루션 설계자는 이러한 요구 사항을 충족하기 위해 무엇을 해야 합니까?

- [ ] A. 모든 데이터를 Amazon S3로 마이그레이션합니다. 사용자가 파일에 액세스할 수 있도록 IAM 인증을 설정합니다.
- [ ] B. Amazon S3 파일 게이트웨이를 설정합니다. 기존 EC2 인스턴스에 S3 File Gateway를 탑재합니다.
- [ ] C. 다중 AZ 구성을 사용하여 파일 공유 환경을 Windows 파일 서버용 Amazon FSx로 확장합니다. 모든 데이터를 FSx for Windows File Server로 마이그레이션합니다.
- [ ] D. 다중 AZ 구성을 사용하여 파일 공유 환경을 Amazon Elastic File System(Amazon EFS)으로 확장합니다. 모든 데이터를 Amazon EFS로 마이그레이션합니다.

## Answer

정답: C

## Explanation

Amazon FSx for Windows File Server는 Multi-AZ 구성으로 두 개의 가용 영역에 걸쳐 데이터를 동기적으로 복제하여 고가용성과 내구성을 제공합니다. SMB 프로토콜을 기본 지원하여 기존 Windows 파일 공유 사용자가 동일한 방식으로 파일에 접근할 수 있으며, 두 EC2 인스턴스에서 별도로 데이터를 동기화하고 복제본을 유지하는 수동 작업을 제거합니다. Active Directory 통합도 지원하여 기존 인증 체계를 유지합니다.

오답 분석

A: S3로 모든 데이터를 마이그레이션하고 IAM 인증으로 접근하면, 기존 Windows 파일 공유의 SMB 프로토콜 기반 접근 방식이 완전히 변경됩니다. '사용자가 현재 파일에 액세스하는 방식 보존'이라는 요구사항에 위배됩니다.

B: S3 파일 게이트웨이를 기존 EC2 인스턴스에 마운트하면 온프레미스 캐시를 통한 접근이 가능하지만, AWS 클라우드 내 EC2 인스턴스 간 파일 공유에는 FSx for Windows File Server가 더 직접적이고 적합한 솔루션입니다.

D: Amazon EFS는 NFS 프로토콜만 지원하며, Windows 파일 공유에 사용되는 SMB 프로토콜과 호환되지 않습니다. Windows 사용자의 기존 파일 접근 방식을 보존하려면 SMB를 지원하는 FSx for Windows가 필요합니다.

