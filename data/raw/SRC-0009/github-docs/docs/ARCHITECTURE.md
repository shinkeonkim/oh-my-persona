# Twin AI 시스템 아키텍처 (ARCHITECTURE.md)

## 1. 전체 구조 개요

```
[User(Slack)]
    │
    ▼
[Slack Bot] ──▶ [API 서버 (Python)]
                      │
                      ├─ [프롬프트 엔지니어링/페르소나 모듈]
                      │
                      ├─ [RAG 파이프라인]
                      │      ├─ [sqlite3 DB]
                      │      └─ [ChromaDB (벡터DB)]
                      │
                      └─ [LLM API (Gemini/ChatGPT)]
```

## 2. 구성요소별 설명

### 1) Slack Bot
- Slack에서 사용자 메시지 수신/응답
- API 서버와 통신하여 답변 전달

### 2) API 서버 (Python)
- Slack Bot과 LLM, DB, RAG 등 모든 로직의 허브
- REST API 또는 WebSocket 등으로 Slack Bot과 연동

### 3) 프롬프트 엔지니어링/페르소나 모듈
- ESTJ 성격, 말투, 자기소개 등 프롬프트 템플릿 관리
- 사용자 입력을 페르소나에 맞게 가공

### 4) RAG 파이프라인
- sqlite3: 원본 데이터 저장(문서, 이력서, 대화 등)
- ChromaDB: 벡터화된 데이터 저장 및 검색
- 동기화 로직: sqlite3 ↔ ChromaDB 데이터 일관성 유지
- 질의 시 관련 데이터 검색 및 LLM에 전달

### 5) LLM API (Gemini/ChatGPT)
- 프롬프트와 RAG 결과를 받아 응답 생성
- 다양한 LLM API 지원 가능

### 6) Docker/Docker-compose
- 전체 서비스 컨테이너화 및 배포 자동화

## 3. 데이터 흐름
1. Slack 사용자가 메시지 입력
2. Slack Bot이 API 서버로 메시지 전달
3. API 서버가 프롬프트/페르소나 적용
4. RAG로 관련 데이터 검색
5. LLM API에 프롬프트+데이터 전달, 응답 생성
6. Slack Bot이 사용자에게 응답 전달

## 4. 향후 확장
- 추가 페르소나, 다양한 입력 채널, 자동 질문/답변 데이터화 등
