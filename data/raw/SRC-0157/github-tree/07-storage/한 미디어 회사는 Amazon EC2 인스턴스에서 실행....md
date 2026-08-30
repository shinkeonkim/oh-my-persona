## Question

한 미디어 회사는 Amazon EC2 인스턴스에서 실행되는 비디오 변환 도구를 사용하고 있습니다. 비디오 변환 도구는 Windows EC2 인스턴스와 Linux EC2 인스턴스의 조합에서 실행됩니다. 각 비디오 파일의 크기는 수십 기가바이트입니다. 비디오 변환 도구는 가능한 한 짧은 시간 안에 비디오 파일을 처리해야 합니다. 회사는 비디오 변환 도구가 호스팅되는 모든 EC2 인스턴스에 마운트할 수 있는 단일 중앙 집중식 파일 저장 솔루션이 필요합니다.
어떤 솔루션이 이러한 요구 사항을 충족할 수 있을까요?

- [ ] A. 하드 디스크 드라이브(HDD) 스토리지가 있는 Amazon FSx for Windows File Server를 배포합니다.
- [ ] B. 솔리드 스테이트 드라이브(SSD) 스토리지가 있는 Amazon FSx for Windows File Server를 배포합니다.
- [ ] C. 최대 I/O 성능 모드로 Amazon Elastic File System(Amazon EFS)를 배포합니다.
- [ ] D. 일반 목적 성능 모드로 Amazon Elastic File System(Amazon EFS)를 배포합니다.

## Answer

정답: B

## Explanation

Amazon FSx for Windows File Server는 SSD 스토리지로 고성능을 제공하며, Windows와 Linux EC2 인스턴스 모두에서 마운트할 수 있는 중앙 집중식 파일 스토리지입니다. 수십 기가바이트의 비디오 파일을 가장 빠른 시간에 처리하기 위해 SSD 기반 고성능 공유 스토리지가 적합합니다.

오답 분석

A: FSx for Windows File Server의 HDD 스토리지는 SSD보다 성능이 낮아 가장 짧은 시간에 처리해야 하는 요구사항에 부적합합니다.

C: Amazon EFS Max I/O 모드는 높은 처리량을 제공하지만, NFS 프로토콜을 주로 지원합니다. Windows EC2 인스턴스에서 NFS 클라이언트를 통해 마운트할 수는 있지만, 이는 추가 구성이 필요하며 Windows/Linux 혼합 환경에서 FSx for Windows File Server의 네이티브 SMB 프로토콜 지원보다 덜 원활합니다.

D: Amazon EFS General Purpose 모드도 NFS 프로토콜을 주로 지원하여 Windows 인스턴스에는 추가 구성이 필요합니다. Max I/O보다 처리량이 낮아 대용량 비디오 파일을 가장 짧은 시간에 처리하기에 적합하지 않습니다.

