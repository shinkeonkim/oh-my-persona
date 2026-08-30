# meFit · 캡스톤디자인 54팀 발표 포스터

가로 **930 mm** × 세로 **1000 mm** 크기의 인쇄용 발표 포스터.

React 19 + TypeScript + Vite + Bun + Tailwind 4 로 구성되며,
모든 사이즈/타이포는 `mm` 단위로 정의해 인쇄 결과와 화면 미리보기가 일치합니다.

## 폴더 구조

```
poster/
├── package.json              # Vite + Bun + React + Tailwind 4
├── vite.config.ts            # base: "./" (file:// 미리보기 호환)
├── index.html                # Pretendard / Inter Tight / IBM Plex Sans KR / JetBrains Mono
├── public/
│   ├── logo-korean.png
│   ├── logo2.png
│   └── diagrams/             # mefit-diagrams 산출물 사본
│       ├── full_infrastructure.png
│       ├── aws_infrastructure.png
│       └── k8s_infrastructure.png
├── src/
│   ├── main.tsx · App.tsx
│   ├── styles.css            # @page 930mm 1000mm + screen scale
│   ├── data.ts               # 모든 콘텐츠 (학번, 키워드, 기능, 스택)
│   └── components/
│       ├── Toolbar.tsx       # Fit / 100% / Print
│       ├── Poster.tsx        # 8x2 grid 레이아웃
│       ├── Header.tsx
│       ├── HeroBlock.tsx     # 큰 "54" + 한 줄 카피
│       ├── KeywordsBlock.tsx
│       ├── TargetBlock.tsx
│       ├── EffectsBlock.tsx
│       ├── FeaturesBlock.tsx # 6 기능 (1 big + 5)
│       ├── ArchitectureBlock.tsx
│       ├── TechStackBlock.tsx
│       ├── TeamBlock.tsx
│       └── Footer.tsx
└── scripts/
    ├── export-pdf.mjs        # Playwright headless → PDF
    └── export-png.mjs        # Playwright headless → PNG
```

## 로컬 개발

```bash
bun install
bun run dev          # http://localhost:5174 (또는 vite 로그 참고)
```

화면 우상단 툴바:

| 버튼 | 동작 |
|---|---|
| Fit | 뷰포트 폭에 맞춰 자동 축소 (기본) |
| 100% | 실제 크기 (스크롤 필수) |
| Print / PDF | 브라우저 인쇄 다이얼로그 (`Ctrl+P` / `⌘+P`) |

브라우저 인쇄 다이얼로그에서 "용지 크기: 사용자 지정 → 930mm × 1000mm",
"여백: 없음", "배경 그래픽 인쇄 ON" 으로 PDF 저장하면 됩니다.

## Export (Playwright headless)

수동 인쇄 없이 자동으로 PDF / PNG / A4 분할 산출:

```bash
bun install                     # 최초 1회
bunx playwright install chromium  # 최초 1회 (또는 npx)

bun run build                  # vite 빌드 → dist/
bun run export:pdf             # output/mefit-poster-54.pdf
bun run export:png             # output/mefit-poster-54.png
bun run export:a4              # output/mefit-poster-54-a4-tiles.pdf  (A4 20장)

bun run export                 # 빌드 + PDF + PNG + A4 한 번에
```

산출물 경로: `poster/output/`

| 파일 | 사이즈 / 페이지 | 용도 |
|---|---|---|
| `mefit-poster-54.pdf` | 930 × 1000 mm (1 page) | 인쇄소 입고용 (벡터) |
| `mefit-poster-54.png` | ≈ 7030 × 7560 px @ 2x | 웹/슬라이드/미리보기 |
| `mefit-poster-54-a4-tiles.pdf` | A4 portrait × 20 (5 cols × 4 rows) | **사무실 A4 출력 분할 인쇄** |

### A4 분할 인쇄 (사무실 환경에서 미리 검토)

`mefit-poster-54-a4-tiles.pdf` 는 930 × 1000 mm 포스터를
**A4 세로 5 열 × 4 행 = 20 장**으로 자른 PDF 입니다.

- 각 페이지 우하단에 `A1 / A2 / B1 / ...` 좌표 라벨이 인쇄됩니다.
- 여백 없는 옵션(Print to scale 100%, no fit) 으로 출력해야 정확한 크기.
- 인쇄 후 가위로 트리밍 → 행/열 순서대로 붙이면 실제 출력 사이즈로 검토 가능.

### 외부 도구 활용 (스크립트 안 쓸 때)

- **macOS Preview** 에서 `mefit-poster-54.pdf` 를 열고 인쇄 다이얼로그
  → "Scale: Tile" → A4 용지 선택 시 자동 분할 인쇄.
- **Adobe Reader** "Poster" 옵션도 동일하게 동작.

### 환경변수

- `POSTER_PORT=4188` 등으로 포트 변경 (frontend dev 서버와 충돌 회피)
- `POSTER_SCALE=3` 으로 PNG 3x DPR (≈ 10500 × 11340 px) 출력

## 학번 / 콘텐츠 수정

모든 콘텐츠는 [`src/data.ts`](./src/data.ts) 한 파일에 모여 있습니다.

```ts
export const members = [
  {
    studentId: "20XX1111",   // ← 실제 학번으로 교체
    name: "김신건",
    role: "PM",
    description: "...",
  },
  // ...
];
```

수정 후 `bun run dev` 에서 즉시 반영됩니다.

## 디자인 토큰

`frontend/` 와 `github-page/` 와 동일한 토큰 사용:

| 토큰 | 값 |
|---|---|
| accent | `#0991B2` |
| accent-mid | `#06B6D4` |
| accent-bg | `#E6F7FA` |
| accent-deep | `#0E7490` |
| fg | `#0A0A0A` |
| muted | `#6B7280` |
| canvas / bg-soft | `#FFFFFF` / `#F9FAFB` |
| 폰트 | Pretendard Variable + Inter Tight + IBM Plex Sans KR + JetBrains Mono |

## 인쇄 스펙

- CSS `@page { size: 930mm 1000mm; margin: 0; }` 으로 인쇄 시 정확 사이즈 확정
- `print-color-adjust: exact` 로 배경/그라데이션 보존
- 모든 폰트 사이즈 / 패딩 / 그리드는 `mm` 단위로 정의 → 화면 미리보기 = 인쇄 결과
- 표준 인쇄 파일 (PDF) 와 web 공유용 (PNG) 두 버전 산출
