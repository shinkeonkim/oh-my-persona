## Question

한 회사가 최근 온프레미스 Oracle 데이터베이스 워크로드를 Amazon EC2 메모리 최적화 Linux 인스턴스에서 실행하기 위해 리프트 앤 시프트 마이그레이션을 수행했습니다. EC2 Linux 인스턴스는 64,000 IOPS의 1TB Provisioned IOPS SSD (io1) EBS 볼륨을 사용합니다. 마이그레이션 후 데이터베이스 스토리지 성능은 온프레미스 데이터베이스 성능보다 느립니다. 어떤 솔루션이 스토리지 성능을 개선할까요?

- [ ] A. Provisioned IOPS SSD(io1) EBS 볼륨을 더 추가합니다. OS 명령을 사용하여 논리 볼륨 관리(LVM) 스트라이프를 만듭니다.
- [ ] B. 프로비저닝된 IOPS SSD(io1) EBS 볼륨을 64,000 IOPS 이상으로 늘립니다.
- [ ] C. Provisioned IOPS SSD(io1) EBS 볼륨의 크기를 2TB로 늘립니다.
- [ ] D. EC2 Linux 인스턴스를 스토리지 최적화 인스턴스 유형으로 변경합니다. Provisioned IOPS SSD(io1) EBS 볼륨은 변경하지 마십시오.

## Answer

정답: A

## Explanation

여러 io1 EBS 볼륨을 추가하고 OS 수준에서 LVM(Logical Volume Manager) 스트라이프를 구성하면 I/O를 여러 볼륨에 분산하여 단일 볼륨의 IOPS 한계(64,000)를 초과하는 총 성능을 달성할 수 있습니다. 이는 온프레미스에서 여러 디스크를 RAID 0으로 구성하는 것과 동일한 원리이며, 볼륨당 64,000 IOPS × N개 볼륨의 총 IOPS를 제공합니다.

오답 분석

B: 단일 io1 볼륨의 최대 프로비저닝 IOPS는 64,000(io2 Block Express는 256,000)이므로, 이미 io1의 최대값에 도달하여 더 이상 단일 볼륨에서 늘릴 수 없습니다.

C: 볼륨 크기를 2TB로 늘리는 것은 저장 용량만 증가시키며, 이미 64,000 IOPS로 프로비저닝되어 있으므로 IOPS 성능 개선에 영향이 없습니다.

D: 스토리지 최적화 인스턴스는 로컬 NVMe SSD를 제공하지만 데이터 영속성이 인스턴스 수명에 종속되며, EBS 볼륨 자체의 IOPS 병목을 해결하지 못합니다.

