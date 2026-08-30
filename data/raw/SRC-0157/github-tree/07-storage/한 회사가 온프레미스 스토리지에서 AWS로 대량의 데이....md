## Question

한 회사가 온프레미스 스토리지에서 AWS로 대량의 데이터를 마이그레이션하고 있습니다. 동일한 AWS 리전에 있는 Windows, Mac 및 Linux 기반 Amazon EC2 인스턴스는 SMB 및 NFS 스토리지 프로토콜을 사용하여 데이터에 액세스합니다. 회사는 정기적으로 데이터의 일부에 액세스합니다. 회사는 나머지 데이터에 드물게 액세스합니다.
회사는 데이터를 호스팅하기 위한 솔루션을 설계해야 합니다.
최소한의 운영 오버헤드로 이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. EFS Intelligent-Tiering을 사용하는 Amazon Elastic File System(Amazon EFS) 볼륨을 생성합니다. AWS DataSync를 사용하여 데이터를 EFS 볼륨으로 마이그레이션합니다.
- [ ] B. ONTAP 인스턴스용 Amazon FSx를 생성합니다. 자동 계층화 정책을 사용하는 루트 볼륨이 있는 FSx for ONTAP 파일 시스템을 생성합니다. 데이터를 FSx for ONTAP 볼륨으로 마이그레이션합니다.
- [ ] C. S3 Intelligent-Tiering을 사용하는 Amazon S3 버킷을 생성합니다. AWS Storage Gateway Amazon S3 파일 게이트웨이를 사용하여 데이터를 S3 버킷으로 마이그레이션합니다.
- [ ] D. OpenZFS 파일 시스템용 Amazon FSx를 생성합니다. 데이터를 새 볼륨으로 마이그레이션합니다.

## Answer

정답: B

## Explanation

Amazon FSx for NetApp ONTAP은 SMB와 NFS를 동시에 지원하는 다중 프로토콜 파일 시스템으로, Windows, Mac, Linux EC2 인스턴스에서 모두 네이티브 프로토콜로 접근할 수 있습니다. 자동 계층화(Auto Tiering) 정책은 자주 액세스하는 데이터를 고성능 SSD 계층에 유지하고, 비활성 데이터를 저비용 용량 풀(Capacity Pool) 스토리지로 자동 이동하여 비용을 최적화합니다. 완전관리형 서비스이므로 운영 오버헤드가 최소화됩니다.

오답 분석

A: Amazon EFS는 NFS 프로토콜만 지원하며 SMB는 지원하지 않으므로, Windows EC2 인스턴스에서 네이티브 프로토콜로 접근할 수 없습니다. 모든 플랫폼에서의 접근이 필요한 이 시나리오에서는 다중 프로토콜 지원이 필수입니다.

C: S3 + Storage Gateway 파일 게이트웨이 조합은 온프레미스 환경을 위한 것이며, AWS 내 EC2 인스턴스에서의 직접 다중 프로토콜 접근에는 적합하지 않습니다. 또한 SMB와 NFS를 동시에 동일한 데이터에 대해 제공하기 어렵습니다.

D: FSx for OpenZFS는 NFS 프로토콜만 지원하며 SMB를 지원하지 않습니다. Windows 인스턴스에서 SMB로 접근해야 하는 요구사항을 충족하지 못합니다.

