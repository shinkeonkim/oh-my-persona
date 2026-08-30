# www.google.com을 입력하면?

> 브라우저 주소창에 `www.google.com`을 입력하면 일어나는 6단계를 인터랙티브 시각화로 설명하는 웹사이트

[![Vite](https://img.shields.io/badge/Vite-5.x-646CFF?style=flat-square&logo=vite)](https://vitejs.dev)
[![React](https://img.shields.io/badge/React-18.x-61DAFB?style=flat-square&logo=react)](https://react.dev)
[![Bun](https://img.shields.io/badge/Bun-1.x-FBF0DF?style=flat-square&logo=bun)](https://bun.sh)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.x-06B6D4?style=flat-square&logo=tailwindcss)](https://tailwindcss.com)

## 미리보기

![Neo-brutalism 디자인 스타일의 6단계 인터랙티브 웹사이트](https://github.com/kokoa-lab/how-to-get-google-dot-com/blob/main/docs/preview.png)

## 다루는 내용

엔터 한 번으로 시작되는 6단계 네트워크 여정:

| # | 단계 | 핵심 개념 |
|---|------|-----------|
| 01 | **DNS 조회** | 도메인 → IP 주소 변환, 캐시 계층, Root/TLD/Authoritative NS |
| 02 | **TCP 연결 수립** | 3-Way Handshake (SYN → SYN-ACK → ACK) |
| 03 | **TLS 핸드셰이크** | 인증서 검증, ECDHE 키 교환, AES-256 암호화 |
| 04 | **HTTP 요청** | HTTP/2, 요청 메서드, 요청 헤더 해부도 |
| 05 | **서버 응답** | CDN, Load Balancer, HTTP 상태코드, Brotli 압축 |
| 06 | **브라우저 렌더링** | Critical Rendering Path (DOM → CSSOM → Layout → Paint → Composite) |

각 단계마다 **인터랙티브 시각화**를 포함합니다.

## 기술 스택

- **Runtime**: [Bun](https://bun.sh)
- **번들러**: [Vite](https://vitejs.dev)
- **UI 라이브러리**: [React 18](https://react.dev)
- **CSS**: [Tailwind CSS v3](https://tailwindcss.com)
- **아이콘**: [lucide-react](https://lucide.dev)
- **디자인 시스템**: Neo-brutalism

## 로컬 실행

```bash
# 저장소 클론
git clone https://github.com/kokoa-lab/how-to-get-google-dot-com.git
cd how-to-get-google-dot-com

# 의존성 설치
bun install

# 개발 서버 시작
bun run dev
```

브라우저에서 `http://localhost:5173` 열기

## 빌드

```bash
bun run build    # 프로덕션 빌드 → dist/
bun run preview  # 빌드 결과 미리보기
```

## Cloudflare 배포

Cloudflare Workers Static Assets를 사용해
`https://how-to-get-google-dot-com.shinkeonkim.com`에 배포합니다.

사전 조건:

- `shinkeonkim.com`이 배포할 Cloudflare 계정의 활성 Zone이어야 합니다.
- 배포 호스트명에 기존 CNAME 레코드가 없어야 합니다.
- 최초 한 번 `bunx wrangler login`으로 Cloudflare 계정을 인증합니다.

```bash
# Cloudflare 환경으로 로컬 미리보기
bun run cf:dev

# 프로덕션 빌드 후 커스텀 도메인으로 배포
bun run deploy
```

배포 대상과 정적 자산 경로는 `wrangler.jsonc`에서 관리합니다. CI에서는
대화형 로그인 대신 `CLOUDFLARE_API_TOKEN` 환경 변수를 사용할 수 있습니다.

## 프로젝트 구조

```
src/
├── components/
│   ├── visualizations/
│   │   ├── DNSVisual.jsx      # DNS 체인 애니메이션
│   │   ├── TCPVisual.jsx      # 3-Way Handshake 시퀀스 다이어그램
│   │   ├── TLSVisual.jsx      # TLS 핸드셰이크 + 자물쇠 시각화
│   │   ├── HTTPVisual.jsx     # HTTP 요청 해부도
│   │   ├── ServerVisual.jsx   # CDN/LB 아키텍처 + 상태코드
│   │   └── RenderVisual.jsx   # Critical Rendering Path 파이프라인
│   ├── Header.jsx
│   ├── Hero.jsx
│   ├── StepCard.jsx
│   └── Footer.jsx
├── data/
│   └── steps.jsx              # 6단계 콘텐츠 데이터
├── hooks/
│   └── useStepAnimation.js    # 시각화 애니메이션 훅
├── App.jsx
├── main.jsx
└── index.css
```

## 라이선스

MIT
