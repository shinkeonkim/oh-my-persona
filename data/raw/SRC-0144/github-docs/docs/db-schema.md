# 매일메일 DB 스키마

---

## 1. users

사용자 프로필. `auth.users`와 1:1 관계.

| Column | Type | Nullable | Default | 비고 |
|--------|------|----------|---------|------|
| id | uuid | NO | gen_random_uuid() | PK, FK → auth.users(id) ON DELETE CASCADE |
| name | text | NO | | 표시 이름 |
| email | text | NO | | unique |
| role | text | YES | null | 직무 (backend, frontend, ...) |
| target_companies | text[] | YES | '{}' | 목표 회사 ID 배열 (최대 3) |
| daily_question_count | int | NO | 3 | 1, 2, 3, 5 |
| notification_time | time | NO | '08:00' | 알림 시간 |
| plan | text | NO | 'free' | free, premium, pro |
| onboarding_completed | boolean | NO | false | |
| created_at | timestamptz | NO | now() | |
| updated_at | timestamptz | NO | now() | |

---

## 2. notification_settings

알림 설정 (users 1:1)

| Column | Type | Nullable | Default | 비고 |
|--------|------|----------|---------|------|
| id | uuid | NO | gen_random_uuid() | PK |
| user_id | uuid | NO | | FK → users(id) ON DELETE CASCADE, unique |
| alimtalk | boolean | NO | true | 카카오 알림톡 |
| email | boolean | NO | true | 이메일 알림 |
| created_at | timestamptz | NO | now() | |

---

## 3. questions

면접 질문 풀

| Column | Type | Nullable | Default | 비고 |
|--------|------|----------|---------|------|
| id | uuid | NO | gen_random_uuid() | PK |
| content_ko | text | NO | | 한국어 질문 |
| type | text | NO | | behavioral, technical, system_design, culture_fit |
| answer_type | text | NO | 'text' | text, video |
| companies | text[] | NO | '{}' | 연관 회사 ID 배열 |
| difficulty | int | NO | 1 | 1~5 |
| tags | text[] | NO | '{}' | |
| created_at | timestamptz | NO | now() | |

---

## 4. daily_question_sets

일일 질문 세트 (사용자별 생성)

| Column | Type | Nullable | Default | 비고 |
|--------|------|----------|---------|------|
| id | uuid | NO | gen_random_uuid() | PK |
| user_id | uuid | NO | | FK → users(id) |
| date | date | NO | | |
| question_ids | uuid[] | NO | | FK → questions(id) 배열 |
| completed_count | int | NO | 0 | |
| created_at | timestamptz | NO | now() | |

**unique** (user_id, date)

---

## 5. answers

사용자 답변

| Column | Type | Nullable | Default | 비고 |
|--------|------|----------|---------|------|
| id | uuid | NO | gen_random_uuid() | PK |
| user_id | uuid | NO | | FK → users(id) |
| question_id | uuid | NO | | FK → questions(id) |
| daily_set_id | uuid | YES | | FK → daily_question_sets(id) |
| content | text | YES | | 텍스트 답변 |
| video_url | text | YES | | 영상 답변 storage URL |
| status | text | NO | 'submitted' | submitted, evaluating, evaluated |
| created_at | timestamptz | NO | now() | |

---

## 6. evaluations

AI 평가 결과 (answers 1:1)

| Column | Type | Nullable | Default | 비고 |
|--------|------|----------|---------|------|
| id | uuid | NO | gen_random_uuid() | PK |
| answer_id | uuid | NO | | FK → answers(id) ON DELETE CASCADE, unique |
| overall_score | int | NO | | 1~10 |
| dimensions | jsonb | NO | | { "이름": { score, feedback } } |
| star_analysis | jsonb | NO | | STAR 분석 객체 |
| strengths | text[] | NO | | |
| improvements | text[] | NO | | |
| model_answer_highlights | text[] | NO | | |
| improved_answer_suggestion | text | NO | | |
| voice_analysis | jsonb | YES | | 영상 답변 전용 |
| video_analysis | jsonb | YES | | 영상 답변 전용 |
| transcript | text | YES | | STT 변환 텍스트 |
| created_at | timestamptz | NO | now() | |

---

## 7. streaks

연속 학습 기록 (users 1:1)

| Column | Type | Nullable | Default | 비고 |
|--------|------|----------|---------|------|
| id | uuid | NO | gen_random_uuid() | PK |
| user_id | uuid | NO | | FK → users(id), unique |
| current_streak | int | NO | 0 | |
| longest_streak | int | NO | 0 | |
| total_days | int | NO | 0 | |
| freeze_remaining | int | NO | 2 | |
| last_completed_date | date | YES | | |
| created_at | timestamptz | NO | now() | |

---

## 8. streak_heatmap

히트맵 데이터 (일별 활동량)

| Column | Type | Nullable | Default | 비고 |
|--------|------|----------|---------|------|
| id | uuid | NO | gen_random_uuid() | PK |
| user_id | uuid | NO | | FK → users(id) |
| date | date | NO | | |
| count | int | NO | 0 | 해당일 완료 문제 수 |

**unique** (user_id, date)

---

## 9. subscriptions

구독 정보

| Column | Type | Nullable | Default | 비고 |
|--------|------|----------|---------|------|
| id | uuid | NO | gen_random_uuid() | PK |
| user_id | uuid | NO | | FK → users(id), unique |
| plan | text | NO | 'free' | |
| stripe_customer_id | text | YES | | |
| stripe_subscription_id | text | YES | | |
| next_billing_date | timestamptz | YES | | |
| created_at | timestamptz | NO | now() | |

---

## RLS 정책 요약

모든 테이블에 RLS 활성화:
- 사용자는 자신의 데이터만 CRUD 가능 (`auth.uid() = user_id`)
- `questions` 테이블은 authenticated 사용자에게 SELECT 허용
- `constants` (companies, roles)는 별도 테이블 또는 앱 코드 내 상수
