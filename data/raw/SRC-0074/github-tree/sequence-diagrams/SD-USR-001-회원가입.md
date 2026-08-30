# SD-USR-001 회원가입

> 대응 UC: [UC-USR-001](../use-cases/UC-USR-001-회원_가입.md)

---

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant DB
    participant Email

    User->>Frontend: 이메일 + 비밀번호 입력 후 회원가입 버튼 클릭

    Frontend->>Backend: POST /api/v1/auth/sign-up<br/>{ email, password }
    Backend->>DB: SELECT * FROM users WHERE email = ?
    DB-->>Backend: 결과 반환

    alt 이미 가입된 이메일
        Backend-->>Frontend: 409 Conflict
        Frontend-->>User: "해당 이메일로 가입된 계정이 있습니다"
    else 신규 이메일
        Backend->>DB: INSERT INTO users (email, password_hash)
        Backend->>DB: INSERT INTO email_verifications (user_id, token, expires_at)
        Backend->>Email: 인증 링크 이메일 발송 (token 포함)
        Backend-->>Frontend: 201 Created
        Frontend-->>User: "인증 이메일을 발송했습니다. 이메일을 확인해 주세요"
    end

    Note over User,Email: 사용자가 이메일 수신 후 인증 링크 클릭

    User->>Frontend: 인증 링크 클릭 (GET /confirm?token=...)
    Frontend->>Backend: GET /api/v1/auth/confirm?token=...
    Backend->>DB: SELECT * FROM email_verifications WHERE token = ?

    alt 토큰 만료 또는 없음
        Backend-->>Frontend: 400 Bad Request
        Frontend-->>User: 인증 링크 재전송 화면으로 이동
    else 유효한 토큰
        Backend->>DB: UPDATE email_verifications SET verified_at = NOW()
        Backend->>DB: UPDATE users SET is_email_verified = TRUE
        Backend-->>Frontend: 200 OK
        Frontend-->>User: 프로필 작성 페이지로 이동
    end
```

---

## 비고

- 인증 링크 만료 시 [SD-USR-002-로그인.md](./SD-USR-002-로그인.md) 이후 재전송 화면으로 유도
- 인증 완료 후 프로필 작성은 [SD-USR-003-프로필_최초_작성.md](./SD-USR-003-프로필_최초_작성.md) 참조
