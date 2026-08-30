## Question

회사는 오래된 뉴스 영상에서 AWS에 비디오 아카이브를 저장할 수 있는 솔루션을 찾고 있습니다. 회사는 비용을 최소화해야 하며 이러한 파일을 복원할 필요가 거의 없습니다. 파일이 필요할 때 최대 5분 내에 사용할 수 있어야 합니다.
가장 비용 효율적인 솔루션은 무엇입니까?

- [ ] A. 비디오 아카이브를 Amazon S3 Glacier에 저장하고 긴급 검색을 사용합니다.
- [ ] B. 비디오 아카이브를 Amazon S3 Glacier에 저장하고 표준 검색을 사용합니다.
- [ ] C. 비디오 아카이브를 Amazon S3 Standard-Infrequent Access(S3 Standard-IA)에 저장합니다.
- [ ] D. 비디오 아카이브를 Amazon S3 One Zone-Infrequent Access(S3 One Zone-IA)에 저장합니다.

## Answer

정답: A

## Explanation

S3 Glacier에 저장하고 긴급(Expedited) 검색을 사용하면 통상 1-5분 이내에 파일을 검색할 수 있어 '최대 5분 이내' 사용 가능 요구 사항을 충족합니다. S3 Glacier의 스토리지 비용은 GB당 약 $0.004로 S3 Standard($0.023)이나 S3 Standard-IA($0.0125)보다 훨씬 저렴합니다. 비디오 아카이브를 거의 복원하지 않으므로 간헐적인 긴급 검색 비용을 고려해도 전체적으로 가장 비용 효율적인 솔루션입니다.

오답 분석

B: S3 Glacier 표준(Standard) 검색은 3-5시간이 소요되어 5분 이내 사용 가능 요구 사항을 전혀 충족하지 못합니다.

C: S3 Standard-IA는 밀리초 단위의 즉시 접근이 가능하지만, GB당 스토리지 비용이 Glacier의 약 3배($0.0125 vs $0.004)로 거의 액세스하지 않는 아카이브 데이터에 과도한 비용이 발생합니다.

D: S3 One Zone-IA도 즉시 접근이 가능하지만, Glacier보다 비용이 높고 단일 AZ만 사용하여 가용 영역 장애 시 비디오 아카이브의 내구성이 보장되지 않습니다.

