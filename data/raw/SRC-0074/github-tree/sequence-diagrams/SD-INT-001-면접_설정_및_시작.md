# SD-INT-001 면접 설정 및 시작

> 대응 UC: [UC-INT-001](../use-cases/UC-INT-001-면접_설정_및_시작.md)

---

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant DB
    participant VectorDB
    participant LLM

    User->>Frontend: 면접 설정 화면 진입

    Frontend->>Backend: GET /api/v1/job-descriptions
    Backend->>DB: SELECT ujd.*, jd.title, jd.company_name FROM user_job_descriptions ujd<br/>JOIN job_descriptions jd ON ujd.job_description_id = jd.id<br/>WHERE ujd.user_id = ? AND ujd.is_active = TRUE
    DB-->>Backend: 채용공고 목록 (application_status 포함)
    Backend-->>Frontend: 채용공고 목록 반환
    Frontend-->>User: 채용공고 선택 또는 직접 입력 폼 표시

    User->>Frontend: 지원 컨텍스트 선택/입력<br/>+ 면접 방식 선택 (꼬리질문 / 전체 프로세스)<br/>+ 진행 모드 선택 (연습 / 실전)

    Frontend->>Backend: POST /api/v1/interview-sessions<br/>{ user_jd_id?, company_name?, interview_stage?, job_role?,<br/>interview_mode, practice_mode }

    Backend->>DB: SELECT * FROM user_profiles WHERE user_id = ?
    Backend->>DB: INSERT INTO interview_sessions<br/>(user_id, interview_mode, practice_mode,<br/>snapshot_job_category, snapshot_occupation,<br/>snapshot_company_name, snapshot_interview_stage,<br/>snapshot_job_role, snapshot_user_jd_id,<br/>status="in_progress")
    DB-->>Backend: session_id 반환

    Note over Backend,LLM: 면접 주제 및 질문 생성 (RAG 파이프라인)

    Backend->>VectorDB: 유사 자료 검색 (사용자 이력서 청크)
    Backend->>VectorDB: 유사 자료 검색 (채용공고 청크)
    Backend->>VectorDB: 유사 자료 검색 (시스템 지식 베이스)
    VectorDB-->>Backend: 관련 청크 목록

    Backend->>DB: SELECT * FROM user_trend_summaries WHERE user_id = ? ORDER BY created_at DESC LIMIT 1
    DB-->>Backend: 경향 분석 요약

    Backend->>LLM: 면접 주제 n개 생성 요청<br/>(직군, 직업, 지원 컨텍스트, 경향 분석, 검색된 청크)
    LLM-->>Backend: 주제 목록 반환

    Backend->>DB: INSERT INTO interview_topics (session_id, topic_text, topic_order) × n

    Backend->>LLM: 각 주제별 면접 질문 생성 요청
    LLM-->>Backend: 질문 목록 반환

    Backend->>DB: INSERT INTO interview_questions (session_id, topic_id, question_text, question_type, question_order) × n
    Backend->>Backend: TTS 오디오 생성 (첫 번째 질문)
    Backend->>DB: UPDATE interview_questions SET tts_audio_path (첫 번째 질문)

    Backend-->>Frontend: 201 Created { session_id, first_question, tts_audio_url }

    Frontend-->>User: 카메라·마이크 권한 요청
    User->>Frontend: 권한 허용

    Frontend-->>User: 면접 화면 진입 (가상 면접관 + 첫 번째 질문 표시)
```

---

## 비고

- 세션 시작 시점의 `job_category`, `occupation`, `company_name`, `interview_stage`, `job_role`, `user_jd_id`는 모두 `snapshot_*` 컬럼에 저장되어 이후 프로필·채용공고 변경과 무관하게 보존됨
- 채용공고 선택 시 `snapshot_user_jd_id`로 참조. 이후 해당 북마크가 삭제되어도 스냅샷은 유지됨 (`ON DELETE SET NULL`)
- 지원 컨텍스트 없이 시작 시 프로필 정보(직군, 직업)만으로 주제 생성
- 이후 흐름: [SD-INT-002-꼬리질문_방식_면접_진행.md](./SD-INT-002-꼬리질문_방식_면접_진행.md)
