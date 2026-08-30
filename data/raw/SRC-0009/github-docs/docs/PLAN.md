# Twin AI 개발 계획 (PLAN.md)

## 1. 프로젝트 개요
- "나"(김신건)를 모방하는 AI 개발
- 실제 사람처럼 지식 설명, 자기소개, 말투/성격 모방

## 2. 주요 목표
1. 페르소나(ESTJ) 기반 AI 구현
2. 프롬프트 엔지니어링으로 자연스러운 대화
3. RAG 기반 데이터 보정 및 활용
4. Slack Bot MVP 배포

## 3. 개발 단계별 계획

### 1단계: 데이터 수집 및 저장
- 김신건 관련 문서, 대화, 이력서 등 수집
- sqlite3에 1차 저장, ChromaDB와 동기화

### 2단계: 페르소나 및 프롬프트 설계
- ESTJ 성격 반영 페르소나 설계
- 프롬프트 템플릿 작성 및 테스트

### 3단계: RAG 파이프라인 구축
- sqlite3 ↔ ChromaDB 동기화 로직 구현
- RAG 기반 질의응답/설명 기능 개발

### 4단계: AI API 연동
- Gemini API/ChatGPT API 연동
- 프롬프트/응답 파이프라인 구축

### 5단계: Slack Bot MVP 개발 및 배포
- Slack Bot 인터페이스 구현
- Docker/Docker-compose로 배포 환경 구성

### 6단계: 부가 기능 및 개선
- 자동 질문 생성 및 답변 데이터화
- 이력서 등 추가 정보 반영

## 5. 사용 기술
- Python, ChromaDB, sqlite3, Docker, docker-compose, Gemini API, ChatGPT API

## 6. 향후 개선 방향
- 자동 질문/답변 데이터화, 이력서 등 정보 추가, 기타 페르소나 확장 등
