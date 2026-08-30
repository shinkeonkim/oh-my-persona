# KMU FastChat API Example

KMU FastChat API(Mindlogic Gateway)를 LangChain으로 연동하는 간단한 CLI 챗봇 예제입니다.

## 개요

[Mindlogic Gateway](https://docs.mindlogic.ai/docs/kmu-ac/gateway/getting-started/overview)는 OpenAI, Google Gemini, Meta 등 다양한 LLM을 단일 OpenAI 호환 엔드포인트로 제공합니다. 이 프로젝트는 `KMU_FASTCHAT_API_KEY` 환경변수를 통해 해당 API에 접근하는 멀티턴 챗봇을 구현합니다.

## 요구사항

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) 패키지 매니저

## 설치

```bash
git clone https://github.com/kmu-aws-capstone-team-4/kmu-fastchat-api-example
cd kmu-fastchat-api-example
uv sync
```

## 환경변수 설정

프로젝트 루트에 `.env` 파일을 생성합니다.

```env
KMU_FASTCHAT_API_KEY=your_api_key_here
KMU_MODEL=gpt-5.3-chat-latest
```

`KMU_MODEL`을 생략하면 기본값 `gpt-5.3-chat-latest`가 사용됩니다.

## 사용 가능한 모델 확인

```bash
uv run check_models.py
```

## 실행

```bash
uv run main.py
```

```
챗봇이 시작되었습니다. 종료하려면 'exit' 또는 'quit'을 입력하세요.

You: 안녕하세요
AI: 안녕하세요! 무엇을 도와드릴까요?

You: exit
```

## 지원 모델 (2026년 4월 기준)

| 제공사 | 모델 ID |
|--------|---------|
| OpenAI | `gpt-5.3-chat-latest`, `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.4-nano` |
| Google | `gemini-3.1-pro-preview`, `gemini-3.1-flash-lite-preview`, `gemini-3-flash-preview` |
| Google | `google/gemma-3-27b-it` |
| Meta | `meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` |
| Upstage | `solar-pro3`, `solar-pro2` |
| LG AI | `LGAI-EXAONE/K-EXAONE-236B-A23B` |

> 실제 사용 가능한 모델은 구독 플랜에 따라 다릅니다. `check_models.py`로 확인하세요.

## 프로젝트 구조

```
.
├── main.py           # 챗봇 메인 코드
├── check_models.py   # 사용 가능한 모델 목록 조회
├── pyproject.toml    # uv 프로젝트 설정
├── .env              # 환경변수 (git 미포함)
└── .gitignore
```

## 작성자

- [@shinkeonkim](https://github.com/shinkeonkim)
