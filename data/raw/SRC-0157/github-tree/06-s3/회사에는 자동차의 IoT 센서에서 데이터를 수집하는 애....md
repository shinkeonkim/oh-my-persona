## Question

회사에는 자동차의 IoT 센서에서 데이터를 수집하는 애플리케이션이 있습니다. 데이터는 Amazon Kinesis Data Firehose를 통해 Amazon S3에 스트리밍 및 저장됩니다. 데이터는 매년 수조 개의 S3 객체를 생성합니다. 매일 아침 회사는 지난 30일 동안의 데이터를 사용하여 일련의 기계 학습(ML) 모델을 재교육합니다.
매년 4회 회사는 이전 12개월의 데이터를 사용하여 분석을 수행하고 다른 ML 모델을 교육합니다. 데이터는 최대 1년 동안 최소한의 지연으로 사용할 수 있어야 합니다. 1년 후에는 데이터를 보관 목적으로 보관해야 합니다.
이러한 요구 사항을 가장 비용 효율적으로 충족하는 스토리지 솔루션은 무엇입니까?

- [ ] A. S3 Intelligent-Tiering 스토리지 클래스를 사용합니다. 1년 후 객체를 S3 Glacier Deep Archive로 전환하는 S3 수명 주기 정책을 생성합니다.
- [ ] B. S3 Intelligent-Tiering 스토리지 클래스를 사용합니다. 1년 후 자동으로 객체를 S3 Glacier Deep Archive로 이동하도록 S3 Intelligent-Tiering을 구성합니다.
- [ ] C. S3 Standard-Infrequent Access(S3 Standard-IA) 스토리지 클래스를 사용합니다. 1년 후 객체를 S3 Glacier Deep Archive로 전환하는 S3 수명 주기 정책을 생성합니다.
- [ ] D. S3 Standard 스토리지 클래스를 사용합니다. 30일 후에 객체를 S3 Standard-Infrequent Access(S3 Standard-IA)로 전환한 다음 1년 후에 S3 Glacier Deep Archive로 전환하는 S3 수명 주기 정책을 생성합니다.

## Answer

정답: D

## Explanation

처음 30일간 데이터를 자주 사용하므로 S3 Standard에 저장하고, 30일 후에는 주로 사용하지 않지만 최소 지연으로 접근 가능해야 하므로 S3 Standard-IA로 전환합니다. 1년 후에는 보관 목적이므로 S3 Glacier Deep Archive로 전환하여 비용을 최소화합니다. 이 3단계 수명 주기 정책이 가장 비용 효율적입니다.

오답 분석

A: S3 Intelligent-Tiering에 수명 주기 정책으로 Glacier Deep Archive 전환을 추가하는 것은 비용 효율적이지만, 처음 30일간 자주 액세스되고 이후 패턴이 명확하므로 Standard에서 Standard-IA로의 명시적 전환이 더 비용 효율적입니다.

B: S3 Intelligent-Tiering이 자동으로 Glacier Deep Archive로 이동하도록 구성할 수 있지만, Deep Archive 계층 활성화는 수명 주기 정책 전환과 다르며 이 시나리오의 명확한 액세스 패턴에는 명시적 전환이 더 적합합니다.

C: S3 Standard-IA를 처음부터 사용하면 처음 30일간 자주 액세스되는 데이터에 대해 검색 비용이 높아집니다.

