# SD-USR-003 프로필 최초 작성

> 대응 UC: [UC-USR-002](../use-cases/UC-USR-002-프로필_최초_작성.md)

---

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant DB

    Note over User,DB: 이메일 인증 완료 후 프로필 작성 페이지 진입

    User->>Frontend: 이름, 희망 직군, 현재 직업 입력 후 저장 버튼 클릭

    Frontend->>Backend: POST /api/v1/users/me/profile<br/>{ nickname, job_category, occupation }
    Backend->>DB: INSERT INTO user_profiles (user_id, nickname, job_category, occupation)
    Backend->>DB: UPDATE users SET is_profile_complete = TRUE
    DB-->>Backend: 저장 완료
    Backend-->>Frontend: 201 Created { profile }
    Frontend-->>User: 서비스 메인 화면으로 이동
```

---

## 비고

- 희망 직군(`job_category`)은 전체 사회 직군 목록에서 선택
- 프로필 정보는 이후 면접 질문 생성 시 동적으로 반영됨
- 수정은 [UC-USR-004](../use-cases/UC-USR-004-개인_정보_수정.md) 참조
