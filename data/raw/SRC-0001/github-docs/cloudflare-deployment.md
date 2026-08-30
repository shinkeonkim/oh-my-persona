# Cloudflare Workers Builds 배포 가이드 (Vite + Bun)

이 문서는 Cloudflare의 **Workers Builds (Unified UI)** 환경에서 Vite 프로젝트를 배포하는 방법을 설명합니다. 모든 프로젝트가 Worker로 관리되며, `npx wrangler deploy`가 배포 명령으로 사용됩니다.

## 1. 프로젝트 설정 (`wrangler.json`)

프로젝트 루트의 `wrangler.json`이 빌드 결과물(`dist`) 서빙 및 커스텀 도메인 바인딩을 담당합니다.

```json
{
  "name": "my-resume",
  "compatibility_date": "2026-01-07",
  "assets": {
    "directory": "dist",
    "not_found_handling": "single-page-application"
  },
  "routes": [
    {
      "pattern": "resume.shinkeonkim.com",
      "custom_domain": true
    }
  ],
  "observability": {
    "enabled": true
  }
}
```

- `assets.directory`: Vite 빌드 산출물(`dist`)을 그대로 서빙
- `assets.not_found_handling`: SPA fallback (`single-page-application`)
- `routes[].custom_domain`: `wrangler deploy` 시 커스텀 도메인을 자동으로 바인딩 (zone이 Cloudflare에 있어야 함)

## 2. variant 빌드 (`bun run build:site`)

`resume.shinkeonkim.com`에는 base 이력서와 public variant가 함께 배포됩니다.

- `scripts/build-site.ts`가 base를 `dist/`에 빌드한 뒤, `visibility: public`인 variant를 각각 빌드하여 `dist/v/<id>/`에 병합합니다.
- `draft`/`private` variant는 절대 배포되지 않습니다.
- 로컬에서 `bun run build:site`로 동일한 결과물을 재현할 수 있습니다.

## 3. Cloudflare Dashboard 빌드 설정

Cloudflare 대시보드의 **Workers & Pages > 프로젝트 > Settings > Build & deployments** 에서 설정합니다.

| 설정 항목 | 값 | 설명 |
| :--- | :--- | :--- |
| **Build command** | `bun run build:site` | type-check + base/variant 전체 빌드 (dist 생성) |
| **Deploy command** | `npx wrangler deploy` | `wrangler.json`을 읽어 배포 + 커스텀 도메인 바인딩 |
| **Production branch** | `main` | 기본 브랜치 push 시 프로덕션 배포 |

## 4. 주의 사항
- **인증**: 대시보드 연동 환경에서는 GitHub 계정 연결만으로 충분하며, 별도 `CLOUDFLARE_API_TOKEN`이 필요하지 않습니다.
- **커스텀 도메인**: `wrangler deploy`가 `routes`의 `custom_domain`을 바인딩합니다. 자동 바인딩이 실패할 경우 대시보드 **Settings > Domains & Routes > Add custom domain**에서 `resume.shinkeonkim.com`을 직접 추가할 수 있습니다.
- **리다이렉트**: 기존 GitHub Pages 주소(`resume.shinkeonkim.com/`) 유입을 새 주소로 옮기려면 zone에 리다이렉트 규칙(Redirect Rule)을 추가하세요.
