## Question

미디어 회사는 Amazon S3에 영화를 저장합니다. 각 영화는 크기가 1GB에서 10GB 사이인 단일 비디오 파일에 저장됩니다.
회사는 사용자가 구매한 후 5분 이내에 영화의 스트리밍 콘텐츠를 제공할 수 있어야 합니다. 20년이 넘은 영화보다 20년 미만의 영화에 대한 수요가 더 높습니다. 회사는 수요에 따라 호스팅 서비스 비용을 최소화하려고 합니다.
어떤 솔루션이 이러한 요구 사항을 충족합니까?

- [ ] A. 모든 미디어 콘텐츠를 Amazon S3에 저장합니다. 영화에 대한 수요가 감소할 때 S3 수명 주기 정책을 사용하여 미디어 데이터를 Infrequent Access 계층으로 이동합니다.
- [ ] B. S3 Standard에 최신 영화 비디오 파일을 저장합니다. S3 Standard-infrequent Access(S3 Standard-IA)에 오래된 영화 비디오 파일을 저장합니다. 사용자가 오래된 영화를 주문하면 표준 검색을 사용하여 비디오 파일을 검색합니다.
- [ ] C. S3 Intelligent-Tiering에 최신 영화 비디오 파일을 저장합니다. S3 Glacier Flexible Retrieval에 오래된 영화 비디오 파일을 저장합니다. 사용자가 오래된 영화를 주문하면 신속 검색을 사용하여 비디오 파일을 검색합니다.
- [ ] D. S3 Standard에 최신 영화 비디오 파일을 저장합니다. S3 Glacier Flexible Retrieval에 오래된 영화 비디오 파일을 저장합니다. 사용자가 오래된 영화를 주문하면 대량 검색을 사용하여 비디오 파일을 검색합니다.

## Answer

정답: C

## Explanation

최신 영화를 S3 Intelligent-Tiering에 저장하면 수요 변화에 따라 Frequent Access, Infrequent Access, Archive Instant Access 계층 간 자동 전환되어 비용이 최적화됩니다. 20년 이상 된 오래된 영화는 S3 Glacier Flexible Retrieval에 저장하여 GB당 약 $0.004의 저렴한 스토리지 비용을 적용합니다. 신속(Expedited) 검색은 통상 1-5분 이내에 완료되어 스트리밍 시작에 필요한 초기 데이터를 신속하게 제공하므로, 구매 후 5분 이내 스트리밍 제공 요구 사항을 충족합니다.

오답 분석

A: S3 수명 주기 정책으로 Infrequent Access 계층으로만 전환하는 것은 S3 Standard-IA의 GB당 $0.0125 비용이 Glacier($0.004)보다 약 3배 높아 오래된 영화의 비용을 충분히 절감하지 못합니다.

B: S3 Standard-IA는 오래된 영화에 Glacier보다 스토리지 비용이 높으며, 20년 미만/이상 영화의 수요 차이를 활용한 비용 최적화가 부족합니다.

D: 대량(Bulk) 검색은 5-12시간이 소요되어 구매 후 5분 이내 스트리밍 제공이 불가능합니다. Bulk 검색은 비용은 저렴하지만 긴급한 검색에는 적합하지 않습니다.

