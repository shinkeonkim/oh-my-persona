## Question

한 회사가 AWS DataSync를 사용하여 온프레미스 시스템에서 AWS로 수백만 개의 파일을 마이그레이션하고 있습니다. 파일의 평균 크기는 10KB입니다. 이 회사는 파일 스토리지에 Amazon S3를 사용하려고 합니다. 마이그레이션 후 첫 1년 동안은 파일을 한두 번 액세스해야 하며 즉시 사용할 수 있어야 합니다. 1년 후에는 파일을 최소 7년 동안 보관해야 합니다. 이러한 요구 사항을 가장 비용 효율적으로 충족하는 솔루션은 무엇입니까?

- [ ] A. 보관 도구를 사용하여 파일을 큰 객체로 그룹화합니다. DataSync를 사용하여 객체를 마이그레이션합니다. 첫해 동안 S3 Glacier Instant Retrieval에 객체를 저장합니다. 라이프사이클 구성을 사용하여 1년 후 7년의 보존 기간으로 파일을 S3 Glacier Deep Archive로 전환합니다.
- [ ] B. 보관 도구를 사용하여 파일을 큰 객체로 그룹화합니다. DataSync를 사용하여 객체를 S3 Standard-Infrequent Access (S3 Standard-IA)로 복사합니다. 라이프사이클 구성을 사용하여 1년 후 7년의 보존 기간으로 파일을 S3 Glacier Instant Retrieval로 전환합니다.
- [ ] C. 파일의 대상 스토리지 클래스를 S3 Glacier Instant Retrieval로 구성합니다. 라이프사이클 정책을 사용하여 1년 후 파일을 S3 Glacier Flexible Retrieval로 전환하고 보존 기간은 7년입니다.
- [ ] D. DataSync 작업을 구성하여 파일을 S3 Standard-Infrequent Access(S3 Standard-IA)로 전송합니다. 라이프사이클 구성을 사용하여 1년 후 7년의 보존 기간으로 파일을 S3 Glacier Deep Archive로 전환합니다.

## Answer

정답: D

## Explanation

10KB 크기의 소형 파일을 S3 Standard-IA에 저장하면 첫해 동안 즉시 접근이 가능하면서 비용이 절감됩니다. 1년 후 S3 Glacier Deep Archive로 전환하는 수명 주기 규칙을 설정하면 7년간 가장 비용 효율적으로 아카이브할 수 있습니다.

오답 분석

A: 소형 파일을 아카이브 도구로 그룹화하는 것은 추가 작업이며, Glacier Instant Retrieval은 Deep Archive보다 비용이 높습니다.

B: S3 Standard-IA에서 Glacier Instant Retrieval로 전환하면 Deep Archive보다 아카이브 비용이 높습니다.

C: Glacier Instant Retrieval은 S3 Standard-IA보다 최소 저장 기간(90일)과 검색 비용이 있어, 1-2회 접근되는 소형 파일에는 S3 Standard-IA가 더 적합합니다.

