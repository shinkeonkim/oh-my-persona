# commit-city

GitHub 사용자명을 입력하면 그 해의 커밋 잔디(contribution graph)를 3D 도시 스카이라인으로 시각화합니다. 커밋 수가 많은 날은 높은 건물로, 적은 날은 공원이나 다리로 표현됩니다. 결과는 SVG/PNG로 내보낼 수 있습니다.

- 배포 URL: https://commit-city.코드.kr
- React, TypeScript, Vite, Three.js(react-three) 기반

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
