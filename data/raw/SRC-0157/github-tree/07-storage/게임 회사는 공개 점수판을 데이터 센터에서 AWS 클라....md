## Question

게임 회사는 공개 점수판을 데이터 센터에서 AWS 클라우드로 옮기고 있습니다. 이 회사는 Application Load Balancer 뒤에 Amazon EC2 Windows Server 인스턴스를 사용하여 동적 애플리케이션을 호스팅합니다. 회사는 애플리케이션을 위한 고가용성 스토리지 솔루션이 필요합니다. 애플리케이션은 정적 파일과 동적 서버 측 코드로 구성됩니다.
이러한 요구 사항을 충족하기 위해 솔루션 설계자는 어떤 단계 조합을 수행해야 합니까? (두 가지를 선택하세요.)

- [ ] A. Amazon S3에 정적 파일을 저장합니다. Amazon CloudFront를 사용하여 엣지에서 객체를 캐싱합니다.
- [ ] B. 정적 파일을 Amazon S3에 저장합니다. Amazon ElastiCache를 사용하여 엣지에서 객체를 캐싱합니다.
- [ ] C. Amazon Elastic File System(Amazon EFS)에 서버 측 코드를 저장합니다. 파일을 공유할 각 EC2 인스턴스에 EFS 볼륨을 탑재합니다.
- [ ] D. Windows File Server용 Amazon FSx에 서버 측 코드를 저장합니다. 파일을 공유할 각 EC2 인스턴스에 FSx for Windows File Server 볼륨을 탑재합니다.
- [ ] E. 범용 SSD(gp2) Amazon Elastic Block Store(Amazon EBS) 볼륨에 서버 측 코드를 저장합니다. 각 EC2 인스턴스에 EBS 볼륨을 탑재하여 파일을 공유합니다.

## Answer

정답: A, D

## Explanation

A(정적 파일은 S3 + CloudFront)와 D(서버 측 코드는 FSx for Windows File Server)가 정답입니다. 정적 파일은 S3에 저장하고 CloudFront로 캐싱하여 성능과 비용을 최적화하며, Windows EC2 인스턴스의 서버 측 코드는 FSx for Windows File Server를 통해 공유할 수 있습니다.

오답 분석

B: ElastiCache는 인메모리 캐시로, 엣지에서 정적 콘텐츠를 캐싱하는 데 적합하지 않습니다. CloudFront가 엣지 캐싱에 적합합니다.

C: EFS는 NFS 프로토콜만 지원하며, Windows Server 인스턴스에서의 네이티브 지원이 제한적입니다. 이는 해당 시나리오의 요구사항에 적합하지 않습니다.

E: EBS 볼륨은 단일 인스턴스에만 연결되므로 여러 EC2 인스턴스 간 파일 공유에 적합하지 않습니다. 이는 해당 시나리오의 요구사항에 적합하지 않습니다.

