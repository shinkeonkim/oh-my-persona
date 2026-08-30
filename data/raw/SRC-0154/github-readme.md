# Works on Mine

"제 컴퓨터에선 되는데요"를 공식 증명서로 발급합니다. 정보를 입력하면 도장이 찍힌
인증서 형태로 만들어줍니다.

- 배포 URL: https://works-on-mine.코드.kr
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
