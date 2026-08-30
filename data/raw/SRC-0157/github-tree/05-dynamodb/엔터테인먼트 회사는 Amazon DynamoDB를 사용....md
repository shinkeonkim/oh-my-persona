## Question

엔터테인먼트 회사는 Amazon DynamoDB를 사용하여 미디어 메타데이터를 저장하고 있습니다. 애플리케이션이 읽기 집약적이며 지연이 발생합니다. 회사에는 추가 운영 오버헤드를 처리할 직원이 없으며 애플리케이션을 재구성하지 않고 DynamoDB의 성능 효율성을 개선해야 합니다.
이 요구 사항을 충족하기 위해 솔루션 설계자는 무엇을 권장해야 합니까?

- [ ] A. Redis용 Amazon ElastiCache를 사용합니다.
- [ ] B. Amazon DynamoDB Accelerator(DAX)를 사용합니다.
- [ ] C. DynamoDB 전역 테이블을 사용하여 데이터를 복제합니다.
- [ ] D. 자동 검색이 활성화된 Memcached용 Amazon ElastiCache를 사용합니다.

## Answer

정답: B

## Explanation

DynamoDB Accelerator(DAX)는 DynamoDB 전용으로 설계된 완전관리형 인메모리 캐시 서비스입니다. DAX는 DynamoDB API와 완전히 호환되어, 애플리케이션 코드에서 DynamoDB 엔드포인트를 DAX 엔드포인트로 변경하기만 하면 됩니다. 이를 통해 읽기 지연 시간을 밀리초에서 마이크로초(일반적으로 수 백 마이크로초) 수준으로 개선할 수 있으며, 추가 운영 오버헤드 없이 완전관리형으로 운영됩니다.

오답 분석

A: Amazon ElastiCache for Redis는 강력한 범용 인메모리 캐시이지만, DynamoDB와 통합하려면 캐시 무효화 로직, 데이터 직렬화/역직렬화, 캐시 미스 처리 등의 애플리케이션 코드를 상당히 수정해야 합니다. 이는 '애플리케이션을 재구성하지 않고' 성능을 개선해야 하는 요구사항에 위배됩니다.

C: DynamoDB 전역 테이블은 여러 AWS 리전에 걸쳐 테이블을 복제하여 글로벌 사용자에게 낮은 지연 시간을 제공합니다. 그러나 동일 리전 내의 읽기 지연 시간 개선에는 도움이 되지 않으며, 복제 비용이 추가로 발생합니다.

D: Amazon ElastiCache for Memcached도 Redis와 마찬가지로 DynamoDB와 별도의 캐시 통합 코드를 작성해야 합니다. DAX는 DynamoDB의 네이티브 캐시 솔루션으로 최소한의 코드 변경만 필요한 반면, Memcached는 별도의 캐시 관리 아키텍처가 필요합니다.

