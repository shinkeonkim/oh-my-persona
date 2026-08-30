## Question

한 회사가 동일한 AWS 리전의 여러 가용 영역에 걸쳐 있는 Amazon EC2 인스턴스에서 애플리케이션을 실행합니다. EC2 인스턴스는 모든 인스턴스에 마운트된 Amazon Elastic File System(Amazon EFS) 볼륨을 공유합니다. EFS 볼륨에는 설치 미디어, 타사 파일, 인터페이스 파일 및 기타 일회성 파일과 같은 다양한 파일이 저장됩니다. 회사는 일부 EFS 파일에 자주 액세스하며 이러한 파일을 빠르게 검색해야 합니다. 반면, 다른 파일에는 거의 액세스하지 않습니다. EFS 볼륨의 크기는 수 테라바이트입니다. 회사는 Amazon EFS의 스토리지 비용을 최적화해야 합니다.
가장 적은 노력으로 이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. 파일을 Amazon S3로 이동합니다. 파일을 S3 Glacier Flexible Retrieval로 이동하는 수명 주기 정책을 설정합니다.
- [ ] B. EFS 파일에 수명 주기 정책을 적용하여 파일을 EFS Infrequent Access로 이동합니다.
- [ ] C. 파일을 Amazon Elastic Block Store(Amazon EBS) Cold HDD 볼륨(sc1)으로 이동합니다.
- [ ] D. 파일을 Amazon S3로 이동합니다. 거의 사용되지 않는 파일을 S3 Glacier Deep Archive로 이동하는 수명 주기 정책을 설정합니다.

## Answer

정답: B

## Explanation

EFS 수명 주기 정책(Lifecycle Policy)을 설정하면 일정 기간(7/14/30/60/90일) 접근하지 않은 파일이 자동으로 EFS Infrequent Access(IA) 스토리지 클래스로 이동됩니다. EFS IA는 Standard보다 최대 92% 저렴하며, 파일 접근 시 자동으로 Standard로 복귀할 수 있습니다. 기존 EFS 파일 시스템에 정책만 설정하면 되므로 데이터 마이그레이션이나 애플리케이션 변경 없이 비용을 최적화합니다.

오답 분석

A: S3로 파일을 이동하면 기존 EFS 마운트 방식이 변경되어 애플리케이션 수정이 필요하며, Glacier 전환 시 즉각적 파일 접근이 불가능합니다.

C: EBS Cold HDD(sc1)는 단일 EC2 인스턴스에만 연결 가능하여 여러 인스턴스 간 공유가 불가능하고, 대규모 데이터 마이그레이션 노력이 필요합니다.

D: S3로 이동 후 Glacier Deep Archive로 전환하면 데이터 검색에 12~48시간이 소요되어 즉각적 접근이 불가능하며, 마이그레이션 노력이 큽니다.

