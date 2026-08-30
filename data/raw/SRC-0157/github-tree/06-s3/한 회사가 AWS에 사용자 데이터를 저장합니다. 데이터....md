## Question

한 회사가 AWS에 사용자 데이터를 저장합니다. 데이터는 업무 시간 동안 피크 사용량으로 지속적으로 사용됩니다. 액세스 패턴은 다양하며, 일부 데이터는 한 번에 몇 달 동안 사용되지 않습니다. 솔루션 아키텍트는 높은 가용성을 유지하면서도 최고 수준의 내구성을 유지하는 비용 효율적인 솔루션을 선택해야 합니다.
어떤 스토리지 솔루션이 이러한 요구 사항을 충족합니까?

- [ ] A. Amazon S3 Standard
- [ ] B. Amazon S3 Intelligent-Tiering
- [ ] C. Amazon S3 Glacier Deep Archive
- [ ] D. Amazon S3 One Zone-Infrequent Access(S3 One Zone-IA)

## Answer

정답: B

## Explanation

Amazon S3 Intelligent-Tiering은 액세스 패턴이 변하거나 예측할 수 없는 데이터에 가장 비용 효율적인 스토리지 클래스입니다. 자주 액세스되는 데이터와 드물게 액세스되는 데이터를 자동으로 적절한 티어로 이동시켜 비용을 최적화하면서도 S3 Standard와 동일한 높은 내구성(99.999999999%)과 고가용성을 제공합니다.

오답 분석

A: S3 Standard은 높은 내구성과 가용성을 제공하지만, 접근 패턴이 불규칙한 데이터에 대해 비용 최적화가 되지 않습니다. 모든 데이터에 동일한 요금이 부과됩니다.

C: S3 Glacier Deep Archive는 장기 보관용으로 데이터 검색에 12시간 이상 걸리므로 비즈니스 시간에 지속적으로 사용되는 데이터에는 부적합합니다.

D: S3 One Zone-IA는 단일 가용 영역에만 데이터를 저장하므로 고가용성 요구사항을 충족하지 못합니다.

