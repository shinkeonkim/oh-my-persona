# npm version era

npm 패키지 이름을 입력하면 [npm registry](https://registry.npmjs.org/)에서 실제
배포 이력을 가져와, 주요 버전들을 시대순 타임라인으로 보여주는 서비스입니다.

- 배포 URL: https://npm-version-era.코드.kr
- React, TypeScript, Vite, shadcn/ui, Framer Motion 기반

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
