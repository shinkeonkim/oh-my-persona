## Question

회사에서 Amazon S3 Standard 스토리지를 사용하여 백업 파일을 저장하고 있습니다. 1개월 동안 파일에 자주 액세스합니다. 그러나 1개월이 지나면 파일에 액세스하지 않습니다. 회사는 파일을 무기한으로 보관해야 합니다.
이러한 요구 사항을 가장 비용 효율적으로 충족하는 스토리지 솔루션은 무엇입니까?

- [ ] A. 객체를 자동으로 마이그레이션하도록 S3 Intelligent-Tiering을 구성합니다.
- [ ] B. 1개월 후에 객체를 S3 Standard에서 S3 Glacier Deep Archive로 전환하는 S3 수명 주기 구성을 생성합니다.
- [ ] C. 1개월 후 객체를 S3 Standard에서 S3 Standard-Infrequent Access(S3 Standard-IA)로 전환하는 S3 수명 주기 구성을 생성합니다.
- [ ] D. 1개월 후에 객체를 S3 Standard에서 S3 One Zone-Infrequent Access(S3 One Zone-IA)로 전환하는 S3 수명 주기 구성을 생성합니다.

## Answer

정답: B

## Explanation

1개월 후에 파일에 더 이상 액세스하지 않고 무기한 보관해야 하므로, S3 Glacier Deep Archive로 전환하는 것이 가장 비용 효율적입니다. S3 Glacier Deep Archive는 AWS에서 가장 저렴한 스토리지 클래스로 GB당 약 $0.00099(us-east-1 기준)이며, 12시간 이내의 표준 검색과 48시간 이내의 대량 검색을 지원합니다. 파일에 전혀 액세스하지 않으므로 검색 비용은 발생하지 않아 장기 보관에 최적화되어 있습니다. S3 수명 주기 정책을 통해 30일 후 자동으로 전환됩니다.

오답 분석

A: S3 Intelligent-Tiering은 액세스 패턴이 예측 불가능할 때 유용하지만, 이 시나리오에서는 1개월 후 전혀 액세스하지 않는 패턴이 명확합니다. Intelligent-Tiering의 객체당 월별 모니터링 및 자동 계층화 비용($0.0025/1000개 객체)이 불필요하게 발생하며, Deep Archive 액세스 계층은 180일 이상 액세스하지 않은 후에야 전환되므로 즉시 최저 비용을 달성하지 못합니다.

C: S3 Standard-IA는 자주 액세스하지 않지만 즉시 액세스가 필요한 데이터에 적합하며, GB당 $0.0125로 Glacier Deep Archive($0.00099)보다 약 12.6배 비쌉니다. 파일에 전혀 액세스하지 않는 경우 즉시 접근 기능이 불필요하여 Glacier Deep Archive가 훨씬 경제적입니다.

D: S3 One Zone-IA는 단일 가용 영역에만 데이터를 저장하여 AZ 장애 시 데이터 손실 위험이 있으며(내구성 99.999999999%, 가용성 99.5%), 전혀 액세스하지 않는 데이터에는 Glacier Deep Archive(GB당 $0.00099)가 One Zone-IA(GB당 $0.01)보다 약 10배 저렴합니다.

