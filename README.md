# oh-my-persona

[![CI](https://github.com/shinkeonkim/oh-my-persona/actions/workflows/ci.yaml/badge.svg)](https://github.com/shinkeonkim/oh-my-persona/actions/workflows/ci.yaml)
[![Image](https://github.com/shinkeonkim/oh-my-persona/actions/workflows/image.yaml/badge.svg)](https://github.com/shinkeonkim/oh-my-persona/actions/workflows/image.yaml)

김신건(별칭 `shinkeonkim`, `singun11`, `koa`, `kokoa`)에 관한 **출처와 시점이 추적되는** 페르소나 지식베이스 및 RAG 챗봇 프로젝트입니다.

기존 `persona-3000-lines.md`는 같은 근거를 여러 렌즈로 반복한 지원서 작성용 문서입니다. 이 프로젝트는 줄 수를 자료 수로 오인하지 않고 `source → document → claim/event → chunk → embedding` 계보를 보존합니다. 사실, 본인의 과거 발언, 해석, 지원서용 서술을 서로 다른 레코드로 관리합니다.

## 현재 포함된 것

- `data/registry/sources.jsonl`: 정규 URL, 관측일, 공개 범위, 수집 정책을 가진 출처 레지스트리
- `data/curated/claims.jsonl`: 날짜 정밀도와 근거를 가진 초기 원자 사실
- `docs/persona.md`: 기존 3,000줄 문서를 보강한 시계열 페르소나
- `docs/research-plan.md`: 5,000~10,000+ **검색 청크** 확보 계획과 품질 게이트
- `docs/architecture.md`: Strands Agents + LiteLLM + PostgreSQL/pgvector 기반 웹 챗봇 설계
- `src/oh_my_persona`: 수집 자료 정규화·청킹·검증 및 API 골격

## 빠른 시작

Python 3.11 이상과 `uv`를 권장합니다.

```bash
uv sync --extra dev
uv run persona validate
uv run persona inventory
uv run persona chunk
uv run persona audit
uv run persona evaluate
uv run pytest
```

`chunk`는 `data/raw/`와 `data/curated/`를 읽고 재생성 가능한 `data/processed/chunks.jsonl`을 만듭니다. 원문 PDF/ZIP은 Git에 바로 넣지 말고 `data/inbox/`에 두며, 수집 승인 후 raw 저장소로 승격합니다.

전체 작업 순서와 진행 상태는 [docs/tasks/README.md](docs/tasks/README.md)에 있습니다.

챗봇 실행은 환경변수를 설정한 뒤 다음과 같습니다.

```bash
PERSONA_MODEL_ID=litellm_proxy/persona-chat \
PERSONA_LITELLM_URL=https://llm.example.com \
PERSONA_LITELLM_KEY=... \
uv run uvicorn oh_my_persona.api:app --reload
```

모델 키는 브라우저에 전달하지 않습니다. 운영에서는 LiteLLM Proxy의 논리 모델 이름(`persona-chat`)을 사용해 Provider를 서버 쪽에서 교체합니다.

## 데이터 디렉터리

```text
data/
├── inbox/       # 사용자가 제공한 PDF/MD/ZIP 격리 구역 (기본 Git 제외)
├── raw/         # 원문 스냅샷 + sidecar metadata
├── registry/    # URL 중심 출처 목록
├── curated/     # 사람이 검토한 claim/event
└── processed/   # 재생성 가능한 청크/임베딩 입력
```

개인정보, 비공개 저장소, 제3자의 연락처와 대화는 명시적 동의 없이 수집하지 않습니다. robots.txt, 서비스 약관, 요청 속도와 저작권을 준수하며 원문 대신 검색에 필요한 최소 인용과 요약을 저장합니다.
