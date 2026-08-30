# cookie-bakery

쿠키(과자)를 굽는 과정에 빗대어 HTTP 쿠키의 동작을 배우는 단계별 학습 게임입니다. 반죽 만들기 → 오븐에 넣기 → 유통기한(Expires/Max-Age) → 포장 옵션(HttpOnly, Secure, SameSite 등)까지, 각 단계마다 퀴즈를 맞혀야 다음으로 진행할 수 있습니다.

- 배포 URL: https://cookie-bakery.코드.kr
- React, TypeScript, Vite, shadcn/ui 기반

## 개발 및 실행

```bash
# 의존성 설치
bun install

# 개발 서버 실행
bun dev
```

## 빌드

```bash
bun run build
```

## Cloudflare Workers 배포

정적 산출물(`dist/`)을 Cloudflare Workers assets로 배포합니다.

```bash
bun run build
bunx wrangler deploy
```
