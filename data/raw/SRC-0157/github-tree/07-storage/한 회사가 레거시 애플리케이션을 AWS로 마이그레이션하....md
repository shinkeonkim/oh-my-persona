## Question

한 회사가 레거시 애플리케이션을 AWS로 마이그레이션하려고 계획하고 있습니다. 이 애플리케이션은 현재 NFS를 사용하여 온프레미스 스토리지 솔루션과 통신하여 애플리케이션 데이터를 저장합니다. 이 애플리케이션을 수정하여 이 목적을 위해 NFS 이외의 다른 통신 프로토콜을 사용할 수 없습니다.
솔루션 아키텍트는 마이그레이션 후 어떤 스토리지 솔루션을 사용하도록 권장해야 합니까?

- [ ] A. AWS DataSync
- [ ] B. Amazon Elastic Block Store(Amazon EBS)
- [ ] C. Amazon Elastic File System(Amazon EFS)
- [ ] D. Amazon EMR 파일 시스템(Amazon EMRFS)

## Answer

정답: C

## Explanation

Amazon EFS(Elastic File System)는 NFSv4 프로토콜을 기본 지원하는 완전 관리형 파일 스토리지 서비스입니다. 레거시 애플리케이션이 NFS만 사용할 수 있으므로, EFS는 코드 변경 없이 기존 NFS 마운트 명령으로 직접 연결할 수 있는 유일한 적합한 AWS 스토리지 솔루션입니다. 탄력적으로 자동 확장되며, 다중 AZ에 데이터를 복제하여 고가용성과 내구성을 제공합니다.

오답 분석

A: AWS DataSync는 온프레미스와 AWS 간, 또는 AWS 서비스 간 데이터 전송을 자동화하는 서비스이며, 애플리케이션이 직접 마운트하여 사용하는 스토리지 솔루션이 아닙니다.

B: Amazon EBS는 블록 스토리지로 NFS 프로토콜을 지원하지 않으며, 기본적으로 단일 EC2 인스턴스에만 연결됩니다.

D: Amazon EMRFS는 EMR 클러스터에서 S3를 HDFS처럼 사용하기 위한 파일 시스템이며, NFS 프로토콜을 지원하지 않아 범용 파일 공유에 적합하지 않습니다.

