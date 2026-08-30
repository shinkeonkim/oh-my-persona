# 벡터 DB 스키마 (Vector Database Schema)

> 가상면접 웹 서비스의 벡터 데이터베이스 컬렉션 정의
>
> 벡터 DB는 의미 기반 유사도 검색(Semantic Search)을 통해 RAG 파이프라인에서 면접 질문 생성의 맥락 자료를 제공하는 역할을 한다.

---

## 설계 원칙

- 각 컬렉션은 **임베딩 벡터** + **원문 텍스트(chunk)** + **메타데이터** 구조를 기본으로 한다
- 임베딩 모델은 다국어 지원 모델 사용 권장 (예: `text-embedding-3-large`, `multilingual-e5-large`)
- 벡터 차원(dimension)은 사용 모델에 따라 결정 (예: 1536, 1024)
- 메타데이터 필드는 검색 필터링 및 결과 후처리에 활용된다
- 각 문서는 청킹(chunking) 후 청크 단위로 저장된다

---

## 컬렉션 목록

| 컬렉션명 | 설명 | 주요 검색 목적 |
|---------|------|-------------|
| `user_document_chunks` | 사용자 업로드 문서 청크 | 사용자 이력서·채용공고 기반 질문 생성 |
| `system_knowledge_chunks` | 시스템 기준 지식 베이스 청크 | 직군별 공통 면접 지식 제공 |
| `interview_qa_examples` | 면접 질문-답변 예시 | 질문 품질 향상 및 모범 답변 참조 |

---

## 컬렉션 상세 정의

---

### user_document_chunks

사용자가 업로드한 이력서, 채용공고, 자기소개서 등을 청킹하여 저장한다.
면접 질문 생성 시 해당 사용자의 문서만 필터링하여 검색한다.

#### 스키마

```json
{
  "id": "string (UUID)",
  "vector": "[float32 x dimension]",
  "payload": {
    "user_id": "string (UUID)",
    "document_id": "string (UUID, 관계형 DB user_documents.id 참조)",
    "document_type": "string ('resume' | 'job_posting' | 'cover_letter')",
    "chunk_index": "integer (문서 내 청크 순서)",
    "chunk_text": "string (청크 원문 텍스트)",
    "title": "string (문서 제목 또는 기업명)",
    "job_category": "string (업로드 시점의 사용자 희망 직군)",
    "is_active": "boolean (비활성화된 문서 청크 제외용)",
    "created_at": "string (ISO 8601)"
  }
}
```

#### 필드 설명

| 필드 | 설명 |
|------|------|
| `user_id` | 검색 시 특정 사용자 문서만 필터링하는 핵심 메타데이터 |
| `document_type` | 이력서/채용공고/자기소개서 구분. 질문 유형별 자료 선택에 활용 |
| `chunk_index` | 청크 순서. 검색 결과 재조합 시 원문 순서 복원에 사용 |
| `chunk_text` | LLM 프롬프트에 직접 삽입되는 원문 텍스트 |
| `is_active` | `false`인 청크는 검색 결과에서 제외 |

#### 검색 시나리오

```
쿼리: "사용자의 프로젝트 경험과 관련된 자료"
필터: user_id = {현재 사용자 ID}, is_active = true
반환: 이력서 내 프로젝트 경험 청크, 채용공고 내 요구 역량 청크
```

---

### system_knowledge_chunks

시스템이 사전에 구축한 직군별 면접 지식 베이스. 사용자 업로드 자료를 보완하는 공통 맥락 자료로 활용된다.

포함 데이터 예시:
- 직군별 자주 출제되는 면접 주제 목록
- 직군별 핵심 역량 및 평가 기준
- 산업별 트렌드 및 기술 키워드
- 공통 면접 에티켓 및 평가 포인트

#### 스키마

```json
{
  "id": "string (UUID)",
  "vector": "[float32 x dimension]",
  "payload": {
    "knowledge_type": "string ('interview_topic' | 'competency' | 'industry_trend' | 'etiquette')",
    "job_category": "string (적용 직군. 'all'이면 전 직군 공통)",
    "occupation_tags": ["string (관련 직업 태그 목록)"],
    "chunk_text": "string (지식 원문 텍스트)",
    "source": "string (출처 또는 작성 기준)",
    "version": "string (지식 버전. 업데이트 관리용)",
    "created_at": "string (ISO 8601)",
    "updated_at": "string (ISO 8601)"
  }
}
```

#### 필드 설명

| 필드 | 설명 |
|------|------|
| `knowledge_type` | 지식 유형. 질문 생성 단계에서 필요한 자료 유형을 선택적으로 검색 |
| `job_category` | 직군 필터. 사용자의 희망 직군과 매칭하여 검색 |
| `occupation_tags` | 세부 직업 태그. 더 정밀한 필터링에 활용 |
| `version` | 지식 베이스 버전 관리. 오래된 정보 갱신 추적 |

#### 검색 시나리오

```
쿼리: "백엔드 개발자 면접에서 자주 나오는 기술 질문 주제"
필터: job_category IN ('IT/개발', 'all')
반환: 백엔드 개발 관련 면접 주제, 공통 기술 역량 평가 기준
```

---

### interview_qa_examples

실제 면접 질문과 모범 답변 예시 쌍. 질문 생성 품질 향상 및 피드백 리포트 생성 시 참조 자료로 활용된다.

#### 스키마

```json
{
  "id": "string (UUID)",
  "vector": "[float32 x dimension]",
  "payload": {
    "question_text": "string (면접 질문 원문)",
    "answer_example": "string (모범 답변 예시)",
    "question_category": "string ('technical' | 'behavioral' | 'situational' | 'motivation' | 'self_intro')",
    "job_category": "string (관련 직군)",
    "occupation_tags": ["string"],
    "difficulty": "string ('easy' | 'medium' | 'hard')",
    "keywords": ["string (질문 핵심 키워드)"],
    "created_at": "string (ISO 8601)"
  }
}
```

#### 필드 설명

| 필드 | 설명 |
|------|------|
| `question_category` | 질문 유형. `technical`(기술), `behavioral`(행동), `situational`(상황), `motivation`(지원동기), `self_intro`(자기소개) |
| `difficulty` | 질문 난이도. 사용자 수준에 맞는 질문 생성 시 필터링 활용 가능 |
| `keywords` | 질문 핵심 키워드. 주제 매칭 정확도 향상에 활용 |

#### 검색 시나리오

```
쿼리: "팀 협업 갈등 상황 대처 경험"
필터: job_category IN ('IT/개발', 'all'), question_category = 'behavioral'
반환: 유사한 행동 면접 질문 예시 및 모범 답변
```

---

## RAG 파이프라인 흐름

면접 질문 생성 시 벡터 DB가 활용되는 전체 흐름이다.

```
1. 면접 세션 시작
   └─ 사용자 프로필 (직군, 직업) + 업로드 문서 확인

2. 면접 주제 생성 (LLM)
   └─ 입력: 사용자 직군, 직업, 최근 경향 요약
   └─ 출력: 면접 주제 n개

3. 주제별 벡터 검색 (각 주제에 대해 수행)
   ├─ user_document_chunks 검색
   │   └─ 필터: user_id, is_active=true
   │   └─ 쿼리: 주제 텍스트
   │   └─ Top-K 청크 반환
   │
   ├─ system_knowledge_chunks 검색
   │   └─ 필터: job_category (사용자 직군)
   │   └─ 쿼리: 주제 텍스트
   │   └─ Top-K 청크 반환
   │
   └─ interview_qa_examples 검색
       └─ 필터: job_category, question_category
       └─ 쿼리: 주제 텍스트
       └─ Top-K 예시 반환

4. 질문 생성 (LLM)
   └─ 입력: 주제 + 검색된 청크들 (컨텍스트)
   └─ 출력: 면접 질문

5. 꼬리 질문 생성 (LLM) - 꼬리질문 방식인 경우
   └─ 입력: 이전 질문 + 사용자 답변 + 검색된 청크들
   └─ 출력: 꼬리 질문 1~3개
```

---

## 청킹 전략

| 문서 유형 | 청킹 방식 | 청크 크기 | 오버랩 |
|---------|---------|---------|------|
| 이력서 | 섹션 기반 (경력, 학력, 기술 등) | 300~500 토큰 | 50 토큰 |
| 채용공고 | 섹션 기반 (자격요건, 우대사항, 업무내용) | 200~400 토큰 | 30 토큰 |
| 자기소개서 | 문단 기반 | 200~400 토큰 | 50 토큰 |
| 시스템 지식 | 주제 단위 | 200~500 토큰 | 0 토큰 |
| QA 예시 | 질문-답변 쌍 단위 (분리 저장 안 함) | 전체 쌍 | - |

---

## 인덱스 설정 권장사항

```
user_document_chunks:
  - 벡터 인덱스: HNSW (ef_construction=200, m=16)
  - 페이로드 인덱스: user_id (keyword), is_active (bool), document_type (keyword)

system_knowledge_chunks:
  - 벡터 인덱스: HNSW (ef_construction=200, m=16)
  - 페이로드 인덱스: job_category (keyword), knowledge_type (keyword)

interview_qa_examples:
  - 벡터 인덱스: HNSW (ef_construction=200, m=16)
  - 페이로드 인덱스: job_category (keyword), question_category (keyword), difficulty (keyword)
```

> HNSW(Hierarchical Navigable Small World): 고차원 벡터의 근사 최근접 이웃 검색에 널리 사용되는 인덱스 알고리즘. Qdrant, Weaviate, Pinecone 등 주요 벡터 DB에서 지원한다.
