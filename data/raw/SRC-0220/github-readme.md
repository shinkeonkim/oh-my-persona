# Claude Code 설정 모음집

> Claude Code CLI 도구를 위한 개인 설정 및 구성 파일 모음입니다.

> 이 프로젝트는 Claude Code를 더 효율적으로 사용하기 위한 개인 설정 모음집입니다.

## 📁 프로젝트 구조

```
.
├── .claude/
│   ├── settings.local.json    # Claude Code 로컬 설정
│   └── agents/               # 전문 에이전트 설정 파일들
│       ├── ai-engineer.md
│       ├── api-documenter.md
│       ├── command-expert.md
│       ├── context-manager.md
│       ├── ....
└── .mcp.json                 # MCP 서버 설정
```

## ⚙️ 주요 설정

### MCP 서버 구성
- **playwright-server**: 웹 브라우저 자동화
- **fetch**: HTTP 요청 처리
- **chrome-devtools**: Chrome 개발자 도구 연동
- **browsermcp**: 브라우저 제어
- **DeepGraph**: Vue, TypeScript, React 코드 분석
- **context7**: 컨텍스트 관리
- **memory**: 메모리 서버

### 권한 설정
다양한 개발 도구와 명령어에 대한 허용 권한이 설정되어 있습니다:
- 파일 시스템 조작 (mkdir, cd, cat, mv, rm, ls 등)
- 패키지 관리 (npm, pip, uv 등)
- 개발 서버 (npm run dev, build 등)
- Docker 명령어
- Python 및 Node.js 실행

### 전문 에이전트
18개의 전문화된 에이전트가 구성되어 있어 다양한 개발 작업을 지원합니다:
- **AI Engineer**: LLM 애플리케이션 및 RAG 시스템 전문
- **Database Architect**: 데이터베이스 설계 및 아키텍처
- **Frontend Developer**: React 애플리케이션 및 반응형 디자인
- **DevOps Troubleshooter**: 프로덕션 트러블슈팅 및 인시던트 대응
- **Performance Engineer**: 애플리케이션 프로파일링 및 최적화
- **Test Engineer**: 테스트 자동화 및 품질 보증
- 기타 다양한 전문 분야

## 🚀 사용법

### 설정 파일 복사

`command.sh` 스크립트를 사용하여 설정 파일들을 원하는 프로젝트에 쉽게 복사할 수 있습니다.

```bash
# 스크립트 실행
./command.sh
```

### Zsh Alias 설정

더 편리한 사용을 위해 zsh 설정에 alias를 추가하세요:

```bash
# ~/.zshrc 파일에 추가
alias claude-setup="$HOME/my-claude-code-settings/command.sh"
```

설정 적용:
```bash
source ~/.zshrc
```

이제 어디서든 `claude-setup` 명령어로 Claude Code 설정을 복사할 수 있습니다.

