## Question

회사는 데이터 객체를 Amazon S3 Standard 스토리지에 저장합니다. 한 솔루션 설계자는 데이터의 75%가 30일 후에 거의 액세스되지 않는다는 사실을 발견했습니다. 회사는 동일한 고가용성 및 탄력성으로 모든 데이터에 즉시 액세스할 수 있어야 하지만 스토리지 비용을 최소화하기를 원합니다.
이러한 요구 사항을 충족하는 스토리지 솔루션은 무엇입니까?

- [ ] A. 30일 후에 데이터 객체를 S3 Glacier Deep Archive로 이동합니다.
- [ ] B. 30일 후에 데이터 객체를 S3 Standard-Infrequent Access(S3 Standard-IA)로 이동합니다.
- [ ] C. 30일 후에 데이터 객체를 S3 One Zone-Infrequent Access(S3 One Zone-IA)로 이동합니다.
- [ ] D. 데이터 객체를 S3 One Zone-Infrequent Access(S3 One Zone-IA)로 즉시 이동합니다.

## Answer

정답: B

## Explanation

30일 후 데이터의 75%가 거의 액세스되지 않으므로 S3 수명 주기 정책을 사용하여 S3 Standard-IA로 전환하는 것이 비용 효율적입니다. S3 Standard-IA는 S3 Standard와 동일하게 밀리초 단위의 즉시 접근성을 유지하면서 스토리지 비용이 약 45% 저렴합니다(S3 Standard $0.023/GB vs S3 Standard-IA $0.0125/GB). 또한 여러 AZ에 데이터를 자동 복제하여 99.999999999%의 내구성과 99.9%의 가용성을 제공합니다.

오답 분석

A: S3 Glacier Deep Archive는 즉시 접근이 불가능하며, 표준 검색에 최대 12시간까지 소요될 수 있어 '즉시 액세스 가능' 요구 사항을 충족하지 못합니다.

C: S3 One Zone-IA는 단일 가용 영역에만 데이터를 저장하므로 AZ 장애 시 데이터 손실 위험이 있어 '동일한 고가용성과 탄력성' 요구 사항을 충족하지 못합니다.

D: 즉시 S3 One Zone-IA로 이동하면 처음 30일간 자주 액세스되는 데이터에 대해 GB당 검색 비용이 부과되어 비용이 증가하며, 단일 AZ 저장으로 고가용성 요구 사항도 충족하지 못합니다.

