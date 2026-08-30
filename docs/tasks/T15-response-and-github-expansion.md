# T15 — 응답 표현과 GitHub 근거 확장

상태: DONE (2026-08-31, metadata·심층 수집 완료)
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

위 A~D 큐는 2026-08-31 순차 실행을 완료했습니다. 반복 수집 명령은 다음과 같습니다.

```bash
persona collect-github-deep --approve
persona collect-github-prs --approve
persona collect-github-docs --approve
persona collect-github-priority --approve
persona chunk
persona audit
persona evaluate
```

모든 네트워크 수집은 `persona collect-github-metadata --approve`처럼 명시적 승인 플래그를
요구하며, 공개 HTTPS URL과 관측 시점을 보존합니다.

## 검증 결과

- GitHub 공개 조직 27개, 소유·기여 repository 합집합 226개 조사
- source 234개, document 13,941개, chunk 21,446개
- exact duplicate 0, 민감정보 탐지 0, source 역추적률 99.83%
- Python 20개, Playwright 7개 운영/CI 검증 통과
- 운영 prompt 회귀 검증에서 금지된 후속 조력 표현 0건, 근거 6개 반환
- GitOps PR #96, #97 검증·병합 및 `persona.shinkeonkim.com` 반영 완료

## 심층 수집 결과 (2026-08-31)

- 전체 226개 저장소 순차 조회: README 203개
- `shinkeonkim` 귀속 기본 branch commit 8,161개를 저장소별 216개 문서로 구성
- 등록된 저장소의 authored PR 682개를 43개 저장소 문서로 구성
- README 외 공개 문서 322개(61개 저장소), commit SHA 고정 URL 보존
- 기여량 상위 조직 저장소 30개 shallow clone: tracked text 3,549개
- shallow clone 실패 0, 내부 중복 208개 제거, 민감정보 의심 파일 1개 제외
- 최종 source 234개, document 18,274개, chunk 40,680개
- exact duplicate 0, 민감정보 탐지 0, source 역추적률 99.99%
- 검색 평가 9개, Python 21개, Playwright 7개 통과
