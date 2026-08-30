## Question

회사는 수집된 원시 데이터를 Amazon S3 버킷에 저장합니다. 이 데이터는 회사 고객을 대신하여 여러 유형의 분석에 사용됩니다. 요청된 분석 유형에 따라 S3 객체에 대한 액세스 패턴이 결정됩니다.
회사는 접속 패턴을 예측하거나 통제할 수 없습니다. 회사는 S3 비용을 줄이고자 합니다.
이러한 요구 사항을 충족하는 솔루션은 무엇입니까?

- [ ] A. S3 복제를 사용하여 자주 액세스하지 않는 객체를 S3 Standard-Infrequent Access(S3 Standard-IA)로 전환합니다.
- [ ] B. S3 수명 주기 규칙을 사용하여 객체를 S3 Standard에서 S3 Standard-Infrequent Access(S3 Standard-IA)로 전환합니다.
- [ ] C. S3 수명 주기 규칙을 사용하여 객체를 S3 Standard에서 S3 Intelligent-Tiering으로 전환합니다.
- [ ] D. S3 Inventory를 사용하여 S3 Standard에서 S3 Intelligent-Tiering으로 액세스하지 않은 객체를 식별하고 전환합니다.

## Answer

정답: C

## Explanation

S3 수명 주기 규칙을 사용하여 S3 Standard에서 S3 Intelligent-Tiering으로 전환하는 것이 가장 적합합니다. 회사가 고객별 분석 유형에 따라 액세스 패턴이 달라지고 이를 예측하거나 통제할 수 없으므로, S3 Intelligent-Tiering이 액세스 빈도를 모니터링하여 자동으로 Frequent Access, Infrequent Access, Archive Instant Access 등 최적의 스토리지 계층으로 데이터를 이동시킵니다. 이를 통해 성능 저하 없이 스토리지 비용을 최대 70%까지 절감할 수 있습니다.

오답 분석

A: S3 복제(Replication)는 데이터를 다른 버킷이나 리전에 복제하는 기능으로, 스토리지 클래스 전환과는 완전히 다른 목적의 기능입니다. 복제를 수행하면 오히려 데이터 중복으로 비용이 증가합니다.

B: S3 수명 주기 규칙으로 S3 Standard-IA로 전환하면, 예측 불가능한 액세스 패턴에서 자주 액세스되는 객체에 GB당 검색 비용($0.01/GB)이 부과되어 오히려 비용이 증가할 수 있습니다.

D: S3 Inventory는 버킷 내 객체 목록과 메타데이터를 CSV/ORC/Parquet 형식으로 생성하는 보고 도구이며, 객체를 다른 스토리지 클래스로 전환하는 기능이 아닙니다.

