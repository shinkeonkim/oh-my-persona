# T03/T06 — 저장과 검색

상태: DONE
실행: T02와 병렬 후 T04에서 합류
선행: T01

`migrations/001_initial.sql`은 source/document/claim/chunk/embedding 계보와 한국어 simple FTS, pgvector cosine index를 만든다. 개발·테스트에서는 설치 없이 동작하는 메모리 lexical retriever를 사용하고 운영에서는 `PERSONA_DATABASE_URL` 설정 시 PostgreSQL hybrid retriever를 사용한다.

임베딩 dimension별 table/모델 버전을 섞지 않는 원칙을 적용한다. 초기 migration은 1536차원이며 변경 시 새 migration/table을 만든다.
