## Question

한 회사는 최근 애플리케이션을 AWS로 마이그레이션했습니다. 애플리케이션은 여러 가용 영역에 걸쳐 Auto Scaling 그룹의 Amazon EC2 Linux 인스턴스에서 실행됩니다. 애플리케이션은 EFS Standard-Infrequent Access 스토리지를 사용하는 Amazon Elastic File System(Amazon EFS) 파일 시스템에 데이터를 저장합니다. 애플리케이션은 회사의 파일을 인덱싱합니다. 인덱스는 Amazon RDS 데이터베이스에 저장됩니다.
회사는 일부 애플리케이션 및 서비스 변경을 통해 스토리지 비용을 최적화해야 합니다.
이러한 요구 사항을 가장 비용 효율적으로 충족하는 솔루션은 무엇입니까?

- [ ] A. Intelligent-Tiering 수명주기 정책을 사용하는 Amazon S3 버킷을 생성합니다. 모든 파일을 S3 버킷에 복사합니다. Amazon S3 API를 사용하여 파일을 저장하고 검색하도록 애플리케이션을 업데이트합니다.
- [ ] B. Windows 파일 서버 파일 공유용 Amazon FSx를 배포합니다. CIFS 프로토콜을 사용하여 파일을 저장하고 검색하도록 애플리케이션을 업데이트합니다.
- [ ] C. OpenZFS 파일 시스템 공유용 Amazon FSx를 배포합니다. 새 탑재 지점을 사용하여 파일을 저장하고 검색하도록 애플리케이션을 업데이트합니다.
- [ ] D. S3 Glacier Flexible Retrieval을 사용하는 Amazon S3 버킷을 생성합니다. 모든 파일을 S3 버킷에 복사합니다. Amazon S3 API를 사용하여 파일을 표준 검색으로 저장하고 검색하도록 애플리케이션을 업데이트합니다.

## Answer

정답: A

## Explanation

Amazon S3에 Intelligent-Tiering 수명 주기 정책을 적용하면 파일의 액세스 빈도에 따라 자동으로 비용이 최적화됩니다. EFS Standard-IA보다 S3가 대규모 파일 저장에 더 비용 효율적이며, Intelligent-Tiering은 인덱싱에 자주 사용되는 파일은 빈번한 액세스 계층에, 거의 사용되지 않는 파일은 저렴한 계층에 자동 배치합니다.

오답 분석

B: Amazon FSx for Windows File Server는 Linux 인스턴스에서 CIFS 프로토콜을 사용하는 것이 부적절하며, FSx는 S3보다 비용이 높습니다.

C: Amazon FSx for OpenZFS는 고성능 파일 시스템이지만, S3보다 비용이 높아 스토리지 비용 최적화에 적합하지 않습니다.

D: S3 Glacier Flexible Retrieval은 즉시 접근이 불가능하여 애플리케이션이 파일을 즉시 인덱싱하고 검색하는 데 적합하지 않습니다.

