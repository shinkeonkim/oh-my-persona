# T07/T08 — 웹 제품

상태: DONE
실행: API와 UI 병렬, 통합은 순차
선행: T06

- `/api/search`: 생성 모델 없이 근거 탐색
- `/api/sources/{source_id}`: 공개 source metadata
- `/api/chat`: RAG 응답
- `/api/chat/stream`: SSE 이벤트(`sources`, `token`, `done`, `error`)
- `/api/models`: 서버가 허용한 논리 model alias만 공개
- `/`: 모바일/PC 반응형 채팅 UI

LLM 자격 증명이 없으면 검색 결과의 발췌를 제공하는 deterministic grounded mode로 동작한다. 따라서 개발 환경에서도 허위 생성 없이 제품 흐름을 확인할 수 있다.
