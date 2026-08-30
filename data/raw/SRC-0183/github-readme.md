# API 통합 프론트엔드 예제

카카오 로그인, NICE 본인인증, 토스 결제를 모두 통합한 Next.js 프론트엔드 예제 프로젝트입니다.

## 기능

1. **카카오 로그인** - OAuth 2.0 인증
2. **NICE 본인인증** - 휴대폰 본인인증
3. **토스 페이먼츠 결제** - 결제 처리 및 티켓 구매

## 사용 기술

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Payment**: Toss Payments SDK
- **Authentication**: JWT (Access/Refresh Token)

## 설치 및 실행

### 1. 의존성 설치

```bash
npm install
```

### 2. 환경 변수 설정

`.env.local` 파일을 생성하고 다음 환경 변수를 설정합니다:

```env
# 백엔드 API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# 카카오 로그인
NEXT_PUBLIC_KAKAO_CLIENT_ID=your_kakao_client_id
NEXT_PUBLIC_KAKAO_REDIRECT_URI=http://localhost:3000/oauth/callback/kakao

# 토스 페이먼츠
NEXT_PUBLIC_TOSS_CLIENT_KEY=your_toss_client_key
```

### 3. 개발 서버 실행

```bash
npm run dev
```

서버가 http://localhost:3000 에서 실행됩니다.

## 프로젝트 구조

```
api_frontend_example/
├── app/
│   ├── checkout/           # 토스 결제 페이지
│   ├── nice/
│   │   └── callback/        # NICE 본인인증 콜백
│   ├── oauth/
│   │   └── callback/
│   │       └── kakao/       # 카카오 로그인 콜백
│   ├── payment/
│   │   ├── success/         # 결제 성공 페이지
│   │   └── fail/            # 결제 실패 페이지
│   ├── layout.tsx           # 루트 레이아웃
│   ├── page.tsx            # 메인 페이지
│   └── globals.css         # 글로벌 스타일
├── hooks/
│   ├── useAuth.ts          # 인증 훅
│   └── useNiceVerification.ts  # 본인인증 훅
├── lib/
│   ├── api.ts              # API 클라이언트 (유저 인증 포함)
│   ├── auth.ts             # 인증 유틸리티
│   ├── nice-api.ts         # NICE API 클라이언트
│   └── types.ts            # 타입 정의
├── next.config.js
├── package.json
└── tsconfig.json
```

## 주요 기능 설명

### 1. 카카오 로그인

- OAuth 2.0 인증 플로우
- Access Token 및 Refresh Token 관리
- 자동 토큰 갱신

### 2. NICE 본인인증

- 팝업 창을 통한 본인인증
- 백엔드 API와 통신하여 초기화 데이터 수신
- 본인인증 결과를 백엔드로 전달

### 3. 토스 결제

- 토스페이먼츠 SDK를 사용한 결제 처리
- 결제 준비 → 결제 요청 → 결제 승인 플로우
- 티켓 구매 완료 처리

## 사용 흐름

1. **로그인 안내**: 사용자가 페이지에 접속하면 카카오 로그인이 필요하다는 안내 표시
2. **카카오 로그인**: 카카오 로그인 버튼 클릭 → 카카오 인증 → 토큰 발급
3. **본인인증**: 로그인 후 본인인증 버튼 클릭 → 팝업에서 본인인증 진행
4. **티켓 선택**: 본인인증 완료 후 티켓 패키지 선택
5. **결제**: 선택한 티켓으로 결제 진행 (토스페이먼츠)
6. **완료**: 결제 승인 후 티켓 자동 지급

## 백엔드 API 엔드포인트

프로젝트는 다음과 같은 백엔드 API를 사용합니다:

### 인증
- `POST /api/v1/users/kakao/login/` - 카카오 로그인
- `POST /api/v1/users/token/refresh/` - 토큰 갱신

### NICE 본인인증
- `POST /api/v1/users/nice/init/` - 본인인증 초기화 (Auth 필요)
- `POST /api/v1/users/nice/verify/` - 본인인증 검증 (Auth 필요)

### 티켓 상품
- `GET /api/v1/ticket-products/` - 티켓 상품 목록

### 결제
- `POST /api/v1/payments/` - 결제 준비 (Auth 필요)
- `POST /api/v1/payments/confirm/` - 결제 승인 (Auth 필요)

## 주요 개선 사항

기존 예제 대비 다음과 같은 개선이 있습니다:

1. **유저 인증 추가**: NICE API 호출 시 Bearer 토큰 포함
2. **통합 플로우**: 로그인 → 본인인증 → 결제를 하나의 흐름으로 통합
3. **에러 처리**: 각 단계별 에러 처리 및 사용자 피드백
4. **UI/UX**: 단계별 상태 표시 및 안내 메시지

## 주의사항

1. 백엔드 서버가 실행 중이어야 합니다
2. 환경 변수를 올바르게 설정해야 합니다
3. 팝업 차단을 해제해야 본인인증이 가능합니다
4. 테스트 모드에서는 실제 결제가 진행되지 않습니다

## 개발 및 빌드

```bash
# 개발 모드
npm run dev

# 프로덕션 빌드
npm run build

# 프로덕션 실행
npm start

# 린트
npm run lint
```

## 라이선스

이 프로젝트는 예제 목적으로 작성되었습니다.

