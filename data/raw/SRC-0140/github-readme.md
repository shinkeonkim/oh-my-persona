# Duck Therapy

러버덕 디버깅 상담소입니다. 러버덕 디버깅(rubber duck debugging)이란 자신의 코드를
누군가에게 설명하다 보면 스스로 문제를 찾게 되는 방법인데, 그 상대를 사람 대신
"Dr. 꽥꽥"이라는 오리로 대체했습니다. 오리에게 버그를 털어놓으면 정해진 규칙에 따라
반응하며 꽥꽥 소리를 내고, 대화를 충분히 나누면 디버깅 상담 완료 증명서를 발급해줍니다.

- 배포 URL: https://duck-therapy.코드.kr
- React, TypeScript, Vite, shadcn/ui 기반. 오리의 응답은 외부 AI API 없이
  `src/lib/duckEngine.ts`의 규칙 기반 로직으로 생성됩니다.

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
