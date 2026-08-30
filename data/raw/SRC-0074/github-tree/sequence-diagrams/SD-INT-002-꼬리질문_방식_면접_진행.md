# SD-INT-002 꼬리질문 방식 면접 진행

> 대응 UC: [UC-INT-002](../use-cases/UC-INT-002-꼬리_질문_방식_면접_진행.md)

---

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant DB
    participant VectorDB
    participant LLM

    Note over User,LLM: 면접 세션 시작 완료 상태 (SD-INT-001 이후)

    Frontend-->>User: 가상 면접관 + 질문 텍스트 표시 + TTS 재생

    alt 연습 모드
        User->>Frontend: "답변 시작" 버튼 클릭
    else 실전 모드
        Note over Frontend: 5~30초 랜덤 대기 후 자동 시작
    end

    Frontend->>Frontend: 마이크 녹음 시작 (STT 실시간 변환)
    Frontend->>Frontend: 시선 추적 시작 (활성화된 경우)

    loop 답변 중 실시간 처리
        Frontend->>Frontend: STT → 텍스트 변환 (Web Speech API)
        Frontend->>Frontend: 침묵 감지 (5초 이상, 데시벨 임계값 이하)
        Frontend->>Frontend: 시선/고개 이탈 감지
    end

    User->>Frontend: 답변 완료 버튼 클릭

    Frontend->>Backend: POST /api/v1/interview-sessions/{session_id}/answers<br/>{ question_id, answer_text, answer_duration_sec,<br/>silence_events[], gaze_events[] }

    Backend->>DB: INSERT INTO interview_answers<br/>(question_id, session_id, answer_text, answer_duration_sec)
    Backend->>DB: INSERT INTO silence_events × n (침묵 이벤트)
    Backend->>DB: INSERT INTO gaze_events × n (시선 이탈 이벤트)
    DB-->>Backend: 저장 완료

    Note over Backend,LLM: 꼬리 질문 생성

    Backend->>VectorDB: 유사 자료 재검색 (답변 내용 기반)
    VectorDB-->>Backend: 관련 청크
    Backend->>LLM: 꼬리 질문 1~3개 생성 요청<br/>(이전 질문, 답변 내용, 사용자 자료)
    LLM-->>Backend: 꼬리 질문 목록 반환

    Backend->>DB: INSERT INTO interview_questions<br/>(session_id, parent_question_id, question_type="follow_up", ...)
    Backend->>Backend: TTS 오디오 생성 (다음 질문)
    Backend->>DB: UPDATE interview_questions SET tts_audio_path

    Backend-->>Frontend: 200 OK { next_question, tts_audio_url }
    Frontend-->>User: 다음 질문 표시 + TTS 재생

    Note over User,LLM: 위 흐름 반복 (모든 질문 완료까지)

    User->>Frontend: 마지막 답변 완료
    Frontend->>Backend: POST /api/v1/interview-sessions/{session_id}/complete
    Backend->>DB: UPDATE interview_sessions SET status="completed", ended_at=NOW()
    Backend-->>Frontend: 200 OK
    Frontend-->>User: 면접 종료 화면 → 리포트 생성 대기

    alt 사용자가 중도 이탈
        User->>Frontend: 세션 중단 버튼 클릭
        Frontend->>Backend: POST /api/v1/interview-sessions/{session_id}/abandon
        Backend->>DB: UPDATE interview_sessions SET status="abandoned"
        Backend-->>Frontend: 200 OK
        Frontend-->>User: 메인 화면으로 이동
    end
```

---

## 비고

- STT는 브라우저 Web Speech API 사용 (Chrome 기준)
- 침묵 감지·시선 추적은 프론트엔드에서 실시간 처리 후 답변 완료 시 일괄 전송
- 꼬리 질문은 최소 1개, 최대 3개
- 세션 완료 후 리포트 생성: [SD-INT-003-면접_리뷰_리포트.md](./SD-INT-003-면접_리뷰_리포트.md)
