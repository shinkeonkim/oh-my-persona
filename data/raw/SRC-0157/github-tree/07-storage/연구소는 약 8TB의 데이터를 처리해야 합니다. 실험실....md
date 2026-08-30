## Question

연구소는 약 8TB의 데이터를 처리해야 합니다. 실험실에는 스토리지 하위 시스템에 대해 1밀리초 미만의 대기 시간과 최소 6GBps의 처리량이 필요합니다. Amazon Linux를 실행하는 수백 개의 Amazon EC2 인스턴스가 데이터를 배포하고 처리합니다.
성능 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. NetApp ONTAP 파일 시스템용 Amazon FSx를 생성합니다. 각 볼륨의 계층화 정책을 ALL로 설정합니다. 원시 데이터를 파일 시스템으로 가져옵니다. EC2 인스턴스에 파일 시스템을 탑재합니다.
- [ ] B. 원시 데이터를 저장할 Amazon S3 버킷을 생성합니다. 영구 SSD 스토리지를 사용하는 Amazon FSx for Lustre 파일 시스템을 생성합니다. Amazon S3에서 데이터를 가져오고 내보내는 옵션을 선택합니다. EC2 인스턴스에 파일 시스템을 탑재합니다.
- [ ] C. 원시 데이터를 저장할 Amazon S3 버킷을 생성합니다. 영구 HDD 스토리지를 사용하는 Amazon FSx for Lustre 파일 시스템을 생성합니다. Amazon S3에서 데이터를 가져오고 내보내는 옵션을 선택합니다. EC2 인스턴스에 파일 시스템을 탑재합니다.
- [ ] D. NetApp ONTAP 파일 시스템용 Amazon FSx를 생성합니다. 각 볼륨의 계층화 정책을 NONE으로 설정합니다. 원시 데이터를 파일 시스템으로 가져옵니다. EC2 인스턴스에 파일 시스템을 탑재합니다.

## Answer

정답: B

## Explanation

Amazon FSx for Lustre 영구 SSD 스토리지는 1밀리초 미만의 지연 시간과 최대 수백 GBps의 처리량을 제공하여 6GBps 이상의 처리량 요구사항을 충족합니다. S3와 기본 통합되어 8TB 데이터를 S3에서 가져오고 처리 결과를 내보낼 수 있으며, 수백 개의 Amazon Linux EC2 인스턴스에서 POSIX 호환 병렬 파일 시스템으로 동시에 마운트하여 분산 처리가 가능합니다.

오답 분석

A: FSx for NetApp ONTAP에서 계층화 정책을 ALL로 설정하면 모든 데이터가 저렴한 용량 풀 스토리지(HDD 기반)로 이동됩니다. 이 경우 SSD 성능이 아닌 HDD 성능으로 데이터에 접근하게 되어 밀리초 미만 지연 시간과 6GBps 처리량 요구사항을 충족하지 못합니다.

C: FSx for Lustre 영구 HDD 스토리지는 SSD보다 지연 시간이 길고 처리량이 낮습니다. HDD 기반은 최대 수백 MB/s 수준의 처리량만 제공하여 6GBps 요구사항을 충족하지 못합니다. SSD 기반만이 이 수준의 성능을 제공합니다.

D: FSx for NetApp ONTAP에서 NONE 정책은 모든 데이터를 고성능 SSD 계층에 유지하지만, ONTAP은 Lustre만큼의 HPC 수준 병렬 I/O 성능을 제공하지 않습니다. 8TB 데이터의 6GBps 처리량에는 Lustre가 더 적합합니다.

