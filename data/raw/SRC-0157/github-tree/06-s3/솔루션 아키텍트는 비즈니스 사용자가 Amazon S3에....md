## Question

솔루션 아키텍트는 비즈니스 사용자가 Amazon S3에 객체를 업로드할 수 있는 애플리케이션을 설계하고 있습니다. 솔루션은 객체 내구성을 극대화해야 합니다. 또한 객체는 언제든지, 기간에 관계없이 쉽게 사용할 수 있어야 합니다. 사용자는 객체가 업로드된 후 처음 30일 이내에 객체에 자주 액세스하지만 30일보다 오래된 객체에는 사용자가 액세스할 가능성이 훨씬 적습니다.
이러한 요구 사항을 가장 비용 효율적으로 충족하는 솔루션은 무엇입니까?

- [ ] A. S3 수명 주기 규칙을 사용하여 모든 객체를 S3 Standard에 저장하여 30일 후에 객체를 S3 Glacier로 전환합니다.
- [ ] B. S3 수명 주기 규칙을 사용하여 모든 객체를 S3 Standard에 저장하고 30일 후에 S3 Standard-Infrequent Access(S3 Standard-IA)로 전환합니다.
- [ ] C. 30일 후에 객체를 S3 One Zone-Infrequent Access(S3 One Zone-IA)로 전환하는 S3 수명 주기 규칙을 사용하여 모든 객체를 S3 Standard에 저장합니다.
- [ ] D. S3 수명 주기 규칙을 사용하여 모든 객체를 S3 Intelligent-Tiering에 저장하여 30일 후에 객체를 S3 Standard-Infrequent Access(S3 Standard-IA)로 전환합니다.

## Answer

정답: B

## Explanation

S3 Standard에 저장한 후 30일 후 S3 Standard-IA로 전환하는 수명 주기 규칙이 가장 비용 효율적입니다. 처음 30일간 자주 액세스되므로 S3 Standard가 적합하고, 이후에는 접근 빈도가 줄지만 언제든 즉시 사용 가능해야 하므로 S3 Standard-IA가 적합합니다. S3 Standard-IA는 여러 AZ에 데이터를 저장하여 최대 내구성을 보장합니다.

오답 분석

A: S3 Glacier로 전환하면 즉시 접근이 불가능하여 '언제든지 쉽게 사용 가능' 요구 사항을 충족하지 못합니다.

C: S3 One Zone-IA는 단일 가용 영역에만 저장하여 '내구성 극대화' 요구 사항을 충족하지 못합니다.

D: S3 Intelligent-Tiering에서 다시 S3 Standard-IA로 전환하는 수명 주기 규칙은 불필요한 복잡성을 추가하며, 직접 Standard에서 Standard-IA로 전환하는 것이 더 간단하고 비용 효율적입니다.

