# AWS Certified Solutions Architect - Associate (SAA-C03) 문제 은행

## 빠른 시작 (30초)

```bash
# 0) 최초 1회: 파이썬 의존성 설치 (uv 필요 — https://docs.astral.sh/uv/)
uv sync

# 1) 최초 1회 + 문항/노트 변경 시마다: 마크다운 → JSON 빌드
uv run python system/build_bank.py    # 문제 은행 (1,217문항) 빌드
uv run python system/build_notes.py   # 학습 노트 (24 study + 8 notes + 51 resource 섹션) 빌드
# 둘 다 외부 의존성 없이 python3만으로도 실행 가능

# 2) 웹 뷰 실행 (택 1)
open system/index.html                # macOS 기본 브라우저에서 열기 (localStorage에만 저장)
# 또는 로컬 서버로 실행 (진도가 SQLite에도 자동 저장됨, 아래 "진도 영속 저장" 참고)
uv run python system/serve.py         # http://127.0.0.1:8765 에서 접속 (이 기기 전용)
```

브라우저에서 `index.html`을 더블 클릭해도 그대로 열립니다. 서버 없이도 (uv/의존성/네트워크 모두 없이) 동작합니다. 실전 문제 풀이는 홈 화면에서, **정리된 학습 노트**는 [`#/study/01-ec2`](system/index.html#/study/01-ec2) 등의 해시 URL로 진입합니다 (아래 "학습 페이지" 참고).

## 진도 영속 저장 (localStorage + SQLite)

기본적으로 진도/오답/설정은 브라우저 `localStorage`에 저장됩니다. `index.html`을 더블 클릭해서 여는 한 가장 간단한 방법이지만, 브라우저 캐시를 지우거나 다른 브라우저로 열면 진도가 분리됩니다.

`uv run python system/serve.py`로 실행하면 FastAPI 로컬 서버가 `system/`을 서빙하면서 `/api/state` 엔드포인트를 통해 진도/오답/설정/테마를 **`system/data/state.db` (SQLite 3)** 에도 자동으로 저장합니다.

```bash
uv run python system/serve.py                        # 기본: 127.0.0.1:8765 (이 기기만)
uv run python system/serve.py --port 9000            # 포트 지정
uv run python system/serve.py 9000                   # (하위호환) 위치인자 포트
uv run python system/serve.py --lan                  # 0.0.0.0 바인딩 — 같은 LAN의 폰/노트북에서 접근
uv run python system/serve.py --host 192.168.0.10 --port 8080   # 명시적 바인딩
uv run python system/serve.py --help                 # 옵션 전체
```

- 헤더 서브타이틀에 `🖥 서버 저장 (JSON 파일)` 또는 `💾 브라우저 저장 (localStorage)` 표시로 현재 저장 모드를 확인할 수 있습니다. (서버 모드일 때 실제 저장소는 SQLite)
- 서버가 최초 실행되어 DB가 비어 있으면, 그 브라우저의 기존 localStorage 진도를 그대로 DB로 이관합니다 (덮어쓰지 않음).
- 서버 모드에서도 localStorage에 동일 데이터를 백업으로 계속 저장하므로, 서버를 끄고 열어도(파일 로딩) 최근 진도는 그대로 남아 있습니다.
- `system/data/state.db`는 표준 SQLite 파일이라 `sqlite3 system/data/state.db` 로 직접 열어 조회/편집할 수 있습니다. 스키마: `progress(qid, attempts, correct, last, last_result)`, `wrong_log(id, qid, ts, submitted, correct, position)`, `kv(key, value)`. 이 파일과 마이그레이션 백업은 `.gitignore` 처리되어 있어 커밋되지 않습니다.
- **`state.json` 자동 마이그레이션**: 기존에 `system/data/state.json`이 있는 상태에서 서버를 처음 띄우면, JSON 내용을 그대로 SQLite로 옮긴 뒤 원본은 `state.json.migrated`로 이름을 바꿔 백업합니다. 두 번 이상 마이그레이션되지 않으니 안심하고 지워도 됩니다.
- **바인딩 범위**: 기본은 `127.0.0.1` (이 기기 전용). `--lan` 을 붙이면 `0.0.0.0`에 바인딩되어 같은 로컬 네트워크의 다른 장치(폰·태블릿·다른 노트북)에서 접근할 수 있습니다. 배너에 실제 접속 URL과 감지된 LAN IP가 표시됩니다. 카페/공용 Wi-Fi 등 신뢰할 수 없는 네트워크에서는 `--lan` 을 사용하지 마세요 (인증 없음).

## 학습 페이지 (SPA)

`build_notes.py`가 `study-notes/*.md` + `notes/*.md`를 파싱해 `system/notes.js`로 사전 번들하고, 브라우저에서는 [marked.js](https://marked.js.org)로 렌더합니다. 서버 없이 `file://`에서도 동작 (모든 데이터가 JS 번들에 포함).

**진입 방법**: 문제 은행 홈 화면 상단 우측의 **📚 학습 노트** 버튼을 누르거나, 아래 해시 URL로 직접 접근.

**라우트**:

| URL | 내용 |
|---|---|
| `system/index.html` (또는 `#/home`) | 문제 은행 홈 (기존 퀴즈 앱) |
| `#/study/{slug}` | 카테고리 학습 노트 (예: `#/study/01-ec2`, `#/study/00-overview`, `#/study/99-cross-references`) |
| `#/notes/{slug}` | 개념 심층 노트 (예: `#/notes/api-gateway`) |
| `#/resources` | AWS SAA-C03 리소스 완전정리 (문서 서론) |
| `#/resources/{section-slug}` | 리소스 완전정리 H2 섹션 (예: `#/resources/section-01`) |
| `#/quiz/{qid}` | 단일 문제 즉시 풀기 (학습 노트의 예시 문제 링크에서 자동 진입) |
| `#/quiz/category/{num}` | 카테고리 필터 랜덤 세션 (예: `#/quiz/category/07`) |

**주요 상호작용**:

- **학습 → 실전 원클릭**: 각 학습 노트의 "패턴 분석" 섹션에는 실제 문제 은행 링크(`[예시 문제]`)가 있어 클릭 시 그 문제만 단일 문제 모드로 즉시 진입 → 답변 + 해설 확인 → 브라우저 뒤로가기로 학습 페이지 복귀.
- **카테고리 학습 → 카테고리 훈련**: 카테고리 학습 노트(01-22) 상단의 "이 카테고리 문제 풀기 (N문제)" 버튼은 그 카테고리만 필터 + 랜덤 세션을 즉시 시작.
- **개념 노트 PDF**: 원본 PDF(사용자의 학습 원본)는 각 개념 노트 상단 "PDF 다운로드" 링크로 즉시 다운로드 (서버 모드일 때 `/notes/files/*.pdf` 로 서빙, `file://` 모드에서도 상대 경로로 접근).
- **자동 TOC**: 데스크톱에서 우측에 현재 페이지의 H2/H3 자동 목차. 모바일에선 사이드바가 햄버거 드로어로 접힘.
- **테마**: 홈에서 켠 다크/라이트 테마가 학습 페이지에도 그대로 적용 (CSS 커스텀 프로퍼티 공유).

**콘텐츠 규칙** (원본 유지):

- 학습 노트 원본(`study-notes/*.md`, `notes/*.md`)은 절대 훼손하지 않습니다. build 단계에서 **내부 링크만** SPA 라우트로 변환하며, 원문·표·코드·인용문은 마크다운 그대로 렌더됩니다.
- 문제 은행 링크는 `bank.json`의 `source_file` 필드와 자동 매칭됩니다 (매칭 실패 시 원본 링크 유지).
- `AWS_SAA-C03_리소스_완전정리.md` (1,108줄)는 H2 헤딩 단위로 자동 분할되어 로딩이 가볍습니다.

## 기능

- **모드**: 전체 / 미풀이만 / 오답만 재풀이
- **순서**: 랜덤 / 순차
- **카테고리 필터**: 카테고리별 개별 선택 (전체 선택/해제 토글)
- **세션 문항 수**: 무제한 / 10 / 25 / 65(실전 모의고사) / 커스텀
- **진도 자동 저장**: 브라우저 localStorage (문항별 시도/정답/최근 결과 기록)
- **오답 자동 축적** + **오답 노트 마크다운 export**
- **키보드 단축키**: `A~E` / `1~5` 선택 · `Enter` 제출/다음 · `Esc` 나가기
- **다크/라이트 테마**: 자동 감지 + 수동 토글
- **모바일 반응형**
- **학습 페이지 SPA**: 위 "학습 페이지" 섹션 참고

이 시스템은 `aws-clf/system`과 동일한 구조를 그대로 재사용합니다 (문제 디렉토리 `NN-슬러그/` 규칙만 지키면 새 카테고리도 자동 인식).

## 파일 구조

```
aws-saa/
├── [01-22]-*/                # 카테고리별 문항 마크다운 (원본, 절대 수정/삭제 금지)
│   └── *.md                  # 파일당 1문항 (총 1,217문항)
├── study-notes/              # 카테고리별 학습 노트 (원본)
│   ├── 00-overview.md        # 시험 개요·6 필러·전략
│   ├── 01-ec2.md ~ 22-others.md  # 22개 카테고리 심층 노트
│   └── 99-cross-references.md    # 관통 개념 지도 · 신호어 사전
├── notes/                    # 심층 개념 노트 + 원본 PDF
│   ├── AWS_SAA_*.md          # 주제별 완전 정리 (API Gateway, IAM 등)
│   ├── AWS_SAA-C03_리소스_완전정리.md  # 1,108줄 관통 리소스
│   └── files/*.pdf           # 위 MD의 PDF 원본 (학습 페이지에서 다운로드 링크)
├── README.md                 # 이 문서
├── pyproject.toml            # uv 의존성 정의 (fastapi + uvicorn)
├── uv.lock                   # uv sync가 생성하는 잠금 파일
└── system/                   # 퀴즈 + 학습 페이지 (SPA)
    ├── build_bank.py         # NN-*/ 마크다운 → bank.js/bank.json 빌더
    ├── build_notes.py        # study-notes/*.md + notes/*.md → notes.js 빌더
    ├── serve.py              # (선택) FastAPI 로컬 서버 — 진도 SQLite 저장 + PDF 서빙
    ├── bank.js / bank.json   # 문제 은행 (자동 생성, ~3.7MB)
    ├── notes.js              # 학습 페이지 데이터 (자동 생성, ~1MB)
    ├── vendor/marked.min.js  # v14.1.4 vendored (외부 CDN 불가, file:// 지원)
    ├── index.html            # 웹 뷰 진입점
    ├── app.js                # 문제 은행 로직 (홈 · 세션 · 결과)
    ├── study.js              # 학습 페이지 SPA (라우터 · 사이드바 · TOC · 마크다운 렌더)
    ├── style.css             # 스타일 (다크/라이트 · 반응형 · 학습 페이지 3-column grid)
    └── data/
        ├── state.db          # (serve.py 실행 시 생성) 진도/오답/설정 SQLite 저장소
        └── state.json.migrated  # (있으면 최초 마이그레이션 시 자동 생성되는 백업)
```

## 문항 추가 워크플로

1. 새 카테고리는 `NN-슬러그/` (예: `23-new-topic/`) 형식의 디렉토리로, 문항은 그 안에 `.md` 파일로 추가합니다.
2. 기존 카테고리에 문항을 추가할 때도 해당 디렉토리에 `.md` 파일만 추가하면 됩니다.
3. 빌더를 재실행합니다:

```bash
uv run python system/build_bank.py    # 또는 python3 system/build_bank.py (외부 의존성 없음)
# ✅ Built N questions across M categories
```

**학습 노트를 수정한 경우** (`study-notes/*.md` 또는 `notes/*.md`):

```bash
uv run python system/build_notes.py
# ✅ Built notes.js: 24 study-notes, 8 notes, 51 resource sections
# → 링크 매칭 요약 · 깨진 링크 리스트 · PDF 매칭 통계
```

퀴즈/학습 앱은 새로고침 시 새 데이터를 로드합니다. 진도는 유지됩니다 (`localStorage` 또는 서버 모드 시 SQLite). **원본 문항/노트 마크다운 파일은 빌더가 읽기만 할 뿐 절대 수정/삭제하지 않습니다.**

### 지원하는 마크다운 형식

```markdown
## Question

<문제 텍스트>  (2개를 선택하세요.)   ← 복수 정답이면 개수 힌트 표기 권장

- [ ] A. <옵션 A>
- [ ] B. <옵션 B>
- [ ] C. <옵션 C>
- [ ] D. <옵션 D>
- [ ] E. <옵션 E>   ← A~E 임의 개수

## Answer

정답: A               ← 단일 정답
정답: B, C            ← 복수 정답 (쉼표 구분)

## Explanation

<정답 설명>

오답 분석

A: <오답 이유>
B: <오답 이유>
...
```

## 진도/오답 데이터

브라우저 localStorage (키 프리픽스 `aws-saa-quiz-v1:`)에 저장됩니다:

| 키 | 내용 |
|---|---|
| `progress` | `{ qid: { attempts, correct, last, lastResult } }` |
| `wrongLog` | 오답 목록 (제출·정답 이력) — 정답 처리 시 자동 제거 |
| `lastSettings` | 홈 화면 마지막 필터 (모드/카테고리/순서/limit) |
| `theme` | `dark` / `light` |

서버 모드(`serve.py`)일 땐 위 4가지가 `system/data/state.db` SQLite에도 동일하게 저장됩니다:

| 테이블 | 컬럼 | 대응 |
|---|---|---|
| `progress` | `qid, attempts, correct, last, last_result` | localStorage `progress` 정규화 |
| `wrong_log` | `id, qid, ts, submitted(JSON), correct(JSON), position` | `wrongLog` (순서 보존) |
| `kv` | `key, value(JSON)` | `settings`, `theme` |

**초기화**: 홈 화면 [진도 초기화] 버튼 (confirm 필요) 또는 브라우저 DevTools → Application → Local Storage에서 해당 origin 정리. 서버 모드에서 완전 초기화가 필요하면 `system/data/state.db` 파일을 지운 뒤 서버를 재기동하세요 (`state.json.migrated`가 남아 있으면 그 내용으로 다시 채워집니다).

**주의**: localStorage는 브라우저/origin별로 격리됩니다. `file://`로 열 때와 `http://localhost:PORT`로 열 때 진도가 분리됩니다. 한 방식으로 고정해 사용하세요. `aws-clf`와는 키 프리픽스가 달라 진도가 섞이지 않습니다.

## 브라우저 지원

- Chrome / Edge 111+
- Safari 16.2+
- Firefox 113+

(`:has()`, `color-mix()` CSS 사용)

## 라이선스/출처

문항 마크다운은 각 저작자의 학습 노트이며, 이 도구는 파싱과 UI만 제공합니다.
