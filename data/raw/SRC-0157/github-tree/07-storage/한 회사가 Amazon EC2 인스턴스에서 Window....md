## Question

한 회사가 Amazon EC2 인스턴스에서 Windows 기반 전자상거래 애플리케이션을 실행합니다. 이 애플리케이션의 거래 속도가 매우 높습니다. 이 회사는 각 EC2 인스턴스에 대해 200,000 IOPS를 제공할 수 있는 내구성 있는 스토리지 솔루션이 필요합니다.
이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. Provisioned IOPS SSD(io2) Block Express Amazon Elastic Block Store(Amazon EBS) 볼륨이 연결된 EC2 인스턴스에 애플리케이션을 호스팅합니다.
- [ ] B. Amazon EMR 클러스터에 애플리케이션을 설치합니다. 범용 SSD(gp3) Amazon Elastic Block Store(Amazon EBS) 볼륨이 있는 Hadoop 분산 파일 시스템(HDFS)을 사용합니다.
- [ ] C. 애플리케이션을 실행하는 EC2 인스턴스에서 Amazon FSx for Lustre를 공유 스토리지로 사용합니다.
- [ ] D. SSD 인스턴스 스토어 볼륨과 범용 SSD(gp3) Amazon Elastic Block Store(Amazon EBS) 볼륨이 연결된 EC2 인스턴스에 애플리케이션을 호스팅합니다.

## Answer

정답: A

## Explanation

Provisioned IOPS SSD(io2) Block Express EBS 볼륨은 최대 256,000 IOPS를 제공하여 200,000 IOPS 요구사항을 충족할 수 있습니다. Block Express는 차세대 EBS 아키텍처로 매우 높은 IOPS와 내구성을 제공합니다.

오답 분석

B: EMR 클러스터의 HDFS와 gp3 EBS 볼륨 조합은 분석 워크로드에 적합하지만, 200,000 IOPS를 제공하기 어렵고 e-커머스 트랜잭션 애플리케이션에 적합하지 않습니다.

C: FSx for Lustre는 고성능 파일 시스템이지만, Windows 기반 e-커머스 애플리케이션에 적합하지 않으며 블록 스토리지가 아닙니다.

D: SSD 인스턴스 스토어는 휘발성이므로 내구성이 없고, gp3 EBS는 최대 16,000 IOPS로 200,000 IOPS 요구사항을 충족하지 못합니다.

