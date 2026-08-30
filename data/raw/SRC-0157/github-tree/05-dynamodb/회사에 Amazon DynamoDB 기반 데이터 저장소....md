## Question

회사에 Amazon DynamoDB 기반 데이터 저장소가 있는 모바일 채팅 애플리케이션이 있습니다. 사용자는 가능한 한 짧은 대기 시간으로 새 메시지를 읽기를 원합니다. 솔루션 설계자는 최소한의 애플리케이션 변경이 필요한 최적의 솔루션을 설계해야 합니다.
솔루션 설계자는 어떤 방법을 선택해야 합니까?

- [ ] A. 새 메시지 테이블에 대해 Amazon DynamoDB Accelerator(DAX)를 구성합니다. DAX 엔드포인트를 사용하도록 코드를 업데이트합니다.
- [ ] B. 증가된 읽기 로드를 처리하기 위해 DynamoDB 읽기 복제본을 추가합니다. 읽기 전용 복제본의 읽기 엔드포인트를 가리키도록 애플리케이션을 업데이트합니다.
- [ ] C. DynamoDB의 새 메시지 테이블에 대한 읽기 용량 단위 수를 두 배로 늘립니다. 기존 DynamoDB 엔드포인트를 계속 사용합니다.
- [ ] D. Redis 캐시용 Amazon ElastiCache를 애플리케이션 스택에 추가합니다. DynamoDB 대신 Redis 캐시 엔드포인트를 가리키도록 애플리케이션을 업데이트합니다.

## Answer

정답: A

## Explanation

DynamoDB Accelerator(DAX)는 DynamoDB와 완전히 호환되는 인메모리 캐시로, 애플리케이션 코드에서 DynamoDB 클라이언트를 DAX 클라이언트로 변경하고 DAX 엔드포인트를 지정하기만 하면 됩니다. 이를 통해 새 메시지 읽기 지연 시간을 밀리초에서 마이크로초 수준으로 줄일 수 있으며, 기존 DynamoDB API(GetItem, Query 등)가 그대로 작동하므로 최소한의 애플리케이션 변경만 필요합니다.

오답 분석

B: DynamoDB는 읽기 복제본(Read Replica) 개념을 지원하지 않습니다. 이는 Amazon RDS의 기능으로, DynamoDB와는 완전히 다른 아키텍처입니다. DynamoDB는 자체적으로 읽기 확장을 처리하며, 캐싱이 필요한 경우 DAX를 사용합니다.

C: 읽기 용량 단위(RCU)를 두 배로 늘리면 처리량(throughput)은 증가하지만, 개별 요청의 지연 시간(latency)은 크게 개선되지 않습니다. DynamoDB의 기본 지연 시간은 한 자릿수 밀리초이며, 마이크로초 수준의 성능은 인메모리 캐시(DAX)를 통해서만 달성 가능합니다.

D: ElastiCache for Redis는 강력한 캐시이지만, DynamoDB 대신 Redis 엔드포인트를 사용하도록 변경하려면 데이터 직렬화, 캐시 관리 로직, 오류 처리 등 상당한 코드 수정이 필요합니다. DAX는 DynamoDB API와 호환되어 최소 변경 요구사항에 더 적합합니다.

