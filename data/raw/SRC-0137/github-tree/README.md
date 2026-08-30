# Cozy Hive

나의 작은 양봉장을 가꾸는 방치형(idle) 양봉 시뮬레이션 게임입니다. 벌집을 관리하고,
연구를 통해 업그레이드하고, 말벌의 습격을 막아내는 미니게임을 즐기고, 프레스티지로
다시 시작할 수 있습니다.

- 배포 URL: https://cozy-hive.코드.kr
- React, TypeScript, Vite, shadcn/ui 기반

## 개발 및 실행

```bash
# 의존성 설치
bun install

# 개발 서버 실행
bun run dev
```

## 빌드

```bash
bun run build
```

## Cloudflare Workers 배포

정적 산출물(`./dist`)을 [wrangler](https://developers.cloudflare.com/workers/wrangler/)로
Cloudflare Workers(assets)에 배포합니다.

```bash
bun run build
wrangler deploy
```
