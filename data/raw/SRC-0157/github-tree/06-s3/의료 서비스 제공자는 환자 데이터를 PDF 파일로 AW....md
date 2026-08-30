## Question

의료 서비스 제공자는 환자 데이터를 PDF 파일로 AWS에 저장할 계획입니다. 규정을 준수하기 위해 회사는 데이터를 암호화하고 여러 위치에 파일을 저장해야 합니다. 모든 환경에서 데이터에 즉시 액세스할 수 있어야 합니다.

- [ ] A. Amazon S3 버킷에 파일을 저장합니다. Standard 스토리지 클래스를 사용합니다. 버킷에서 Amazon S3 관리 키(SSE-S3)로 서버 측 암호화를 활성화합니다. 버킷에서 리전 간 복제를 구성합니다.
- [ ] B. Amazon Elastic File System(Amazon EFS) 볼륨에 파일을 저장합니다. AWS KMS 관리 키를 사용하여 EFS 볼륨을 암호화합니다. AWS DataSync를 사용하여 EFS 볼륨을 두 번째 AWS 리전으로 복제합니다.
- [ ] C. Amazon Elastic Block Store(Amazon EBS) 볼륨에 파일을 저장합니다. AWS Backup을 구성하여 볼륨을 정기적으로 백업합니다. AWS KMS 키를 사용하여 백업을 암호화합니다.
- [ ] D. Amazon S3 버킷에 파일을 저장합니다. S3 Glacier Flexible Retrieval 스토리지 클래스를 사용합니다. 파일을 업로드하기 전에 모든 PDF 파일이 클라이언트 측 암호화를 사용하여 암호화되었는지 확인합니다. 버킷에서 크로스 리전 복제를 구성합니다.

## Answer

정답: A

## Explanation

Amazon S3 Standard 스토리지 클래스에 파일을 저장하면 즉각적인 접근이 가능하고, SSE-S3 서버 측 암호화로 규정 준수 요건을 충족하며, 교차 리전 복제(CRR)를 통해 여러 위치에 데이터를 저장할 수 있습니다. 이 조합이 최소한의 운영 오버헤드로 모든 요구사항을 충족합니다.

오답 분석

B: Amazon EFS와 AWS DataSync 조합은 작동하지만, PDF 파일 저장에 EFS를 사용하는 것은 S3보다 비용이 높고 운영 오버헤드가 더 큽니다.

C: Amazon EBS 볼륨은 단일 가용 영역에 바인딩되어 여러 위치에 저장하는 요구사항을 충족하지 못하며, AWS Backup은 복제가 아닌 백업 솔루션입니다.

D: S3 Glacier Flexible Retrieval은 즉각적인 접근이 불가능하여 '모든 환경에서 즉시 접근 가능' 요구사항을 충족하지 못합니다.

