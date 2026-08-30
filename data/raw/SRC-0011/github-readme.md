# CV - 김신건

[보러가기](http://singun11.wtf/my-cv)

A4 1장 분량의 CV. Vue 3 + TypeScript + Vite 기반.

## 파일 구조

- `src/App.vue` — 최상위 컴포넌트 (`PrintButton` + `CvPage`)
- `src/components/CvPage.vue` — `CvSidebar` + `CvMain` 페이지 레이아웃
- `src/components/CvSidebar.vue` — 좌측 사이드바 (Contact / Skills / Education / Certifications / Awards / Activities)
- `src/components/CvMain.vue` — 우측 메인 (Header / About / Work Experience / Projects)
- `src/components/sections/` — 각 섹션 컴포넌트
- `src/data/` — 섹션별 데이터 소스 (`profile`, `contact`, `skills`, `education`, `certifications`, `awards`, `activities`, `experiences`, `projects`)
- `src/types/cv.ts` — 데이터 타입 정의
- `src/assets/main.css` / `main-area.css` — 글로벌 스타일 (A4 레이아웃, print 규칙 포함)
- `cv-original.html` — 기존 HTML 원본 (참고용 백업)
- `CV.pdf` — PDF 출력본

## 개발

```sh
bun install
bun dev
bun run type-check
bun run lint
bun run build
```

## 배포

`main` 브랜치 push 시 `.github/workflows/deploy.yml` 워크플로가 GitHub Pages로 배포합니다.
