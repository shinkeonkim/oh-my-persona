# Stack Digger

키워드를 입력하면 Stack Exchange의 오래된(2008~2013년) 답변들을 시대별 지층처럼
파고 들어가며 찾아주는 웹 서비스입니다. 최신 답변이 얕은 지층, 오래된 답변일수록
깊은 지층에 있는 "발굴물"로 표시됩니다.

- 배포 URL: https://stack-digger.코드.kr
- React, TypeScript, Vite, Tailwind CSS 기반

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

## Cloudflare Pages 배포

정적 빌드 산출물(`dist/`)을 Cloudflare Pages에 SPA로 배포합니다
([wrangler](https://developers.cloudflare.com/workers/wrangler/) 설정은
`wrangler.toml` 참고).
