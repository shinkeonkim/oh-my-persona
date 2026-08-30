## Question

회사는 AWS에서 확장 가능한 웹 애플리케이션을 호스팅하려고 합니다. 응용 프로그램은 전 세계 여러 지역의 사용자가 액세스할 수 있습니다. 애플리케이션 사용자는 최대 기가바이트 크기의 고유한 데이터를 다운로드하고 업로드할 수 있습니다. 개발 팀은 업로드 및 다운로드 대기 시간을 최소화하고 성능을 최대화할 수 있는 비용 효율적인 솔루션을 원합니다.
이를 달성하기 위해 솔루션 설계자는 무엇을 해야 합니까?

- [ ] A. Transfer Acceleration과 함께 Amazon S3를 사용하여 애플리케이션을 호스팅합니다.
- [ ] B. Cache-Control 헤더와 함께 Amazon S3를 사용하여 애플리케이션을 호스팅합니다.
- [ ] C. Auto Scaling 및 Amazon CloudFront와 함께 Amazon EC2를 사용하여 애플리케이션을 호스팅합니다.
- [ ] D. Auto Scaling 및 Amazon ElastiCache와 함께 Amazon EC2를 사용하여 애플리케이션을 호스팅합니다.

## Answer

정답: A

## Explanation

Amazon S3 Transfer Acceleration은 AWS CloudFront의 전 세계 엣지 로케이션을 통해 전 세계 사용자의 업로드 및 다운로드 대기 시간을 최소화합니다. 기가바이트 크기의 고유한 데이터를 업로드하고 다운로드하는 데 최적화되어 있으며, 비용 효율적인 서버리스 솔루션입니다.

오답 분석

B: Cache-Control 헤더는 캐싱을 관리하지만, 고유한 데이터의 업로드 대기 시간을 줄이는 데 도움이 되지 않습니다. 또한 S3만으로는 웹 애플리케이션의 동적 기능을 호스팅하기 어렵습니다.

C: EC2와 CloudFront 조합은 확장 가능하지만, CloudFront는 캐시 가능한 콘텐츠에 적합하며 고유한 사용자 데이터의 업로드에는 Transfer Acceleration이 더 효과적입니다.

D: ElastiCache는 인메모리 캐싱으로 데이터베이스 쿼리 성능을 개선하지만, 대용량 파일 업로드/다운로드 대기 시간 감소에는 도움이 되지 않습니다.

