# pmg — PR Message Generator

LLM을 활용하여 GitHub Pull Request 설명을 자동 생성하는 Go CLI 도구입니다.

두 브랜치 간의 diff를 분석하고, PR 템플릿을 감지하여 제목과 본문을 생성합니다.

## 주요 기능

- 브랜치 간 diff 분석 및 단계적 축소 전략 (대용량 diff 지원)
- PR 템플릿 자동 감지 및 적용 (`.github/PULL_REQUEST_TEMPLATE.md`)
- 인터랙티브 브랜치 선택기 (자동완성)
- 7개 LLM 프로바이더 지원 (OpenAI, Claude CLI, Gemini CLI, Gemini API, Kiro CLI, Ollama Local/Remote)
- 클립보드 복사
- 프로젝트별 PR 규칙 관리
- 생성된 PR 설명을 `.pr-generator/pr-descriptions/` 에 마크다운으로 저장

## 설치

```bash
git clone https://github.com/kokoa-tools/pr-content-generator.git
cd pr-content-generator
make build
make install  # /usr/local/bin/pmg 에 설치
```

또는 직접 빌드:

```bash
go build -o pmg .
```

## 빠른 시작

```bash
# 1. 프로젝트 초기화
pmg init

# 2. PR 설명 생성
pmg

# 3. 브랜치 직접 지정
pmg --base main --branch feature/my-feature

# 4. 결과를 클립보드에 복사
pmg --copy

# 5. 출력만 하고 종료
pmg --dry-run
```

## 명령어

| 명령어 | 설명 |
|--------|------|
| `pmg` 또는 `pmg generate` | PR 설명 생성 |
| `pmg init` | 프로젝트 설정 초기화 |
| `pmg config` | 현재 설정 확인 |
| `pmg config set <key> <value>` | 설정값 변경 |
| `pmg rules` | PR 규칙 확인 |
| `pmg rules init` | PR 규칙 파일 생성 |
| `pmg rules edit` | PR 규칙 편집 |

## 플래그

| 플래그 | 설명 |
|--------|------|
| `--base` | Base 브랜치 (병합 대상) |
| `--branch` | PR 브랜치 (소스) |
| `--force`, `-f` | 크기 경고 무시 |
| `--dry-run`, `-d` | 출력만 하고 종료 |
| `--copy` | 결과를 클립보드에 복사 |

## LLM 프로바이더

| 프로바이더 | 설명 |
|-----------|------|
| `openai` | OpenAI API (GPT-4o 등) |
| `claude-cli` | Claude CLI 도구 |
| `gemini-cli` | Gemini CLI 도구 |
| `gemini` | Google Gemini API |
| `kiro-cli` | Kiro CLI 도구 |
| `ollama-local` | 로컬 Ollama 서버 |
| `ollama-remote` | 원격 Ollama 서버 |

## 프로젝트 구조

```
pr-content-generator/
├── main.go
├── cmd/                    # CLI 명령어
│   ├── root.go
│   ├── generate.go
│   ├── init.go
│   ├── config.go
│   └── rules.go
├── internal/
│   ├── config/             # 설정 관리
│   ├── git/                # Git 연동 (diff, branch)
│   ├── llm/                # LLM 프로바이더
│   ├── ui/                 # TUI 브랜치 선택기
│   ├── clipboard/          # 클립보드 연동
│   └── template/           # PR 템플릿 감지
├── Makefile
├── go.mod
└── go.sum
```

## 설정 파일

`pmg init` 실행 시 `.pr-generator/` 디렉토리에 생성됩니다:

- `config.json` — LLM 프로바이더, diff 크기 제한, 제외 패턴 등
- `pr-rules.md` — 프로젝트별 PR 작성 규칙
- `pr-descriptions/` — 생성된 PR 설명 마크다운 파일

> `.pr-generator/config.json`에 API 키가 포함될 수 있으므로 `.gitignore`에 추가하는 것을 권장합니다.

## Author

[@shinkeonkim](https://github.com/shinkeonkim)

## License

MIT
