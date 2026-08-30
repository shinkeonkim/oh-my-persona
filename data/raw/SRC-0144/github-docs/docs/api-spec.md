# 매일메일 API 명세서 (v1)

모든 엔드포인트는 `/api/v1` 접두사를 사용합니다.  
인증이 필요한 엔드포인트는 `Authorization: Bearer <token>` 헤더를 포함해야 합니다.

---

## 공통 규격

### 에러 응답 형식

모든 에러 응답은 동일한 JSON 구조를 따릅니다:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "사람이 읽을 수 있는 에러 메시지",
    "details?": {}
  }
}
```

#### HTTP 상태 코드별 에러

| 상태 코드 | 코드 | 설명 | 예시 |
|-----------|------|------|------|
| `400` Bad Request | `VALIDATION_ERROR` | 요청 데이터가 유효하지 않음 | 필수 필드 누락, 잘못된 형식 |
| `400` Bad Request | `INVALID_INPUT` | 비즈니스 규칙 위반 | 최대 3개 회사만 선택 가능 |
| `401` Unauthorized | `UNAUTHORIZED` | 인증 토큰 없음 또는 만료 | 토큰 미포함, 만료된 JWT |
| `401` Unauthorized | `INVALID_TOKEN` | 유효하지 않은 토큰 | 변조된 JWT |
| `403` Forbidden | `FORBIDDEN` | 권한 부족 | 프리미엄 전용 기능 접근 |
| `403` Forbidden | `PLAN_LIMIT_EXCEEDED` | 플랜 제한 초과 | 무료 플랜 일일 한도 |
| `404` Not Found | `NOT_FOUND` | 리소스를 찾을 수 없음 | 존재하지 않는 질문 ID |
| `409` Conflict | `ALREADY_EXISTS` | 리소스 중복 | 이미 제출된 답변 |
| `429` Too Many Requests | `RATE_LIMITED` | 요청 횟수 초과 | API 호출 제한 |
| `500` Internal Server Error | `INTERNAL_ERROR` | 서버 내부 오류 | 예기치 못한 에러 |

**에러 응답 예시:**

`400` — 유효성 검사 실패:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "답변은 최소 100자 이상이어야 합니다.",
    "details": {
      "field": "content",
      "minLength": 100,
      "actualLength": 42
    }
  }
}
```

`401` — 인증 실패:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "인증 토큰이 만료되었습니다. 다시 로그인해주세요."
  }
}
```

`404` — 리소스 없음:
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "요청한 질문을 찾을 수 없습니다."
  }
}
```

`500` — 서버 오류:
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
  }
}
```

### 페이지네이션 공통 규격

목록 API는 커서 기반이 아닌 **오프셋 기반 페이지네이션**을 사용합니다.

#### 요청 파라미터 (Query Params)

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `page` | number | `1` | 현재 페이지 (1부터 시작) |
| `limit` | number | `10` | 페이지당 항목 수 (최대 50) |

#### 응답 형식

모든 페이지네이션 응답은 `PaginatedResponse<T>` 래퍼를 사용합니다:

```json
{
  "items": [T],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 45,
    "totalPages": 5,
    "hasNext": true,
    "hasPrev": false
  }
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `items` | T[] | 현재 페이지의 데이터 배열 |
| `pagination.page` | number | 현재 페이지 번호 |
| `pagination.limit` | number | 페이지당 항목 수 |
| `pagination.total` | number | 전체 항목 수 |
| `pagination.totalPages` | number | 전체 페이지 수 |
| `pagination.hasNext` | boolean | 다음 페이지 존재 여부 |
| `pagination.hasPrev` | boolean | 이전 페이지 존재 여부 |

---

## 1. 인증 (Auth)

### `POST /api/v1/auth/signup`
이메일 회원가입

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```
**Response:** `201`
```json
{
  "user": { "id": "string", "email": "string" },
  "token": "string"
}
```

### `POST /api/v1/auth/login`
이메일 로그인

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```
**Response:** `200`
```json
{
  "user": { "id": "string", "email": "string" },
  "token": "string"
}
```

### `POST /api/v1/auth/oauth`
소셜 로그인 (Google, Kakao)

**Request Body:**
```json
{
  "provider": "google" | "kakao",
  "accessToken": "string"
}
```
**Response:** `200` — 동일한 user + token 응답

### `POST /api/v1/auth/logout`
🔒 로그아웃. **Response:** `204`

---

## 2. 사용자 (Users)

### `GET /api/v1/users/me`
🔒 현재 로그인한 사용자 프로필 조회

**Response:** `200`
```json
{
  "id": "string",
  "name": "string",
  "email": "string",
  "role": "string",
  "targetCompanies": ["string"],
  "dailyQuestionCount": 3,
  "notificationTime": "08:00",
  "plan": "free" | "premium" | "pro",
  "onboardingCompleted": true
}
```

### `PATCH /api/v1/users/me`
🔒 프로필 업데이트 (이름, 일일 질문 수 등)

**Request Body:** (부분 업데이트)
```json
{
  "name?": "string",
  "dailyQuestionCount?": 1 | 2 | 3 | 5,
  "notificationTime?": "HH:mm"
}
```
**Response:** `200` — 업데이트된 User 객체

### `PUT /api/v1/users/me/onboarding`
🔒 온보딩 설정 저장

**Request Body:**
```json
{
  "role": "string",
  "targetCompanies": ["string"],
  "dailyQuestionCount": 3,
  "notificationTime": "08:00"
}
```
**Response:** `200` — 업데이트된 User 객체

---

## 3. 알림 설정 (Notifications)

### `GET /api/v1/users/me/notifications`
🔒 알림 설정 조회

**Response:** `200`
```json
{
  "alimtalk": true,
  "email": true,
  "notificationTime": "08:00"
}
```

### `PATCH /api/v1/users/me/notifications`
🔒 알림 설정 업데이트

**Request Body:**
```json
{
  "alimtalk?": true,
  "email?": false,
  "notificationTime?": "09:00"
}
```

---

## 4. 오늘의 질문 (Daily Questions)

### `GET /api/v1/daily-questions`
🔒 오늘의 질문 세트 조회

**Query Params:** 없음 (날짜는 서버에서 결정)

**Response:** `200`
```json
{
  "id": "string",
  "date": "2025-01-15",
  "questions": [Question],
  "completedCount": 1
}
```

---

## 5. 질문 (Questions)

### `GET /api/v1/questions`
🔒 질문 목록 (페이지네이션)

사용자 설정(직무, 목표 회사)에 맞는 질문 풀을 탐색합니다.

**Query Params:**
| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `page` | number | `1` | 페이지 번호 |
| `limit` | number | `10` | 페이지당 항목 수 |
| `type?` | string | — | behavioral, technical, system_design, culture_fit |
| `difficulty?` | number | — | 1~5 |
| `answerType?` | string | — | text, video |

**Response:** `200` — `PaginatedResponse<Question>`
```json
{
  "items": [
    {
      "id": "string",
      "contentKo": "string",
      "type": "behavioral",
      "answerType": "text",
      "companies": ["naver", "kakao"],
      "difficulty": 3,
      "tags": ["teamwork"]
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 48,
    "totalPages": 5,
    "hasNext": true,
    "hasPrev": false
  }
}
```

### `GET /api/v1/questions/:id`
🔒 개별 질문 상세 조회

**Response:** `200` — Question 객체

---

## 6. 답변 (Answers)

### `POST /api/v1/answers`
🔒 텍스트 답변 제출

**Request Body:**
```json
{
  "questionId": "string",
  "content": "string"
}
```
**Response:** `201`
```json
{
  "id": "string",
  "questionId": "string",
  "status": "evaluating"
}
```

### `POST /api/v1/answers/video`
🔒 영상 답변 제출 (multipart/form-data)

**Request Body:**
- `questionId`: string
- `video`: File (video/webm)

**Response:** `201`
```json
{
  "id": "string",
  "questionId": "string",
  "status": "evaluating"
}
```

### `GET /api/v1/answers`
🔒 답변 이력 목록 (페이지네이션)

**Query Params:**
| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `page` | number | `1` | 페이지 번호 |
| `limit` | number | `10` | 페이지당 항목 수 |

**Response:** `200` — `PaginatedResponse<Answer>`
```json
{
  "items": [Answer],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 45,
    "totalPages": 5,
    "hasNext": true,
    "hasPrev": false
  }
}
```

### `GET /api/v1/answers/:id`
🔒 개별 답변 + 평가 결과 조회

**Response:** `200` — Answer 객체 (evaluation 포함)

---

## 7. 평가 (Evaluations)

### `GET /api/v1/answers/:id/evaluation`
🔒 답변에 대한 AI 평가 결과 조회

**Response:** `200`
```json
{
  "overallScore": 7,
  "dimensions": {
    "기술적 정확성": { "score": 8, "feedback": "string" },
    "구조 (STAR)": { "score": 6, "feedback": "string" },
    "구체성": { "score": 7, "feedback": "string" },
    "관련성": { "score": 8, "feedback": "string" },
    "결과 정량화": { "score": 5, "feedback": "string" }
  },
  "starAnalysis": {
    "situationPresent": true,
    "taskPresent": true,
    "actionPresent": true,
    "actionDetailLevel": 3,
    "resultPresent": true,
    "resultQuantified": false
  },
  "strengths": ["string"],
  "improvements": ["string"],
  "modelAnswerHighlights": ["string"],
  "improvedAnswerSuggestion": "string",
  "voiceAnalysis?": { ... },
  "videoAnalysis?": { ... },
  "transcript?": "string"
}
```

---

## 8. 스트릭 (Streak)

### `GET /api/v1/streak`
🔒 현재 사용자의 스트릭 정보

**Response:** `200`
```json
{
  "currentStreak": 12,
  "longestStreak": 28,
  "totalDays": 45,
  "freezeRemaining": 1,
  "lastCompletedDate": "2025-01-15",
  "heatmapData": { "2025-01-15": 3, "2025-01-14": 2, ... }
}
```

### `POST /api/v1/streak/freeze`
🔒 스트릭 프리즈 사용

**Response:** `200`
```json
{
  "freezeRemaining": 0,
  "currentStreak": 12
}
```

---

## 9. 통계 (Stats)

### `GET /api/v1/stats`
🔒 대시보드 통계 (배지, 평균 점수, 이번 주, 총 답변)

**Response:** `200`
```json
{
  "badges": 3,
  "averageScore": 7.2,
  "weeklyCount": 12,
  "totalAnswers": 45
}
```

---

## 10. 구독 (Subscription)

### `GET /api/v1/subscription`
🔒 현재 구독 정보

**Response:** `200`
```json
{
  "plan": "free",
  "planLabel": "무료 플랜",
  "description": "일 1문제, 기본 피드백",
  "nextBillingDate": null,
  "upgradePriceMonthly": 9900
}
```

### `POST /api/v1/subscription/upgrade`
🔒 구독 업그레이드 (결제 연동)

---

## 11. 상수 데이터 (Constants)

### `GET /api/v1/constants/companies`
회사 목록

**Response:** `200`
```json
[{ "id": "naver", "name": "네이버", "logo": "🟢" }, ...]
```

### `GET /api/v1/constants/roles`
직무 목록

**Response:** `200`
```json
[{ "id": "backend", "name": "백엔드 개발" }, ...]
```
