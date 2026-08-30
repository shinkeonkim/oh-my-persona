# 사주 궁합 태그 생성기

LLM을 활용하여 사주 일주(日柱) 조합에 대한 궁합 태그를 자동으로 생성하는 프로젝트입니다.

## 요약

60개의 사주 일주 조합을 기반으로 총 3,600개(60 x 60)의 궁합 조합에 대해 LLM이 자동으로 궁합 태그를 생성합니다. 생성된 태그는 SQLite 데이터베이스에 저장되며, 중복 처리를 지원합니다.

### 주요 특징

- **다양한 LLM Provider 지원**: Ollama, OpenAI, Google Gemini
- **자동 태그 생성**: 각 조합당 최소 20개 이상의 궁합 태그 자동 생성
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
cd saju_compatibility_tags_with_llm
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
# LLM Provider 선택 (ollama, gemini, openai)
LLM_PROVIDER=ollama

# Ollama 설정
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1

# OpenAI 설정
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4

# Gemini 설정
GOOGLE_API_KEY=your-google-api-key-here
GEMINI_MODEL=gemini-1.5-pro

# 데이터베이스 경로
DATABASE_PATH=./saju_compatibility.db
```

### 4. 실행

#### Ollama 사용 (권장)

```bash
# 1. Ollama 서버 실행 (별도 터미널)
ollama serve

# 2. 모델 다운로드 (필요시)
ollama pull llama3.1

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
3. 병렬로 LLM 호출하여 태그 생성 (기본 3개 스레드)
4. 생성된 태그를 데이터베이스에 저장
5. 진행 상황 및 통계 출력

## 프로젝트 구조

```
saju_compatibility_tags_extractor/
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
│   │   └── compatibility.py     # Pydantic 모델 정의
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db.py                # SQLite CRUD 로직
│   │   └── schema.sql           # 데이터베이스 스키마
│   └── constants/
│       ├── __init__.py
│       └── ilju.py              # 60개 일주 데이터 및 특성
├── .env                         # 환경 변수 (생성 필요)
├── .env.example                 # 환경 변수 예시
├── pyproject.toml               # 프로젝트 설정
└── README.md                    # 프로젝트 문서
```

### 주요 모듈 설명

#### `main.py`
- `CompatibilityTagGenerator`: 메인 클래스
  - `generate_tags()`: 단일 조합에 대한 태그 생성
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
- 일주 조합 및 특성 기반 태그 생성 프롬프트

#### `src/models/compatibility.py`
- `CompatibilityTagsResponse`: LLM 응답 검증 모델
  - 최소 20개 이상의 태그 필수
  - 중복 제거 및 공백 처리
- `IljuCompatibility`: 데이터베이스 저장 모델

#### `src/database/db.py`
- SQLite 데이터베이스 관리
- CRUD 작업 및 중복 확인
- 미처리 조합 조회

#### `src/constants/ilju.py`
- 60개 천간지지 일주 정의
- 각 일주별 특성 데이터 (성격, 성향, 강점, 약점 등)

### 데이터베이스 스키마

```sql
CREATE TABLE compatibility_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    male_ilju TEXT NOT NULL,
    female_ilju TEXT NOT NULL,
    tags TEXT NOT NULL,          -- JSON 배열 형식
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(male_ilju, female_ilju)
);
```

## 생성되는 태그 예시

각 일주 조합에 대해 다음과 같은 카테고리의 태그가 생성됩니다:

- **감정/소통**: "감정 텔레파시", "대화가 술술", "서로의 마음 이해"
- **성격 조화**: "성격 보완", "찰떡궁합", "케미 폭발"
- **관계 역학**: "주도권 균형", "밀당 고수", "서로 존중"
- **장단점**: "장점 극대화", "단점 보완", "시너지 효과"
- **미래 전망**: "장기적 안정", "성장 가능성", "평생 파트너"
- **갈등**: "갈등 적음", "이해 충돌 주의", "소통 노력 필요"
- **특별 포인트**: "운명적 만남", "천생연분", "특별한 인연"

## 설정 및 최적화

### 병렬 처리 조정

`main.py:19`에서 워커 수 조정 가능:

```python
MAX_WORKERS = 3  # 동시 처리 스레드 수
```

### 요청 딜레이 조정

`main.py:263`에서 요청 간 딜레이 조정:

```python
success, total = generator.process_all(
    male_iljus=male_iljus,
    female_iljus=female_iljus,
    force=False,
    delay=0.5  # 초 단위
)
```

### 재시도 횟수 조정

```python
generator = CompatibilityTagGenerator(
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
ollama pull llama3.1
```

### API 키 오류

- `.env` 파일의 API 키가 올바른지 확인
- OpenAI: `OPENAI_API_KEY`
- Gemini: `GOOGLE_API_KEY`

### 데이터베이스 초기화

데이터베이스를 초기화하려면:

```python
from src.database.db import CompatibilityDatabase

db = CompatibilityDatabase()
db.clear_all()
```

또는 파일 삭제:

```bash
rm saju_compatibility.db
```
