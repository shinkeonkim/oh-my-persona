## Question

한 회사가 5PB의 보관된 데이터를 물리적 테이프에 저장합니다. 이 회사는 데이터를 10년 더 보관해야 합니다. 테이프를 저장하는 데이터 센터에는 AWS 리전에 대한 10Gbps Direct Connect 연결이 있습니다. 이 회사는 향후 6개월 이내에 데이터를 AWS로 마이그레이션하려고 합니다.

- [ ] A. 온프레미스에서 테이프의 데이터를 읽습니다. 로컬 스토리지를 사용하여 데이터를 스테이징합니다. AWS DataSync를 사용하여 데이터를 Amazon S3 Glacier Flexible Retrieval 스토리지로 마이그레이션합니다.
- [ ] B. 온프레미스 백업 애플리케이션을 사용하여 테이프의 데이터를 읽습니다. 백업 애플리케이션을 사용하여 Amazon S3 Glacier Deep Archive 스토리지에 직접 씁니다.
- [ ] C. 여러 AWS Snowball Edge 장치를 주문합니다. Snowball Edge 장치의 가상 테이프에 물리적 테이프를 복사합니다. Snowball Edge 장치를 AWS로 배송합니다. 테이프를 Amazon S3 Glacier Instant Retrieval 스토리지로 이동하는 S3 수명 주기 정책을 만듭니다.
- [ ] D. 온프레미스 AWS Storage Gateway Tape Gateway를 구성합니다. AWS Cloud에서 가상 테이프를 만듭니다. 백업 소프트웨어를 사용하여 물리적 테이프를 가상 테이프로 복사합니다. 가상 테이프를 Amazon S3 Glacier Deep Archive 스토리지로 이동합니다.

## Answer

정답: D

## Explanation

AWS Storage Gateway Tape Gateway를 온프레미스에 구성하면 기존 백업 소프트웨어를 사용하여 물리적 테이프 데이터를 가상 테이프로 복사할 수 있습니다. 가상 테이프를 S3 Glacier Deep Archive로 이동하면 10년 장기 보관에 가장 비용 효율적이며, 10Gbps Direct Connect를 통해 데이터를 전송할 수 있습니다.

오답 분석

A: DataSync로 S3 Glacier Flexible Retrieval에 저장하는 것은 가능하지만, Deep Archive보다 비용이 높고, 테이프에서 직접 데이터를 읽어 스테이징하는 것은 추가 로컬 스토리지가 필요합니다.

B: 온프레미스 백업 애플리케이션에서 S3 Glacier Deep Archive에 직접 쓰는 것은 기술적으로 S3 API를 통해 가능하지만, 이 방식은 백업 소프트웨어가 Glacier Deep Archive 스토리지 클래스를 사용하는 S3 API를 사용하도록 수정되어야 합니다. Tape Gateway는 기존 백업 소프트웨어가 이미 지원하는 VTL(가상 테이프 라이브러리) 인터페이스를 제공하므로 애플리케이션 변경이 필요 없어 이 시나리오에 더 적합합니다.

C: Snowball Edge는 5PB 데이터에 대해 많은 디바이스가 필요하고, S3 Glacier Instant Retrieval은 장기 보관에 Deep Archive보다 비용이 높습니다.

