# SD-USR-002 로그인

> 대응 UC: [UC-USR-003](../use-cases/UC-USR-003-로그인.md)

---

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant DB

    User->>Frontend: 이메일 + 비밀번호 입력 후 로그인 버튼 클릭

    Frontend->>Backend: POST /api/v1/auth/sign-in<br/>{ email, password }
    Backend->>DB: SELECT * FROM users WHERE email = ? AND deleted_at IS NULL
    DB-->>Backend: 결과 반환

    alt 이메일 없음 또는 비밀번호 불일치
        Backend-->>Frontend: 401 Unauthorized
        Frontend-->>User: "이메일 또는 비밀번호가 올바르지 않습니다"
    else 이메일 미인증 상태
        Backend-->>Frontend: 403 Forbidden { reason: "email_not_confirmed" }
        Frontend-->>User: 이메일 인증 링크 재전송 화면으로 이동
    else 프로필 미작성 상태
        Backend->>Backend: JWT 토큰 생성
        Backend-->>Frontend: 200 OK { access_token, is_profile_complete: false }
        Frontend-->>User: 프로필 작성 페이지로 이동
    else 정상 로그인
        Backend->>Backend: JWT 토큰 생성
        Backend-->>Frontend: 200 OK { access_token, is_profile_complete: true }
        Frontend->>Frontend: 토큰 저장 (localStorage / httpOnly cookie)
        Frontend-->>User: 개인화 메인 화면으로 이동
    end
```

---

## 비고

- JWT 기반 인증. 이후 모든 API 요청에 `Authorization: Bearer <token>` 헤더 포함
- `is_profile_complete = false`이면 프로필 작성 페이지로 강제 이동
