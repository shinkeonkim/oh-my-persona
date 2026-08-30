## Question

한 회사는 CIFS 및 NFS 파일 공유를 위해 기본 AWS 지역에서 NetApp ONTAP용 Amazon FSx를 사용합니다. Amazon EC2 인스턴스에서 실행되는 애플리케이션은 파일 공유에 액세스합니다. 회사는 보조 지역에 스토리지 재해 복구(DR) 솔루션이 필요합니다. 보조 리전에 복제된 데이터는 기본 리전과 동일한 프로토콜을 사용하여 액세스해야 합니다.
최소한의 운영 오버헤드로 이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. AWS Lambda 함수를 생성하여 Amazon S3 버킷에 데이터를 복사합니다. S3 버킷을 보조 리전에 복제합니다.
- [ ] B. AWS Backup을 사용하여 FSx for ONTAP 볼륨의 백업을 생성합니다. 볼륨을 보조 리전에 복사합니다. 백업에서 ONTAP 인스턴스용 새 FSx를 생성합니다.
- [ ] C. 보조 지역에 FSx for ONTAP 인스턴스를 생성합니다. NetApp SnapMirror를 사용하여 기본 지역에서 보조 지역으로 데이터를 복제합니다.
- [ ] D. Amazon Elastic File System(Amazon EFS) 볼륨을 생성합니다. 현재 데이터를 볼륨으로 마이그레이션합니다. 볼륨을 보조 리전에 복제합니다.

## Answer

정답: C

## Explanation

보조 리전에 FSx for NetApp ONTAP 인스턴스를 생성하고 NetApp SnapMirror를 사용하면, 기본 리전의 ONTAP 파일 시스템에서 보조 리전으로 블록 레벨의 효율적인 증분 복제가 수행됩니다. SnapMirror는 FSx for ONTAP의 기본 내장 복제 기능으로, 별도의 도구나 스크립트 없이 설정만으로 교차 리전 복제가 가능합니다. 보조 리전의 ONTAP도 CIFS(SMB)와 NFS를 모두 지원하므로 기본 리전과 동일한 프로토콜로 데이터에 접근할 수 있어 DR 요구사항을 완벽히 충족합니다.

오답 분석

A: Lambda 함수로 S3 버킷에 데이터를 복사하면 ONTAP의 CIFS/NFS 파일 시스템 프로토콜이 아닌 S3 객체 스토리지 API로만 접근 가능합니다. 보조 리전에서 '기본 리전과 동일한 프로토콜' 요구사항을 충족하지 못합니다.

B: AWS Backup으로 FSx for ONTAP 볼륨의 백업을 생성하고 보조 리전에 복사하는 방식은 시점 기반 백업이므로, 연속적인 실시간 복제인 SnapMirror보다 RPO가 높을 수 있습니다. 또한 백업에서 새 인스턴스를 생성하는 복구 시간이 더 깁니다.

D: Amazon EFS는 NFS 프로토콜만 지원하며 CIFS(SMB)를 지원하지 않습니다. 기본 리전에서 CIFS와 NFS를 모두 사용하므로, NFS만 지원하는 EFS로는 동일한 프로토콜 접근 요구사항을 충족하지 못합니다.

