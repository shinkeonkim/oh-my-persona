# SD-GMF-001 스트릭 적립 및 보상

> 대응 UC: [UC-GMF-001](../use-cases/UC-GMF-001-스트릭_적립.md), [UC-GMF-004](../use-cases/UC-GMF-004-스트릭_보상_수령.md)

---

```mermaid
sequenceDiagram
    participant Backend
    participant DB

    Note over Backend,DB: 면접 세션 completed 상태 전환 직후 자동 실행

    Backend->>DB: SELECT * FROM streaks WHERE user_id = ?
    DB-->>Backend: 현재 스트릭 정보

    Backend->>DB: SELECT * FROM streak_participation_logs<br/>WHERE user_id = ? AND participated_date = TODAY
    DB-->>Backend: 오늘 적립 여부

    alt 오늘 이미 적립됨
        Note over Backend: 중복 적립 없이 종료
    else 오늘 미적립
        Backend->>DB: INSERT INTO streak_participation_logs<br/>(user_id, participated_date=TODAY)

        alt last_participated_date = 어제
            Backend->>DB: UPDATE streaks SET<br/>current_streak = current_streak + 1,<br/>last_participated_date = TODAY
        else last_participated_date가 어제가 아님 (공백 발생)
            Backend->>DB: UPDATE streaks SET<br/>current_streak = 1,<br/>last_participated_date = TODAY
        end

        Backend->>DB: SELECT current_streak FROM streaks WHERE user_id = ?
        DB-->>Backend: 갱신된 current_streak

        alt current_streak > longest_streak
            Backend->>DB: UPDATE streaks SET longest_streak = current_streak
        end

        Note over Backend,DB: 보상 달성 여부 확인

        Backend->>DB: SELECT * FROM streak_reward_policy<br/>WHERE streak_milestone <= current_streak AND is_active = TRUE
        DB-->>Backend: 달성 가능한 보상 정책 목록

        loop 각 마일스톤에 대해
            Backend->>DB: SELECT * FROM streak_reward_logs<br/>WHERE user_id = ? AND streak_milestone = ?
            DB-->>Backend: 기존 지급 이력

            alt 이미 지급된 마일스톤
                Note over Backend: 중복 지급 없이 스킵
            else 미지급 마일스톤
                Backend->>DB: UPDATE user_feature_usages<br/>SET usage_count = usage_count + reward_amount<br/>WHERE user_id = ? AND feature_key = reward_feature_key
                Backend->>DB: INSERT INTO streak_reward_logs<br/>(user_id, streak_milestone, reward_type,<br/>reward_feature_key, reward_amount)
                Note over Backend: 보상 지급 알림 트리거
            end
        end
    end
```

---

## 비고

- 스트릭 적립은 `completed` 세션에서만 발생. `abandoned`는 적립 안 됨
- 하루 여러 번 면접 완료해도 `streak_participation_logs`의 UNIQUE 제약으로 1회만 기록
- 보상 정책은 `streak_reward_policy` 테이블에서 운영팀이 코드 배포 없이 관리
