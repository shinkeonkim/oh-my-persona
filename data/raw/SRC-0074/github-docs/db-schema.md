# 관계형 DB 스키마 (Relational Database Schema)

> 가상면접 웹 서비스의 관계형 데이터베이스 테이블 정의

---

## 설계 원칙

- 모든 테이블은 `id` (UUID)를 기본키로 사용
- 생성/수정 시각은 `created_at`, `updated_at`으로 통일
- 소프트 삭제가 필요한 테이블은 `deleted_at` 컬럼 추가
- 외래키는 `{참조테이블_단수명}_id` 형식으로 명명
- ENUM 값은 문서 내 별도 정의

---

## 테이블 목록

| 테이블명 | 설명 |
|---------|------|
| `users` | 사용자 계정 |
| `email_verifications` | 이메일 인증 토큰 |
| `user_profiles` | 사용자 프로필 |
| `user_consents` | 약관 및 데이터 수집 동의 |
| `subscriptions` | 요금제 구독 정보 |
| `feature_quotas` | 요금제별 기능 사용 한도 |
| `user_feature_usages` | 사용자별 기능 사용 횟수 |
| `resumes` | 이력서 메타데이터 (다형성 지원) |
| `resume_text_contents` | 자유 텍스트 입력 이력서 본문 |
| `resume_file_contents` | 파일 업로드 이력서 메타데이터 |
| `job_descriptions` | 채용공고 원문 (URL 기준 공유 자원) |
| `user_job_descriptions` | 사용자별 채용공고 연결 (북마크) |
| `user_trend_summaries` | 사용자 경향 분석 누적 요약 |
| `interview_sessions` | 가상 면접 세션 |
| `interview_topics` | 세션별 생성된 면접 주제 |
| `interview_questions` | 세션별 생성된 면접 질문 |
| `interview_answers` | 질문별 사용자 답변 |
| `silence_events` | 답변 중 침묵 감지 이벤트 |
| `gaze_events` | 답변 중 시선 이탈 이벤트 |
| `interview_reports` | 면접 세션 리뷰 리포트 |
| `streaks` | 사용자 스트릭 현황 (집계값) |
| `streak_participation_logs` | 가상 면접 참여 날짜 이력 |
| `streak_reward_policy` | 스트릭 보상 정책 (운영팀 관리) |
| `streak_reward_logs` | 스트릭 보상 지급 이력 |
| `media_recordings` | 영상·음성 녹화 파일 메타데이터 |

---

## 테이블 상세 정의

### users

사용자 계정 기본 정보. 인증 상태와 프로필 완성 여부를 별도 플래그로 관리한다.

```sql
CREATE TABLE users (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email               VARCHAR(320) NOT NULL UNIQUE,
    password_hash       VARCHAR(255) NOT NULL,
    is_email_verified   BOOLEAN NOT NULL DEFAULT FALSE,
    is_profile_complete BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ
);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `id` | UUID | 기본키 |
| `email` | VARCHAR(320) | 로그인용 이메일, 유니크 |
| `password_hash` | VARCHAR(255) | bcrypt 해시된 비밀번호 |
| `is_email_verified` | BOOLEAN | 이메일 인증 완료 여부 |
| `is_profile_complete` | BOOLEAN | 프로필 최초 작성 완료 여부 |
| `deleted_at` | TIMESTAMPTZ | 소프트 삭제 시각 |

---

### email_verifications

이메일 인증 링크 토큰 관리. 만료 시각 이후 토큰은 무효 처리된다.

```sql
CREATE TABLE email_verifications (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token       VARCHAR(255) NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    verified_at TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `token` | VARCHAR(255) | 이메일로 전송되는 일회성 토큰 |
| `expires_at` | TIMESTAMPTZ | 토큰 만료 시각 |
| `verified_at` | TIMESTAMPTZ | 실제 인증 완료 시각 (NULL이면 미인증) |

---

### user_profiles

사용자 프로필 정보. 이메일 인증 완료 후 별도 작성 절차로 생성된다.

```sql
CREATE TABLE user_profiles (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    nickname         VARCHAR(50) NOT NULL,
    job_category     VARCHAR(100) NOT NULL,  -- 희망 직군 (예: IT/개발, 마케팅, 금융)
    occupation       VARCHAR(100),           -- 현재 직업/직책
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `nickname` | VARCHAR(50) | 서비스 내 표시 이름 |
| `job_category` | VARCHAR(100) | 희망 직군. 면접 질문 생성 시 동적 반영 |
| `occupation` | VARCHAR(100) | 현재 직업/직책. 면접 질문 맥락에 활용 |

---

### user_consents

약관 동의 및 AI 학습 데이터 활용 동의 이력. 동의 버전 관리를 위해 `consent_version`을 포함한다.

```sql
CREATE TABLE user_consents (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    consent_type     VARCHAR(50) NOT NULL,   -- 'terms_of_service' | 'privacy_policy' | 'ai_training_data'
    consent_version  VARCHAR(20) NOT NULL,   -- 약관 버전 (예: '2025-01')
    is_agreed        BOOLEAN NOT NULL,
    agreed_at        TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `consent_type` | VARCHAR(50) | 동의 유형: `terms_of_service`, `privacy_policy`, `ai_training_data` |
| `consent_version` | VARCHAR(20) | 약관 버전. 버전 변경 시 재동의 유도에 활용 |
| `is_agreed` | BOOLEAN | 동의 여부 |

---

### subscriptions

사용자 요금제 구독 정보. 무료/Pro 구분 및 구독 기간을 관리한다.

```sql
CREATE TABLE subscriptions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_type       VARCHAR(20) NOT NULL DEFAULT 'free',  -- 'free' | 'pro'
    status          VARCHAR(20) NOT NULL DEFAULT 'active', -- 'active' | 'cancelled' | 'expired'
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ,   -- NULL이면 무기한 (무료 플랜)
    cancelled_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `plan_type` | VARCHAR(20) | `free` 또는 `pro` |
| `status` | VARCHAR(20) | `active`, `cancelled`, `expired` |
| `expires_at` | TIMESTAMPTZ | Pro 구독 만료 시각. 무료 플랜은 NULL |

---

### feature_quotas

요금제별 기능 사용 한도 정의. 기능 정책 변경 시 이 테이블만 수정한다.

```sql
CREATE TABLE feature_quotas (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_type    VARCHAR(20) NOT NULL,   -- 'free' | 'pro'
    feature_key  VARCHAR(100) NOT NULL,  -- 기능 식별자 (예: 'follow_up_mode', 'gaze_tracking')
    quota_type   VARCHAR(20) NOT NULL,   -- 'daily' | 'monthly' | 'unlimited' | 'disabled'
    quota_amount INTEGER,                -- quota_type이 'unlimited'/'disabled'이면 NULL
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (plan_type, feature_key)
);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `feature_key` | VARCHAR(100) | 기능 식별자. 예: `follow_up_mode`, `full_process_mode`, `gaze_tracking`, `real_mode` |
| `quota_type` | VARCHAR(20) | `daily`(일 한도), `monthly`(월 한도), `unlimited`(무제한), `disabled`(사용 불가) |
| `quota_amount` | INTEGER | 한도 횟수. `unlimited`/`disabled`이면 NULL |

---

### user_feature_usages

사용자별 기능 사용 횟수 추적. 한도 초과 여부 판단에 사용된다.

```sql
CREATE TABLE user_feature_usages (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    feature_key  VARCHAR(100) NOT NULL,
    usage_date   DATE NOT NULL,          -- 일별 집계용
    usage_count  INTEGER NOT NULL DEFAULT 0,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, feature_key, usage_date)
);
```

---

### resumes

사용자 이력서 메타데이터. `resume_type`으로 입력 방식을 구분하며, 실제 내용은 타입별 하위 테이블에 저장된다.

```sql
CREATE TABLE resumes (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    resume_type  VARCHAR(20) NOT NULL,  -- 'text' | 'file' | 'structured'
    title        VARCHAR(255) NOT NULL, -- 식별용 제목
    is_active    BOOLEAN NOT NULL DEFAULT TRUE,
    is_parsed    BOOLEAN NOT NULL DEFAULT FALSE,  -- 비동기 후처리 완료 여부
    parsed_data  JSONB,                           -- LLM 추출 구조화 데이터 (UI 표시용)
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at   TIMESTAMPTZ
);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `resume_type` | VARCHAR(20) | `text`(자유 텍스트), `file`(파일 업로드), `structured`(정규화 입력, 추후 구현) |
| `is_active` | BOOLEAN | 비활성화 시 면접 질문 생성에서 제외 |
| `is_parsed` | BOOLEAN | 비동기 후처리(LLM 파싱 + 벡터 DB 저장) 완료 여부. `false`이면 UI에 "분석 중..." 표시 |
| `parsed_data` | JSONB | LLM이 추출한 구조화 데이터. 예: `{"skills": ["Python"], "total_experience_years": 3, "summary": "..."}` |

---

### resume_text_contents

`resume_type = 'text'`인 이력서의 자유 텍스트 본문.

```sql
CREATE TABLE resume_text_contents (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id  UUID NOT NULL UNIQUE REFERENCES resumes(id) ON DELETE CASCADE,
    content    TEXT NOT NULL,  -- 사용자가 입력한 자유 텍스트 원문
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

### resume_file_contents

`resume_type = 'file'`인 이력서의 파일 메타데이터.

```sql
CREATE TABLE resume_file_contents (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id         UUID NOT NULL UNIQUE REFERENCES resumes(id) ON DELETE CASCADE,
    original_filename VARCHAR(255) NOT NULL,
    storage_path      VARCHAR(500) NOT NULL,  -- S3 등 오브젝트 스토리지 경로
    file_size_bytes   BIGINT,
    mime_type         VARCHAR(100),           -- 'application/pdf' | 'application/vnd.openxmlformats...'
    extracted_text    TEXT,                   -- 파일에서 파싱·추출된 텍스트 원문
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `storage_path` | VARCHAR(500) | 오브젝트 스토리지 경로 |
| `extracted_text` | TEXT | 파일 파싱 후 추출된 텍스트. 벡터 임베딩 생성 원본 |

---

### job_descriptions

URL 기준으로 공유되는 채용공고 원문. 동일 URL을 여러 사용자가 등록해도 원문은 1행만 존재한다.

```sql
CREATE TABLE job_descriptions (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_url   VARCHAR(2048) NOT NULL UNIQUE,  -- 크롤링 원본 URL (중복 방지 기준)
    title        VARCHAR(255),                   -- 크롤링·파싱으로 추출된 공고 제목
    company_name VARCHAR(255),                   -- 크롤링·파싱으로 추출된 기업명
    content_text TEXT,                           -- 크롤링으로 추출된 원문 텍스트
    parsed_data  JSONB,                          -- LLM 추출 구조화 데이터
    is_parsed    BOOLEAN NOT NULL DEFAULT FALSE, -- 비동기 후처리 완료 여부
    crawled_at   TIMESTAMPTZ,                    -- 최초 크롤링 시각
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `source_url` | VARCHAR(2048) | 채용공고 원본 URL. UNIQUE 제약으로 중복 크롤링 방지 |
| `content_text` | TEXT | 크롤링으로 추출된 원문 텍스트. 벡터 임베딩 생성 원본 |
| `parsed_data` | JSONB | LLM이 추출한 구조화 데이터. 예: `{"requirements": [...], "preferred": [...], "role_summary": "..."}` |
| `is_parsed` | BOOLEAN | 비동기 후처리(LLM 파싱 + 벡터 DB 저장) 완료 여부 |
| `crawled_at` | TIMESTAMPTZ | 최초 크롤링 완료 시각. NULL이면 크롤링 대기 중 |

---

### user_job_descriptions

사용자별 채용공고 북마크. 동일 채용공고 원문(`job_descriptions`)을 여러 사용자가 각자 연결할 수 있다. 지원 상태는 이 테이블에서 함께 관리한다.

```sql
CREATE TABLE user_job_descriptions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_description_id  UUID NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE,
    custom_title        VARCHAR(255),            -- 사용자가 지정한 식별용 제목 (선택)
    application_status  VARCHAR(20) NOT NULL DEFAULT 'planned',  -- 'planned' | 'saved' | 'applied'
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, job_description_id)
);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `job_description_id` | UUID | 공유 원문(`job_descriptions`) 참조 |
| `custom_title` | VARCHAR(255) | 사용자가 직접 지정한 식별용 제목. NULL이면 원문의 `title` 사용 |
| `application_status` | VARCHAR(20) | 지원 상태: `planned`(지원 예정), `saved`(관심 저장), `applied`(지원 완료). 기본값 `planned` |
| `is_active` | BOOLEAN | 비활성화 시 면접 질문 생성에서 제외 |
| `UNIQUE(user_id, job_description_id)` | — | 동일 사용자가 같은 공고를 중복 북마크하는 것을 방지 |

---

### user_trend_summaries

시스템이 분석한 사용자의 최근 경향을 자연어로 누적 저장한다.

```sql
CREATE TABLE user_trend_summaries (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    summary     TEXT NOT NULL,   -- LLM이 생성한 자연어 경향 요약
    basis       JSONB,           -- 요약 근거 (참조한 document_id 목록 등)
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `summary` | TEXT | 자연어 형식의 경향 분석 요약 |
| `basis` | JSONB | 요약 생성에 참조된 문서 ID 목록 등 근거 데이터 |

---

### interview_sessions

가상 면접 세션 단위 정보.

```sql
CREATE TABLE interview_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    interview_mode  VARCHAR(30) NOT NULL,   -- 'follow_up' | 'full_process'
    practice_mode   VARCHAR(20) NOT NULL,   -- 'practice' | 'real'
    status          VARCHAR(20) NOT NULL DEFAULT 'in_progress',  -- 'in_progress' | 'completed' | 'abandoned'
    -- 세션 시작 시점의 사용자 컨텍스트 스냅샷
    snapshot_job_category       VARCHAR(100),
    snapshot_occupation         VARCHAR(100),
    snapshot_company_name       VARCHAR(255),   -- 지원 기업명 스냅샷 (자유 입력 포함)
    snapshot_interview_stage    VARCHAR(100),   -- 면접 단계 스냅샷 (예: 1차 면접, 임원 면접)
    snapshot_job_role           VARCHAR(100),   -- 지원 직무 스냅샷
    snapshot_user_jd_id         UUID REFERENCES user_job_descriptions(id) ON DELETE SET NULL,  -- 선택된 채용공고 참조
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at        TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `interview_mode` | VARCHAR(30) | `follow_up`(꼬리질문 방식), `full_process`(전체 프로세스 방식) |
| `practice_mode` | VARCHAR(20) | `practice`(연습 모드), `real`(실전 모드) |
| `status` | VARCHAR(20) | `in_progress`, `completed`, `abandoned` |
| `snapshot_job_category` | VARCHAR(100) | 세션 시작 시점의 직군 스냅샷. 이후 프로필 변경과 무관하게 보존 |
| `snapshot_occupation` | VARCHAR(100) | 세션 시작 시점의 직업 스냅샷 |
| `snapshot_company_name` | VARCHAR(255) | 지원 기업명 스냅샷. 직접 입력 또는 채용공고에서 추출 |
| `snapshot_interview_stage` | VARCHAR(100) | 면접 단계 스냅샷. 예: `1차 면접`, `임원 면접` |
| `snapshot_job_role` | VARCHAR(100) | 지원 직무 스냅샷 |
| `snapshot_user_jd_id` | UUID | 세션 시작 시 선택된 `user_job_descriptions` 참조. 삭제 시 NULL로 유지 |

---

### interview_topics

세션별 LLM이 생성한 면접 주제 목록.

```sql
CREATE TABLE interview_topics (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id  UUID NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    topic_text  TEXT NOT NULL,       -- 생성된 주제 텍스트
    topic_order INTEGER NOT NULL,    -- 주제 순서
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

### interview_questions

세션 내 각 질문 정보. 꼬리 질문은 `parent_question_id`로 계층 구조를 표현한다.

```sql
CREATE TABLE interview_questions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    topic_id            UUID REFERENCES interview_topics(id),
    parent_question_id  UUID REFERENCES interview_questions(id),  -- 꼬리 질문인 경우 부모 질문 참조
    question_text       TEXT NOT NULL,
    question_type       VARCHAR(30) NOT NULL,  -- 'initial' | 'follow_up' | 'self_intro' | 'motivation' | 'general'
    question_order      INTEGER NOT NULL,
    tts_audio_path      VARCHAR(500),          -- 서버에서 생성된 TTS 오디오 파일 경로
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `parent_question_id` | UUID | 꼬리 질문의 경우 원본 질문 ID 참조 |
| `question_type` | VARCHAR(30) | `initial`(첫 질문), `follow_up`(꼬리 질문), `self_intro`(자기소개), `motivation`(지원동기), `general`(기타) |
| `tts_audio_path` | VARCHAR(500) | 서버 생성 TTS 오디오 파일 경로 |

---

### interview_answers

질문별 사용자 답변 정보.

```sql
CREATE TABLE interview_answers (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id         UUID NOT NULL UNIQUE REFERENCES interview_questions(id) ON DELETE CASCADE,
    session_id          UUID NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    answer_text         TEXT,                  -- STT 변환 텍스트
    answer_duration_sec INTEGER,               -- 답변 소요 시간 (초)
    random_wait_sec     INTEGER,               -- 실전 모드 랜덤 대기 시간 (초)
    started_at          TIMESTAMPTZ,
    ended_at            TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `answer_text` | TEXT | STT로 변환된 답변 텍스트 |
| `random_wait_sec` | INTEGER | 실전 모드에서 적용된 랜덤 대기 시간 |

---

### silence_events

답변 중 침묵(5초 이상, 특정 데시벨 이하) 감지 이벤트.

```sql
CREATE TABLE silence_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    answer_id       UUID NOT NULL REFERENCES interview_answers(id) ON DELETE CASCADE,
    session_id      UUID NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    silence_start_sec  FLOAT NOT NULL,   -- 답변 시작 기준 침묵 시작 시각 (초)
    silence_duration_sec FLOAT NOT NULL, -- 침묵 지속 시간 (초)
    context_text    TEXT,                -- 침묵 직전 STT 텍스트 (맥락 파악용)
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `silence_start_sec` | FLOAT | 답변 시작 기준 침묵 발생 시각 |
| `context_text` | TEXT | 침묵 직전까지의 STT 텍스트. 어떤 맥락에서 멈췄는지 파악에 활용 |

---

### gaze_events

답변 중 시선/고개 이탈 감지 이벤트.

```sql
CREATE TABLE gaze_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    answer_id       UUID NOT NULL REFERENCES interview_answers(id) ON DELETE CASCADE,
    session_id      UUID NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    event_type      VARCHAR(30) NOT NULL,  -- 'head_turn' | 'gaze_away'
    occurred_at_sec FLOAT NOT NULL,        -- 답변 시작 기준 발생 시각 (초)
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `event_type` | VARCHAR(30) | `head_turn`(고개 돌림), `gaze_away`(시선 이탈) |
| `occurred_at_sec` | FLOAT | 답변 시작 기준 이벤트 발생 시각 |

---

### interview_reports

면접 세션 종료 후 생성되는 리뷰 리포트.

```sql
CREATE TABLE interview_reports (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id              UUID NOT NULL UNIQUE REFERENCES interview_sessions(id) ON DELETE CASCADE,
    user_id                 UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    overall_feedback        TEXT,           -- 전반적인 피드백 (LLM 생성)
    silence_summary         JSONB,          -- 침묵 분석 요약 { total_count, avg_duration, contexts[] }
    gaze_summary            JSONB,          -- 시선 분석 요약 { events_per_minute, total_count }
    question_feedbacks      JSONB,          -- 질문별 피드백 배열
    improvement_suggestions TEXT,           -- 개선 제안 (LLM 생성)
    is_pro_report           BOOLEAN NOT NULL DEFAULT FALSE,  -- Pro 상세 리포트 여부
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `silence_summary` | JSONB | 침묵 총 횟수, 평균 지속 시간, 맥락 목록 |
| `gaze_summary` | JSONB | 분당 시선 이탈 횟수, 총 이탈 횟수 |
| `question_feedbacks` | JSONB | 질문별 답변 평가 배열 |
| `is_pro_report` | BOOLEAN | Pro 요금제 상세 리포트 여부 |

---

### streaks

사용자 스트릭 집계값. 현재 연속 일수와 역대 최장 기록만 보관한다. 날짜 이력은 `streak_participation_logs`에서 별도 관리한다.

```sql
CREATE TABLE streaks (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    current_streak         INTEGER NOT NULL DEFAULT 0,
    longest_streak         INTEGER NOT NULL DEFAULT 0,
    last_participated_date DATE,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `current_streak` | INTEGER | 현재 연속 참여 일수 |
| `longest_streak` | INTEGER | 역대 최장 연속 참여 일수. 만료 시에도 초기화되지 않음 |
| `last_participated_date` | DATE | 마지막 면접 참여 날짜. 만료 판단 기준 |

---

### streak_participation_logs

가상 면접에 참여한 날짜 이력. 달력 뷰 시각화 전용 테이블로, 스트릭 적립 시 동시에 기록된다.

```sql
CREATE TABLE streak_participation_logs (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id            UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    participated_date  DATE NOT NULL,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, participated_date)
);

CREATE INDEX idx_streak_participation_logs_user_date
    ON streak_participation_logs (user_id, participated_date DESC);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `participated_date` | DATE | 면접 참여 날짜 (1일 1행, 중복 불가) |

- `UNIQUE (user_id, participated_date)` 제약으로 하루에 여러 번 면접해도 1행만 기록됨
- 달력 조회: `SELECT participated_date FROM streak_participation_logs WHERE user_id = :id ORDER BY participated_date DESC`

---

### streak_reward_policy

스트릭 보상 정책. 운영팀이 코드 배포 없이 마일스톤·보상 유형·지급량을 동적으로 관리한다.

```sql
CREATE TABLE streak_reward_policy (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    streak_milestone   INTEGER NOT NULL UNIQUE,  -- 보상 지급 기준 연속 일수
    reward_type        VARCHAR(50) NOT NULL,      -- 'feature_usage_count'
    reward_feature_key VARCHAR(100) NOT NULL,     -- 보상 대상 기능 키
    reward_amount      INTEGER NOT NULL,          -- 지급 횟수
    is_active          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `streak_milestone` | INTEGER | 보상 트리거 연속 일수 (예: 7, 14, 30, 60) |
| `reward_type` | VARCHAR(50) | 보상 유형. 현재는 `feature_usage_count` |
| `reward_feature_key` | VARCHAR(100) | 보상 대상 기능 키 (예: `gaze_tracking`, `real_mode`) |
| `reward_amount` | INTEGER | 지급 횟수 |
| `is_active` | BOOLEAN | `false`이면 해당 마일스톤 보상 비활성화 |

---

### streak_reward_logs

스트릭 달성 보상 지급 이력.

```sql
CREATE TABLE streak_reward_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    streak_milestone INTEGER NOT NULL,   -- 보상 지급 기준 스트릭 일수 (예: 7, 30)
    reward_type     VARCHAR(50) NOT NULL, -- 'feature_usage_count'
    reward_feature_key VARCHAR(100),      -- 보상 대상 기능 키
    reward_amount   INTEGER NOT NULL,     -- 지급된 사용 횟수
    granted_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `streak_milestone` | INTEGER | 보상 트리거 스트릭 일수 (예: 7일, 30일) |
| `reward_type` | VARCHAR(50) | 현재는 `feature_usage_count` (기능 사용 횟수 지급) |
| `reward_feature_key` | VARCHAR(100) | 보상으로 지급되는 기능 키 |

---

### media_recordings

면접 중 수집된 영상·음성 녹화 파일 메타데이터. 실제 파일은 오브젝트 스토리지에 저장된다.

```sql
CREATE TABLE media_recordings (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    media_type          VARCHAR(10) NOT NULL,   -- 'video' | 'audio'
    storage_path        VARCHAR(500) NOT NULL,
    duration_sec        INTEGER,
    file_size_bytes     BIGINT,
    ai_training_consent BOOLEAN NOT NULL DEFAULT FALSE,  -- 수집 시점의 동의 여부 스냅샷
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `media_type` | VARCHAR(10) | `video` 또는 `audio` |
| `ai_training_consent` | BOOLEAN | 녹화 시점의 AI 학습 동의 여부 스냅샷. 이후 동의 철회와 무관하게 보존 |

---

## ERD 관계 요약

```
users
 ├── email_verifications     (1:N)
 ├── user_profiles           (1:1)
 ├── user_consents           (1:N)
 ├── subscriptions           (1:N)
 ├── user_feature_usages     (1:N)
 ├── resumes                 (1:N)
 │    ├── resume_text_contents  (1:1, type='text')
 │    └── resume_file_contents  (1:1, type='file')
 ├── user_job_descriptions   (1:N) ──→ job_descriptions (공유 원문, N:M 중간 테이블)
 │    └── interview_sessions  (1:N, snapshot_user_jd_id 참조)
 ├── user_trend_summaries    (1:N)
 ├── streaks                      (1:1)
 ├── streak_participation_logs    (1:N)
 ├── streak_reward_policy         (시스템 공통)
 ├── streak_reward_logs           (1:N)
 └── interview_sessions      (1:N)
      ├── interview_topics    (1:N)
      ├── interview_questions (1:N)
      │    └── interview_questions (self-ref: follow_up)
      ├── interview_answers   (1:N)
      │    ├── silence_events (1:N)
      │    └── gaze_events    (1:N)
      ├── interview_reports   (1:1)
      └── media_recordings    (1:N)
```
