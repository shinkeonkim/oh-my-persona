# SD-DOC-002 채용공고 등록

> 대응 UC: [UC-DOC-002](../use-cases/UC-DOC-002-채용공고_등록_및_관리.md)

---

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant DB
    participant Crawler
    participant LLM
    participant VectorDB

    User->>Frontend: 채용공고 URL 입력 (+ 선택: custom_title)
    Frontend->>Backend: POST /api/v1/job-descriptions<br/>{ source_url, custom_title? }

    Backend->>DB: SELECT * FROM job_descriptions WHERE source_url = ?
    DB-->>Backend: 결과 반환

    alt 동일 사용자가 이미 북마크한 URL
        Backend-->>Frontend: 409 Conflict
        Frontend-->>User: "이미 등록된 채용공고입니다"

    else URL이 job_descriptions에 이미 존재 (다른 사용자가 등록)
        Backend->>DB: INSERT INTO user_job_descriptions<br/>(user_id, job_description_id, custom_title,<br/>application_status='planned', is_active=true)
        Backend-->>Frontend: 201 Created { user_jd_id, is_parsed: true }
        Frontend-->>User: 목록에 추가 (이미 분석 완료 상태)

    else 신규 URL
        Backend->>DB: INSERT INTO job_descriptions (source_url, is_parsed=false)
        Backend->>DB: INSERT INTO user_job_descriptions<br/>(user_id, job_description_id, custom_title,<br/>application_status='planned', is_active=true)
        Backend-->>Frontend: 201 Created { user_jd_id, is_parsed: false }
        Frontend-->>User: 목록에 추가 ("분석 중..." 상태 표시)

        Note over Backend,VectorDB: 비동기 후처리 (백그라운드 워커)

        Backend->>Crawler: 크롤링 요청 (source_url)
        Crawler-->>Backend: content_text, title, company_name 반환

        alt 크롤링 실패
            Backend->>DB: UPDATE job_descriptions SET crawled_at = NULL (실패 표기)
            Frontend-->>User: "공고 정보를 불러오지 못했습니다"
        else 크롤링 성공
            Backend->>DB: UPDATE job_descriptions SET content_text, title, company_name, crawled_at
            Backend->>LLM: 텍스트 파싱 요청 (requirements, preferred, role_summary 추출)
            LLM-->>Backend: parsed_data 반환
            Backend->>DB: UPDATE job_descriptions SET parsed_data = ?, is_parsed = TRUE
            Backend->>VectorDB: 청킹 후 임베딩 저장 (user_document_chunks)
            Frontend-->>User: UI 갱신 (구조화 뷰)
        end
    end
```

---

## 비고

- `job_descriptions`는 URL 기준 공유 원문. 크롤링은 최초 1회만 수행
- `user_job_descriptions`는 사용자별 북마크 레이어. `is_active`로 면접 질문 생성 포함 여부 제어
- 삭제 시 `user_job_descriptions` 행만 제거. 공유 원문(`job_descriptions`)은 유지
