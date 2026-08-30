# SD-DOC-001 이력서 등록

> 대응 UC: [UC-DOC-001](../use-cases/UC-DOC-001-이력서_등록_및_관리.md)

---

## 자유 텍스트 입력

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant DB
    participant Storage
    participant LLM
    participant VectorDB

    User->>Frontend: 이력서 제목 + 자유 텍스트 입력 후 저장

    Frontend->>Backend: POST /api/v1/resumes<br/>{ resume_type: "text", title, content }
    Backend->>DB: INSERT INTO resumes (user_id, resume_type, title, is_parsed=false)
    Backend->>DB: INSERT INTO resume_text_contents (resume_id, content)
    Backend-->>Frontend: 201 Created { resume_id }
    Frontend-->>User: 목록에 추가 ("분석 중..." 상태 표시)

    Note over Backend,VectorDB: 비동기 후처리 (백그라운드 워커)

    Backend->>LLM: 텍스트 파싱 요청 (skills, experience, summary 추출)
    LLM-->>Backend: parsed_data 반환
    Backend->>DB: UPDATE resumes SET parsed_data = ?, is_parsed = TRUE
    Backend->>VectorDB: 텍스트 청킹 후 임베딩 저장 (user_document_chunks)
    Backend->>DB: INSERT INTO user_trend_summaries (경향 분석 갱신)

    Frontend-->>User: UI 갱신 ("분석 중..." → 구조화 뷰)
```

---

## 파일 업로드

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant DB
    participant Storage
    participant LLM
    participant VectorDB

    User->>Frontend: 이력서 제목 + PDF/DOCX 파일 선택 후 업로드

    Frontend->>Backend: POST /api/v1/resumes<br/>{ resume_type: "file", title, file }
    Backend->>Storage: 파일 업로드 (S3 등)
    Storage-->>Backend: storage_path 반환
    Backend->>DB: INSERT INTO resumes (user_id, resume_type, title, is_parsed=false)
    Backend->>DB: INSERT INTO resume_file_contents (resume_id, original_filename, storage_path, mime_type)
    Backend-->>Frontend: 201 Created { resume_id }
    Frontend-->>User: 목록에 추가 ("분석 중..." 상태 표시)

    Note over Backend,VectorDB: 비동기 후처리 (백그라운드 워커)

    Backend->>Storage: 파일 다운로드
    Backend->>Backend: 텍스트 파싱·추출 (PDF/DOCX → text)
    Backend->>DB: UPDATE resume_file_contents SET extracted_text = ?

    alt 파싱 실패
        Backend->>DB: UPDATE resumes SET is_parsed = FALSE (오류 상태 표기)
        Frontend-->>User: "파일을 읽지 못했습니다. 텍스트로 직접 입력해 주세요"
    else 파싱 성공
        Backend->>LLM: 텍스트 파싱 요청
        LLM-->>Backend: parsed_data 반환
        Backend->>DB: UPDATE resumes SET parsed_data = ?, is_parsed = TRUE
        Backend->>VectorDB: 청킹 후 임베딩 저장 (user_document_chunks)
        Backend->>DB: INSERT INTO user_trend_summaries (경향 분석 갱신)
        Frontend-->>User: UI 갱신 (구조화 뷰)
    end
```

---

## 비고

- 이력서는 필수 사항. 등록 없이는 면접 시작 불가능
- `is_parsed = false` 동안 UI는 "분석 중..." 폴백 뷰 표시
- 여러 이력서 등록 가능. 각각 `is_active`로 활성화/비활성화 관리
