## Question

한 회사에서 AWS에서 호스팅되는 서비스 솔루션으로서 고성능 컴퓨팅(HPC) 워크로드를 구축할 계획입니다. 16개의 Amazon EC2 Linux 인스턴스 그룹은 노드 간 통신을 위해 가능한 가장 낮은 지연 시간이 필요합니다. 인스턴스에는 고성능 스토리지를 위한 공유 블록 장치 볼륨도 필요합니다.
이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. 클러스터 배치 그룹을 사용합니다. Amazon EBS 다중 연결을 사용하여 단일 프로비저닝된 IOPS SSD Amazon Elastic Block Store(Amazon EBS) 볼륨을 모든 인스턴스에 연결합니다.
- [ ] B. 클러스터 배치 그룹을 사용합니다. Amazon Elastic File System(Amazon EFS)을 사용하여 인스턴스 간에 공유 파일 시스템을 생성합니다.
- [ ] C. 파티션 배치 그룹을 사용합니다. Amazon Elastic File System(Amazon EFS)을 사용하여 인스턴스 간에 공유 파일 시스템을 생성합니다.
- [ ] D. 스프레드 배치 그룹을 사용합니다. Amazon EBS 다중 연결을 사용하여 단일 프로비저닝된 IOPS SSD Amazon Elastic Block Store(Amazon EBS) 볼륨을 모든 인스턴스에 연결합니다.

## Answer

정답: A

## Explanation

클러스터 배치 그룹(Cluster Placement Group)과 Amazon EBS Multi-Attach를 사용하여 단일 Provisioned IOPS SSD 볼륨을 모든 인스턴스에 연결하는 것이 이 요구 사항을 충족합니다. 클러스터 배치 그룹은 16개의 인스턴스를 동일한 가용 영역 내에서 물리적으로 가까운 위치에 배치하여 노드 간 최저 지연 시간을 제공합니다. EBS Multi-Attach(io1/io2 볼륨)는 동일 AZ 내 최대 16개 Nitro 기반 인스턴스에 단일 블록 볼륨을 동시에 연결하여 공유 블록 스토리지를 제공합니다.

오답 분석

B: 클러스터 배치 그룹은 최저 지연 시간을 제공하지만, Amazon EFS는 파일 시스템 수준 공유이며 '공유 블록 장치 볼륨' 요구 사항을 충족하지 않습니다. EFS는 블록 장치가 아니라 NFS 파일 시스템입니다.

C: 파티션 배치 그룹(Partition Placement Group)은 대규모 분산 워크로드의 장애 격리를 위한 것이며, 클러스터 배치 그룹처럼 인스턴스 간 최저 지연 시간을 보장하지 않습니다.

D: 스프레드 배치 그룹(Spread Placement Group)은 인스턴스를 서로 다른 하드웨어에 분산하여 장애 격리에 초점을 맞추며, 최저 지연 시간 요구 사항에 적합하지 않습니다. 또한 가용 영역당 최대 7개 인스턴스만 지원하여 16개 인스턴스 요구 사항을 충족할 수 없습니다.

