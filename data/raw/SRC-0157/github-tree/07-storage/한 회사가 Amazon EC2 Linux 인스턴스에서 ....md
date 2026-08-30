## Question

한 회사가 Amazon EC2 Linux 인스턴스에서 실행되는 애플리케이션을 테스트하고 있습니다. 단일 500GB Amazon Elastic Block Store(Amazon EBS) General Purpose SSD(gp2) 볼륨이 EC2 인스턴스에 연결되어 있습니다. 이 회사는 Auto Scaling 그룹의 여러 EC2 인스턴스에 애플리케이션을 배포합니다. 모든 인스턴스는 EBS 볼륨에 저장된 데이터에 액세스해야 합니다. 이 회사는 애플리케이션 코드에 상당한 변경을 도입하지 않는 고가용성 및 복원력 있는 솔루션이 필요합니다.
어떤 솔루션이 이러한 요구 사항을 충족할까요?

- [ ] A. NFS 서버 소프트웨어를 사용하는 EC2 인스턴스를 프로비저닝합니다. 인스턴스에 단일 500GB gp2 EBS 볼륨을 연결합니다.
- [ ] B. Amazon FSx for Windows File Server 파일 시스템을 프로비저닝합니다. 단일 가용성 영역 내에서 파일 시스템을 SMB 파일 저장소로 구성합니다.
- [ ] C. 250GB 프로비저닝 IOPS SSD EBS 볼륨 2개로 EC2 인스턴스를 프로비저닝합니다.
- [ ] D. Amazon Elastic File System(Amazon EFS) 파일 시스템을 프로비저닝합니다. 파일 시스템을 구성하여 General Purpose 성능 모드를 사용합니다.

## Answer

정답: D

## Explanation

Amazon EFS는 NFS 프로토콜 기반의 완전 관리형 파일 시스템으로, 여러 AZ의 EC2 인스턴스에서 동시에 마운트하여 공유 스토리지로 사용할 수 있습니다. General Purpose 성능 모드는 대부분의 워크로드에 적합한 지연 시간을 제공하며, Auto Scaling 그룹의 모든 인스턴스가 동일한 데이터에 접근할 수 있어 코드 변경이 최소화됩니다. 다중 AZ에 데이터를 자동 복제하여 고가용성과 내구성을 보장합니다.

오답 분석

A: EC2 인스턴스에 NFS 서버를 직접 구성하면 단일 장애 지점(SPOF)이 되어 고가용성이 부족하며, 서버 관리 부담이 큽니다.

B: FSx for Windows File Server는 SMB 프로토콜을 사용하며, Linux EC2 인스턴스에서는 NFS 기반 EFS가 더 적합합니다. 단일 AZ 구성은 고가용성 요구사항에 위배됩니다.

C: EBS 볼륨은 기본적으로 단일 EC2 인스턴스에만 연결되며(io1/io2 Multi-Attach는 제한적), 여러 인스턴스 간 데이터 공유가 불가능합니다.

