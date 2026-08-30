# cors-port

공항 출입국 심사에 빗대어 CORS(Cross-Origin Resource Sharing)를 배우는 시뮬레이터입니다. 요청 출처(Origin)·메서드·헤더를 직접 설정해 프리플라이트(사전 심사) 요청이 발생하는지, 서버의 `Access-Control-Allow-*` 설정에 따라 요청이 통과되는지 애니메이션으로 확인할 수 있습니다. Same-Origin Policy 등 관련 개념 설명 페이지도 함께 제공합니다.

- 배포 URL: https://cors-port.코드.kr
- React, TypeScript, Vite, shadcn/ui, Framer Motion 기반

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
