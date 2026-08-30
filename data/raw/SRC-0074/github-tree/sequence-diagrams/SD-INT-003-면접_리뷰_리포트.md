# SD-INT-003 면접 리뷰 리포트

> 대응 UC: [UC-INT-004](../use-cases/UC-INT-004-면접_리뷰_리포트_확인.md)

---

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant DB
    participant LLM

    Note over User,LLM: 면접 세션 completed 상태 전환 직후

    Backend->>DB: SELECT interview_answers, silence_events, gaze_events<br/>WHERE session_id = ?
    DB-->>Backend: 세션 전체 데이터

    Note over Backend,LLM: 비동기 리포트 생성 (백그라운드)

    Backend->>LLM: 질문별 답변 평가 요청<br/>(question_text, answer_text × n)
    LLM-->>Backend: question_feedbacks 배열 반환

    Backend->>LLM: 전반적 피드백 및 개선 제안 생성 요청<br/>(전체 답변 요약, 침묵/시선 데이터)
    LLM-->>Backend: overall_feedback, improvement_suggestions 반환

    Backend->>Backend: 침묵 분석 집계<br/>{ total_count, avg_duration, contexts[] }
    Backend->>Backend: 시선 분석 집계<br/>{ events_per_minute, total_count }

    Backend->>DB: INSERT INTO interview_reports<br/>(session_id, user_id, overall_feedback,<br/>silence_summary, gaze_summary,<br/>question_feedbacks, improvement_suggestions)
    DB-->>Backend: report_id 반환

    Frontend->>Backend: GET /api/v1/interview-sessions/{session_id}/report
    Backend->>DB: SELECT * FROM interview_reports WHERE session_id = ?
    DB-->>Backend: 리포트 데이터

    alt 리포트 아직 생성 중
        Backend-->>Frontend: 202 Accepted { status: "generating" }
        Frontend-->>User: "리포트를 생성하고 있습니다..." 로딩 표시
        Note over Frontend: 폴링 또는 WebSocket으로 완료 감지
    else 리포트 생성 완료
        Backend-->>Frontend: 200 OK { report }
        Frontend-->>User: 리뷰 리포트 화면 표시
    end

    Note over Frontend,User: 리포트 구성 항목
    Note over Frontend,User: - 질문별 답변 내용 및 평가
    Note over Frontend,User: - 침묵 발생 횟수 및 맥락
    Note over Frontend,User: - 시선 이탈 빈도 (활성화 시)
    Note over Frontend,User: - 전반적 피드백 및 개선 제안
```

---

## 비고

- 리포트 생성은 비동기. 완료 전까지 로딩 상태 표시
- 이전 세션 리포트는 세션 목록에서 재조회 가능
- `interview_reports.is_pro_report`로 요금제별 상세 수준 구분
