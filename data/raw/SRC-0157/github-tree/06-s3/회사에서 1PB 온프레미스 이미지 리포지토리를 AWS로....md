## Question

회사에서 1PB 온프레미스 이미지 리포지토리를 AWS로 마이그레이션하려고 합니다. 이미지는 서버리스 웹 애플리케이션에서 사용됩니다. 리포지토리에 저장된 이미지는 거의 액세스되지 않지만 즉시 사용할 수 있어야 합니다. 또한 미사용 이미지를 암호화하고 우발적인 삭제로부터 보호해야 합니다.
어떤 솔루션이 이러한 요구 사항을 충족합니까?

- [ ] A. 클라이언트 측 암호화를 구현하고 이미지를 Amazon S3 Glacier 볼트에 저장합니다. 우발적인 삭제를 방지하기 위해 볼트 잠금을 설정합니다.
- [ ] B. S3 Standard-Infrequent Access(S3 Standard-IA) 스토리지 클래스의 Amazon S3 버킷에 이미지를 저장합니다. S3 버킷에서 버전 관리, 기본 암호화 및 MFA 삭제를 활성화합니다.
- [ ] C. Amazon FSx for Windows File Server 파일 공유에 이미지를 저장합니다. AWS Key Management Service(AWS KMS) 고객 마스터 키(CMK)를 사용하여 파일 공유의 이미지를 암호화하도록 Amazon FSx 파일 공유를 구성합니다. 우발적인 삭제를 방지하려면 이미지에 NTFS 권한 집합을 사용합니다.
- [ ] D. Infrequent Access 스토리지 클래스의 Amazon Elastic File System(Amazon EFS) 파일 공유에 이미지를 저장합니다. AWS Key Management Service(AWS KMS) 고객 마스터 키(CMK)를 사용하여 파일 공유의 이미지를 암호화하도록 EFS 파일 공유를 구성합니다. 우발적인 삭제를 방지하려면 이미지에 NFS 권한 집합을 사용합니다.

## Answer

정답: B

## Explanation

S3 Standard-IA는 거의 액세스하지 않지만 즉시 사용 가능해야 하는 1PB 이미지 리포지토리에 적합합니다. 밀리초 단위의 첫 바이트 접근 시간을 제공하면서 S3 Standard보다 스토리지 비용이 약 45% 저렴합니다. S3 버전 관리를 활성화하면 우발적 삭제나 덮어쓰기 시 이전 버전에서 즉시 복구할 수 있습니다. S3 기본 암호화를 활성화하면 업로드되는 모든 이미지가 SSE-S3(AES-256) 또는 SSE-KMS로 자동 암호화되어 미사용(at-rest) 암호화 요구사항을 충족합니다. MFA Delete를 활성화하면 객체 버전 삭제나 버전 관리 비활성화 시 MFA 디바이스 인증이 필수적으로 요구되어 우발적 삭제를 강력하게 방지합니다. MFA Delete는 버킷 소유자(루트 계정)만 활성화/비활성화할 수 있습니다.

오답 분석

A: S3 Glacier 볼트 잠금은 WORM(Write Once Read Many) 정책을 적용하지만, Glacier는 밀리초 단위의 즉시 접근이 불가능합니다. Glacier Flexible Retrieval의 긴급 검색도 1-5분, 표준 검색은 3-5시간이 소요되어 '즉시 사용 가능(immediately available)' 요구사항을 충족하지 못합니다.

C: Amazon FSx for Windows File Server는 Windows 기반 SMB 프로토콜을 사용하는 파일 공유이며, 서버리스 웹 애플리케이션(Lambda, API Gateway 등)과의 직접 통합이 제한적입니다. 또한 FSx 인스턴스 프로비저닝과 관리가 필요하고, 1PB 규모에서 S3보다 비용이 훨씬 높습니다.

D: Amazon EFS Infrequent Access는 NFS 기반 공유 파일 시스템으로 가능한 옵션이지만, NFS 권한(chmod/chown)으로는 우발적 삭제를 완전히 방지하기 어렵고, 루트 권한이 있으면 삭제 가능합니다. S3의 MFA Delete + 버전 관리 조합이 훨씬 강력한 삭제 보호를 제공하며, 1PB 규모에서 EFS보다 S3 Standard-IA가 비용 효율적입니다.

