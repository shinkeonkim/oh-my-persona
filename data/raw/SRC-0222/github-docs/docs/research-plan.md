# 자료 조사·확장 계획

## 목표의 단위

목표 5,000~10,000+는 서로 다른 사실 1만 개가 아니라 **중복 제거 후 검색 가능한 청크 수**다. 하나의 원문은 여러 청크가 될 수 있으나 같은 문장을 렌즈만 바꿔 복제하지 않는다. 원문 수, 원자 사실 수, 사건 수, 청크 수를 별도로 보고한다.

## 단계

### 0. 기반과 기준선 (현재)

- canonical URL과 별칭 기반 identity resolution
- `published_at`, `updated_at`, `observed_at`, `valid_at`, `date_precision` 분리
- SHA-256으로 동일 원문/청크 중복 제거
- self-published / organization-published / platform metadata / third-party의 신뢰 유형 분리

### 1. 소유 저장소와 사이트 (목표 1,500~3,000 청크)

- `my-resume`, `my-portfolio`의 데이터 파일과 Git 이력
- `shinkeonkim` 및 연결 조직의 공개 저장소 README, docs, release, issue, PR, commit metadata
- `shinkeonkim.com`, `singun11.tistory.com`, `singun11.wtf`의 sitemap/RSS/공개 글
- PDF 발표자료는 페이지·슬라이드 번호와 원본 URL을 보존

Git 이력은 작성일의 보조 근거일 뿐 사건 발생일로 자동 간주하지 않는다. fork, generated file, dependency lockfile, vendored code는 기본 제외한다.

### 2. 조직·활동 자료 (목표 누적 3,000~5,000 청크)

- 국민대, 멋쟁이사자처럼, SIPE, 대회 주최기관의 공개 게시물
- 발표 영상·슬라이드·강의 저장소와 프로젝트 조직 저장소
- 본인 기여는 작성자, 커밋, 발표자, 명시적 역할 중 하나로 검증

### 3. 사용자가 제공하는 문서 (목표 누적 5,000~10,000+ 청크)

ZIP/PDF/Markdown을 `data/inbox/`에 넣은 뒤 다음 순서로 처리한다.

1. 압축 경로 순회 공격, 실행 파일, 암호화 파일, 최대 용량을 검사한다.
2. 원본은 변경하지 않고 해시·MIME·파일명·수집일 sidecar를 만든다.
3. PDF는 페이지 단위 텍스트와 OCR 여부를 기록하고, Markdown은 제목 계층을 유지한다.
4. 주민번호, 전화번호, 주소, 토큰·키, 제3자 개인정보를 탐지해 격리한다.
5. 사람이 공개 범위와 저작권을 승인한 문서만 `raw/`로 승격한다.

## 조사 쿼리

- 강한 식별자: `site:github.com/shinkeonkim`, `site:shinkeonkim.com`, `site:singun11.tistory.com`
- 교차 식별자: `"김신건" "국민대학교" 개발`, `"김신건" 그렙 프로그래머스`, `"shinkeonkim" SIPE`
- 별칭: `"kokoa" shinkeonkim`, `"koa" "김신건" 개발`
- 산출물: 프로젝트명 + `shinkeonkim`, 발표명 + `김신건`

이름 단독 검색 결과는 수집 후보일 뿐 채택 근거가 아니다.

## 품질 게이트

- accepted source 100%에 HTTPS canonical URL(로컬 체크아웃도 GitHub URL로 인용)
- claim 100%에 최소 1개 source ID와 날짜 정밀도
- 고위험/수치 claim은 가능하면 독립 근거 2개
- exact chunk duplicate 0%, near duplicate 비율 5% 미만
- 임의 100개 샘플의 출처 역추적 성공률 100%
- 시간 질문, 근거 없는 질문, 동명이인 질문을 포함한 회귀 평가셋 운영

## 수집 예산과 예의

robots.txt와 약관을 먼저 확인하고 도메인별 낮은 동시성·지수 백오프·캐시를 사용한다. 검색 결과 전문을 무단 복제하지 않고 URL, 최소 인용, 사실 요약, 해시 중심으로 보존한다. 삭제 요청과 원출처 삭제를 반영할 tombstone 절차를 둔다.
