# T15 — 응답 표현과 GitHub 근거 확장

상태: DOING
선행: T14

## 순차 작업

1. `**강조**`를 안전한 DOM `<strong>` 요소로 렌더링하고 임의 HTML은 text로 유지한다.
2. system prompt에서 김신건 본인의 답변 외 요약·첨삭·후속 서비스 제안을 금지한다.
3. 결정적 후처리로 `원하시면`, 면접 30초 버전, 자기소개서 문체 등의 이탈 문장을 제거한다.
4. GitHub GraphQL에서 `shinkeonkim` 소유 공개 저장소와 공개 기여 저장소를 페이지 단위로 조사한다.
5. 조직, 프로젝트 관계, 생성·수정·push 일시, 언어, topic, 최신 commit을 source/document로 등록한다.
6. chunk·audit·retrieval 검증 후 이미지와 GitOps digest를 배포한다.

## 후속 병렬 수집 큐

- A: 신규 저장소 README 및 공개 문서 snapshot 보강
- B: `shinkeonkim` authored commit과 PR의 날짜별 contribution snapshot 보강
- C: 주요 조직 프로젝트를 우선순위화하여 shallow clone 후 tracked text 수집
- D: 중복·민감정보·source 역추적 audit 및 검색 평가 질문 확장

모든 네트워크 수집은 `persona collect-github-metadata --approve`처럼 명시적 승인 플래그를
요구하며, 공개 HTTPS URL과 관측 시점을 보존합니다.
