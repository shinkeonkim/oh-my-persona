# 사주 프로필 태그 생성기

LLM을 활용하여 사주 월주(月柱)와 일주(日柱) 조합에 대한 프로필 태그를 자동으로 생성하는 프로젝트입니다.

## 요약

60개의 갑자(甲子) 조합을 기반으로 월주와 일주의 60 x 60 = 3,600개 조합에 대해 남자일 때와 여자일 때의 프로필 태그를 각각 자동으로 생성합니다. 생성된 태그는 SQLite 데이터베이스에 저장되며, 중복 처리를 지원합니다.

### 주요 특징

- **다양한 LLM Provider 지원**: Ollama, OpenAI, Google Gemini
- **성별 구분 태그 생성**: 같은 사주 조합에 대해 남자와 여자의 태그를 각각 생성
- **자동 태그 생성**: 각 성별당 최소 20개 이상의 프로필 태그 자동 생성
- **병렬 처리**: ThreadPoolExecutor를 활용한 효율적인 병렬 처리
- **데이터 검증**: Pydantic을 통한 엄격한 데이터 검증
- **중복 방지**: 이미 생성된 조합은 자동으로 건너뛰기
- **재시도 메커니즘**: LLM 호출 실패 시 자동 재시도 (최대 3회)

### 기술 스택

- Python 3.12+
- LangChain (LLM 통합)
- Pydantic (데이터 검증)
- SQLite3 (데이터베이스)
- uv (패키지 관리)

## 사용방법

### 1. 저장소 클론

```bash
git clone <repository-url>
cd saju_profile_tags_extractor
```

### 2. 패키지 설치

uv를 사용하여 의존성을 설치합니다:

```bash
# uv 설치 (미설치 시)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 의존성 설치
uv sync
```

### 3. 환경 변수 설정

`.env.example`을 복사하여 `.env` 파일을 생성하고 설정을 수정합니다:

```bash
cp .env.example .env
```

`.env` 파일 예시:

```env
# 병렬 처리 워커 수
MAX_WORKERS=40

# LLM Provider 선택 (ollama, gemini, openai)
LLM_PROVIDER=ollama

# Ollama 설정
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=exaone3.5:7.8b

# OpenAI 설정
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4

# Gemini 설정
GOOGLE_API_KEY=your-google-api-key-here
GEMINI_MODEL=gemini-1.5-pro

# 데이터베이스 경로
DATABASE_PATH=./saju_profile_tags.db
```

### 4. 실행

#### Ollama 사용 (권장)

```bash
# 1. Ollama 서버 실행 (별도 터미널)
ollama serve

# 2. 모델 다운로드 (필요시)
ollama pull exaone3.5:7.8b

# 3. 프로그램 실행
uv run python main.py
```

#### OpenAI 사용

```bash
# .env에서 LLM_PROVIDER=openai 설정 후
uv run python main.py
```

#### Gemini 사용

```bash
# .env에서 LLM_PROVIDER=gemini 설정 후
uv run python main.py
```

### 실행 흐름

1. 데이터베이스에서 이미 처리된 조합 확인
2. 미처리 조합만 필터링
3. 병렬로 LLM 호출하여 태그 생성 (기본 40개 스레드)
4. 각 조합마다 남자 태그와 여자 태그를 별도로 생성
5. 생성된 태그를 데이터베이스에 저장
6. 진행 상황 및 통계 출력

## 프로젝트 구조

```
saju_profile_tags_extractor/
├── main.py                      # 메인 실행 파일
├── src/
│   ├── __init__.py
│   ├── config.py                # 환경 변수 설정
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── provider.py          # LLM Provider 추상화
│   │   └── prompts.py           # 프롬프트 템플릿
│   ├── models/
│   │   ├── __init__.py
│   │   └── saju_profile_tags_response.py  # Pydantic 모델 정의
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db.py                # SQLite CRUD 로직
│   │   └── schema.sql           # 데이터베이스 스키마
│   └── constants/
│       ├── __init__.py
│       └── gapza.py             # 60갑자 데이터
├── .env                         # 환경 변수 (생성 필요)
├── .env.example                 # 환경 변수 예시
├── .gitignore                   # Git 무시 파일
├── pyproject.toml               # 프로젝트 설정
└── README.md                    # 프로젝트 문서
```

### 주요 모듈 설명

#### `main.py`
- `SajuProfileTagsGenerator`: 메인 클래스
  - `generate_tags()`: 단일 조합에 대한 태그 생성 (남자/여자 구분)
  - `process_combination()`: 조합 처리 및 데이터베이스 저장
  - `process_all()`: 모든 조합 병렬 처리

#### `src/config.py`
- 환경 변수 로딩 및 설정 관리
- LLM Provider, API 키, 데이터베이스 경로 등

#### `src/llm/provider.py`
- LLM Provider 추상화
- Ollama, OpenAI, Gemini 지원
- 통합된 인터페이스 제공

#### `src/llm/prompts.py`
- LangChain 프롬프트 템플릿
- 월주/일주 조합 기반 성별별 태그 생성 프롬프트

#### `src/models/saju_profile_tags_response.py`
- `SajuProfileTagsResponse`: LLM 응답 검증 모델
  - 각 성별당 최소 20개 이상의 태그 필수
  - 중복 제거 및 공백 처리

#### `src/database/db.py`
- SQLite 데이터베이스 관리
- CRUD 작업 및 중복 확인
- 미처리 조합 조회

#### `src/constants/gapza.py`
- 60갑자 정의 (천간+지지 조합)

### 데이터베이스 스키마

```sql
CREATE TABLE IF NOT EXISTS saju_profile_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month_stem TEXT NOT NULL,        -- 월주 천간
    month_branch TEXT NOT NULL,      -- 월주 지지
    day_stem TEXT NOT NULL,          -- 일주 천간
    day_branch TEXT NOT NULL,        -- 일주 지지
    male_tags TEXT NOT NULL,         -- 남자 태그 (JSON 배열)
    female_tags TEXT NOT NULL,       -- 여자 태그 (JSON 배열)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(month_stem, month_branch, day_stem, day_branch)
);
```

## 생성되는 태그 예시

각 월주/일주 조합에 대해 남자와 여자 각각 다음과 같은 카테고리의 태그가 생성됩니다:

- **성격**: "리더십 강함", "부드러운 성격", "결단력 있음"
- **대인관계**: "사교적", "배려심 많음", "친화력 좋음"
- **직업적 성향**: "추진력 있음", "창의적", "분석적"
- **연애 스타일**: "로맨틱", "솔직한 표현", "헌신적"
- **소통 방식**: "직설적", "공감 잘함", "경청 능력"
- **강점**: "책임감 강함", "끈기 있음", "적응력 좋음"

같은 사주 조합이라도 남자와 여자의 태그가 다르게 생성됩니다.

## 설정 및 최적화

### 병렬 처리 조정

`.env` 파일에서 워커 수 조정:

```env
MAX_WORKERS=40  # 동시 처리 스레드 수
```

### 요청 딜레이 조정

`main.py:246`에서 요청 간 딜레이 조정:

```python
success, total = generator.process_all(
    month_sajus=month_sajus,
    day_sajus=day_sajus,
    force=False,
    delay=0.5  # 초 단위
)
```

### 재시도 횟수 조정

```python
generator = SajuProfileTagsGenerator(
    max_retries=3  # 최대 재시도 횟수
)
```

### 강제 재생성

이미 존재하는 데이터를 다시 생성하려면:

```python
success, total = generator.process_all(force=True)
```

## 문제 해결

### Ollama 연결 실패

```bash
# Ollama 서버 상태 확인
ollama list

# Ollama 서버 실행
ollama serve

# 모델 다운로드 확인
ollama pull exaone3.5:7.8b
```

### API 키 오류

- `.env` 파일의 API 키가 올바른지 확인
- OpenAI: `OPENAI_API_KEY`
- Gemini: `GOOGLE_API_KEY`

### 데이터베이스 초기화

데이터베이스를 초기화하려면:

```python
from src.database.db import SajuProfileTagsDatabase

db = SajuProfileTagsDatabase()
db.clear_all_saju_profile_tags()
```

또는 파일 삭제:

```bash
rm saju_profile_tags.db
```
