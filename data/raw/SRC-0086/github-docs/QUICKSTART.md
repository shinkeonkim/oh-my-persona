# Quick Start Guide

## 5분 안에 시작하기

### 1. 환경 설정

```bash
# 환경 변수 파일 생성
cp .env.example .env.local

# 의존성 설치
bun install
```

### 2. 개발 서버 실행

```bash
bun dev
```

브라우저에서 http://localhost:5173 접속

### 3. Docker로 실행 (선택사항)

```bash
# mefit-local 네트워크 생성 (처음 한 번만)
docker network create mefit-local

# Backend 실행
cd ../backend
docker-compose up -d

# Voice API 실행
cd ../voice-api
docker-compose up -d

# Frontend 실행
cd ../voice-fe-example
docker-compose up
```

## 사용 방법

### 1단계: 로그인

Backend에 등록된 계정으로 로그인:
- Username: (your username)
- Password: (your password)

### 2단계: TTS 테스트

1. 텍스트 입력 (예: "안녕하세요")
2. 언어 선택 (한국어/영어)
3. "Generate Speech" 버튼 클릭
4. 생성된 오디오 재생

## 주요 기능

- ✅ JWT 토큰 기반 인증
- ✅ 자동 토큰 갱신
- ✅ Text-to-Speech 변환
- ✅ 실시간 오디오 재생

## API 엔드포인트

### Backend (Django)
- Login: `POST /api/v1/users/tokens/`
- Refresh: `POST /api/v1/users/tokens/refresh/`
- Verify: `POST /api/v1/users/tokens/verify/`

### Voice API (FastAPI)
- TTS: `POST /api/v1/tts`

## 문제 해결

### CORS 에러
Backend와 Voice API의 CORS 설정을 확인하세요.

### 로그인 실패
- Backend API가 실행 중인지 확인
- 올바른 계정 정보 사용

### TTS 생성 실패
- Voice API가 실행 중인지 확인
- 토큰이 유효한지 확인

## 다음 단계

- [README.md](./README.md) - 상세 문서
- [../voice-api/README.md](../voice-api/README.md) - Voice API 문서
- [../backend/README.md](../backend/README.md) - Backend 문서
