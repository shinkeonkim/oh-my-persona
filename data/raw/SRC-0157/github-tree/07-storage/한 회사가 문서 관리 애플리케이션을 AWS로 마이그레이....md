## Question

한 회사가 문서 관리 애플리케이션을 AWS로 마이그레이션하고 있습니다. 애플리케이션은 Linux 서버에서 실행됩니다.
회사는 애플리케이션을 Auto Scaling 그룹의 Amazon EC2 인스턴스로 마이그레이션합니다. 회사는 공유 스토리지 파일 시스템에 7TiB의 문서를 저장합니다. 외부 관계형 데이터베이스가 문서를 추적합니다.
문서는 한 번 저장되며 언제든지 참조를 위해 여러 번 검색할 수 있습니다. 회사는 마이그레이션 도중 애플리케이션을 수정할 수 없습니다. 스토리지 솔루션은 가용성이 높아야 하며 시간에 따른 확장을 지원해야 합니다.
이러한 요구 사항을 가장 비용 효율적으로 충족하는 솔루션은 무엇입니까?

- [ ] A. 향상된 네트워킹을 갖춘 EC2 인스턴스를 공유 NFS 스토리지 시스템으로 배포합니다. NFS 공유를 내보냅니다. Auto Scaling 그룹의 EC2 인스턴스에 NFS 공유를 탑재합니다.
- [ ] B. S3 Standard-Infrequent Access(S3 Standard-IA) 스토리지 클래스를 사용하는 Amazon S3 버킷을 생성합니다. Auto Scaling 그룹의 EC2 인스턴스에 S3 버킷을 탑재합니다.
- [ ] C. AWS Transfer for SFTP 및 Amazon S3 버킷을 사용하여 SFTP 서버 엔드포인트를 배포합니다. SFTP 서버에 연결하도록 Auto Scaling 그룹의 EC2 인스턴스를 구성합니다.
- [ ] D. 여러 가용 영역에 마운트 지점이 있는 Amazon EFS(Amazon Elastic File System) 파일 시스템을 생성합니다. EFS Standard-Infrequent Access(Standard-IA) 스토리지 클래스를 사용합니다. Auto Scaling 그룹의 EC2 인스턴스에 NFS 공유를 탑재합니다.

## Answer

정답: D

## Explanation

Amazon EFS Standard-IA(Infrequent Access)는 NFS 프로토콜을 기본 지원하여 Linux EC2 인스턴스에서 애플리케이션 수정 없이 직접 마운트할 수 있습니다. 여러 AZ에 마운트 포인트를 제공하여 고가용성을 보장하며, 자동으로 확장됩니다. 문서가 한 번 저장되고 간헐적으로 참조를 위해 검색되는 액세스 패턴에서 Standard-IA 스토리지 클래스는 Standard보다 스토리지 비용이 최대 92% 저렴하여(액세스 비용은 더 높지만) 비용 효율적입니다.

오답 분석

A: EC2 인스턴스를 NFS 서버로 구성하면 해당 인스턴스가 단일 장애 지점(SPOF)이 되며, 서버 관리, 패치, 장애 복구 등의 운영 오버헤드가 상당합니다. EFS는 완전관리형 서비스로 이러한 관리 부담을 제거합니다.

B: Amazon S3 버킷은 EC2 인스턴스에 POSIX 파일 시스템으로 직접 마운트할 수 없습니다. S3는 객체 스토리지로 파일 시스템 시맨틱스를 제공하지 않으므로, 기존 파일 기반 애플리케이션을 수정하지 않고는 사용할 수 없어 마이그레이션 중 애플리케이션 수정 불가 조건에 위배됩니다.

C: AWS Transfer for SFTP는 S3 또는 EFS에 대한 SFTP 기반 파일 전송 서비스이며, 공유 파일 시스템을 제공하지 않습니다. 애플리케이션이 NFS 파일 시스템으로 직접 파일에 접근하려면 별도의 코드 수정이 필요합니다.

