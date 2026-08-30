# Voice API Frontend Example

React + TypeScript + Vite 기반의 Voice API 데모 애플리케이션입니다.

## 기능

- ✅ 사용자 로그인 (JWT 토큰 기반)
- ✅ 자동 토큰 갱신
- ✅ Text-to-Speech API 호출
- ✅ 오디오 재생
- ✅ 한국어/영어 지원

## 기술 스택

- React 19
- TypeScript
- Vite
- SWC (빠른 컴파일)
- Bun (패키지 매니저)
- Axios (HTTP 클라이언트)

## 시작하기

### 1. 환경 변수 설정

```bash
cp .env.example .env.local
```

`.env.local` 파일을 편집하여 API URL을 설정하세요:

```env
VITE_API_URL=http://localhost:8000
VITE_VOICE_API_URL=http://localhost:8001
```

### 2. 의존성 설치

```bash
bun install
```

### 3. 개발 서버 실행

```bash
bun dev
```

브라우저에서 http://localhost:5173 을 열어주세요.

## 사용 방법

### 1. 회원가입 또는 로그인

- 새 계정 생성 또는 기존 계정으로 로그인
- 로그인 성공 시 JWT 토큰이 localStorage에 저장됨
- 이메일 인증 상태 및 프로필 완성 여부 표시

### 2. TTS 생성

- 텍스트 입력
- 언어 선택 (한국어/영어)
- "Generate Speech" 버튼 클릭
- 생성된 오디오 재생

### 3. 토큰 관리

- 토큰이 만료되면 자동으로 refresh token을 사용하여 갱신
- 갱신 실패 시 자동 로그아웃

## API 엔드포인트

### Backend API (Django)

**인증:**
- `POST /api/v1/users/sign-up/` - 회원가입
  - Body: `{ "name": "...", "email": "...", "password1": "...", "password2": "..." }`
  - Response: `{ "access": "...", "refresh": "...", "is_email_confirmed": false, "is_profile_completed": false }`

- `POST /api/v1/users/sign-in/` - 로그인
  - Body: `{ "email": "...", "password": "..." }`
  - Response: `{ "access": "...", "refresh": "...", "is_email_confirmed": true, "is_profile_completed": true }`

- `POST /api/v1/users/sign-out/` - 로그아웃
  - Body: `{ "refresh": "..." }`
  - Headers: `Authorization: Bearer <access_token>`

- `POST /api/v1/users/tokens/refresh/` - 토큰 갱신
  - Body: `{ "refresh": "..." }`
  - Response: `{ "access": "..." }`

- `POST /api/v1/users/tokens/verify/` - 토큰 검증
  - Body: `{ "token": "..." }`

- `GET /api/v1/users/me/` - 현재 사용자 정보
  - Headers: `Authorization: Bearer <access_token>`
  - Response: `{ "name": "...", "email": "...", "is_email_confirmed": true, "is_profile_completed": true }`

### Voice API (FastAPI)

- `POST /api/v1/tts` - Text-to-Speech 변환
  - Headers: `Authorization: Bearer <token>`
  - Body: `{ "text": "...", "language": "ko" | "en" }`
  - Response: `{ "text": "...", "audio_base64": "..." }`

## 프로젝트 구조

```
src/
├── components/
│   ├── AuthForm.tsx           # 로그인/회원가입 폼
│   └── TTSDemo.tsx            # TTS 데모 컴포넌트
├── hooks/
│   └── useAuth.ts             # 인증 관리 훅
├── services/
│   └── api.ts                 # API 클라이언트
├── App.tsx                    # 메인 앱
└── main.tsx                   # 엔트리 포인트
```

## 빌드

```bash
bun run build
```

빌드된 파일은 `dist/` 디렉토리에 생성됩니다.

## 프리뷰

```bash
bun run preview
```

## 개발 팁

### CORS 이슈

로컬 개발 시 CORS 이슈가 발생할 수 있습니다. Backend와 Voice API에서 CORS 설정을 확인하세요.

### 네트워크 설정

Docker Compose를 사용하는 경우, `mefit-local` 네트워크를 통해 서비스 간 통신이 가능합니다.

```bash
# 네트워크 생성 (한 번만 실행)
docker network create mefit-local

# Backend 실행
cd ../backend
docker-compose up

# Voice API 실행
cd ../voice-api
docker-compose up
```

## 문제 해결

### 로그인 실패

- Backend API가 실행 중인지 확인
- 사용자 계정이 생성되어 있는지 확인
- CORS 설정 확인

### TTS 생성 실패

- Voice API가 실행 중인지 확인
- 토큰이 유효한지 확인
- 네트워크 연결 확인

### 토큰 갱신 실패

- Refresh token이 만료되었을 수 있음
- 다시 로그인 필요
