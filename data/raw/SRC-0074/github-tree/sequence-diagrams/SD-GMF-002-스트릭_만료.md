# SD-GMF-002 스트릭 만료 처리

> 대응 UC: [UC-GMF-003](../use-cases/UC-GMF-003-스트릭_만료_처리.md)

---

```mermaid
sequenceDiagram
    participant Scheduler
    participant Backend
    participant DB

    Note over Scheduler: 매일 자정(00:00) 스케줄러 실행

    Scheduler->>Backend: 스트릭 만료 처리 작업 트리거

    Backend->>DB: SELECT user_id FROM streaks<br/>WHERE last_participated_date < TODAY - 1<br/>AND current_streak > 0
    DB-->>Backend: 만료 대상 사용자 목록

    loop 각 만료 대상 사용자
        Backend->>DB: UPDATE streaks SET current_streak = 0<br/>WHERE user_id = ?
        Note over DB: longest_streak은 변경하지 않음
    end

    Backend-->>Scheduler: 처리 완료 (만료 처리된 사용자 수)
```

---

## 비고

- `longest_streak`은 초기화 대상이 아님. 역대 최장 기록은 영구 보존
- `last_participated_date`가 어제인 사용자는 만료 대상에서 제외 (오늘 면접 예정 가능)
- 만료 알림(푸시/이메일)은 선택적 구현 사항
