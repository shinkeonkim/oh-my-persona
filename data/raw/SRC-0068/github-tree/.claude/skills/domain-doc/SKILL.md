---
name: domain-doc
description: 도메인 문서화 - 업무 흐름, entities, API 스키마 정리
compatibility: opencode
---

# 도메인 문서화

## 주요 활동

### 1. 업무 흐름 정리
- 주요 플로우
- 상태 변화
- 사용자 인터랙션

### 2. Entities 정리
- 주요 모델
- 속성 정의
- 관계 정의

### 3. API 스키마 정리
- 엔드포인트
- Request/Response
- 에러 코드

### 4. 도메인 전문가 연계
- Domain Expert에게 정보 요청
- 검증 받기
- 문서 업데이트

## 저장 위치
`.opencode/docs/domain-knowledge.md`

## 문서 구조

```
## [도메인명]

### 업무 흐름
### 핵심 entities
### API
### 상태
```

## 운영 이슈 기록 가이드
- 어드민 작업 이슈(폼/버튼/뷰 구성)는 해당 도메인 섹션에 별도 기록
- API 응답 규칙(예: camelCase 변환)은 API 하위에 명시
