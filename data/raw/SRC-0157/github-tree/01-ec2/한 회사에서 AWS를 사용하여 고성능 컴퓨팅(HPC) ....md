## Question

한 회사에서 AWS를 사용하여 고성능 컴퓨팅(HPC) 워크로드와 분석 워크로드를 실행하려고 합니다. 이 회사는 Amazon EC2 인스턴스에서 HPC 워크로드를 실행합니다. 워크로드에는 초당 수백만 개의 입출력 작업(IOPS)으로 확장할 수 있는 고성능 파일 시스템이 필요합니다. 이러한 요구 사항을 충족하는 단계 조합은 무엇입니까? (2개 선택)

- [ ] A. Amazon Elastic File System(Amazon EFS)을 고성능 파일 시스템으로 사용합니다.
- [ ] B. Amazon FSx for Lustre를 고성능 파일 시스템으로 사용합니다.
- [ ] C. Amazon EC2 인스턴스의 자동 확장 그룹을 만듭니다. 예약 인스턴스를 사용합니다. 분산 배치 그룹을 구성합니다. AWS Batch를 사용하여 분석 워크로드를 실행합니다.
- [ ] D. Mountpoint for Amazon S3를 고성능 파일 시스템으로 사용합니다.
- [ ] E. Amazon EC2 인스턴스의 자동 확장 그룹을 만듭니다. 온디맨드 인스턴스, 예약 인스턴스, 스팟 인스턴스를 혼합하여 사용합니다. 클러스터 배치 그룹을 구성합니다. Amazon EMR을 사용하여 분석 워크로드를 실행합니다.

## Answer

정답: B, E

## Explanation

B(Amazon FSx for Lustre)는 POSIX 호환 고성능 병렬 파일 시스템으로 초당 수백만 IOPS로 확장 가능하며, HPC 및 기계 학습 워크로드에 최적화되어 있습니다. E(혼합 인스턴스 유형 + 클러스터 배치 그룹 + Amazon EMR)에서 클러스터 배치 그룹은 인스턴스를 동일 AZ 내 물리적으로 가까이 배치하여 저지연/고대역폭 네트워크 통신을 보장합니다. EMR은 Apache Spark, Hadoop 등을 활용한 대규모 데이터 분석에 특화됩니다.

오답 분석

A: Amazon EFS는 범용 NFS 파일 시스템으로, FSx for Lustre의 수백만 IOPS 수준의 성능을 제공하지 못합니다.

C: 분산(Spread) 배치 그룹은 인스턴스를 서로 다른 하드웨어에 분산하여 상관관계 장애를 줄이는 목적이며, HPC에 필요한 저지연 인스턴스 간 통신에는 클러스터 배치 그룹이 필요합니다.

D: Mountpoint for Amazon S3는 S3에 POSIX 파일 시스템 접근을 제공하지만, 객체 스토리지 특성상 HPC에 필요한 수백만 IOPS의 랜덤 I/O 성능을 지원할 수 없습니다.

