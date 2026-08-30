# 발표 자료 PDF 처리 워크플로우

큰 PDF 발표 자료를 페이지별 이미지 슬라이드 갤러리로 변환하여 사이트에 임베드하는 표준 워크플로우입니다.

## 언제 사용하나요?

- PDF 파일이 5MB 이상이거나 페이지 수가 많은 발표 자료
- 사이트 방문자가 PDF 다운로드 없이 페이지별로 미리보기를 보아야 할 때
- 모바일 환경에서도 빠르게 로드되어야 할 때

**작은 PDF (~ 1MB)는 `links` 에 `type: 'pdf'` 로 단순 첨부**가 더 간단합니다. Sellon 프로젝트 발표 자료(464KB)가 그 예시입니다.

## 1. 사전 요구사항

```bash
brew install poppler
```

`pdftoppm` 과 `pdfinfo` 가 PATH에 있어야 합니다.

## 2. 변환 + 자산 배치 (스크립트 1회 실행)

```bash
scripts/add-project-presentation.sh <PDF_PATH> <PROJECT_SLUG> [옵션]
```

### 예시

```bash
scripts/add-project-presentation.sh ~/Downloads/mefit-final.pdf mefit
scripts/add-project-presentation.sh "~/Downloads/깜빡이 발표자료.pdf" kkambbaki --dpi=80 --title="4호선톤 발표"
```

### 옵션

| 옵션 | 기본값 | 설명 |
|---|---|---|
| `--dpi=N` | `72` | 페이지 이미지 해상도. 1920×1080 슬라이드 기준 72이면 1:1 픽셀. 더 선명하게 하려면 100~150. |
| `--quality=N` | `85` | JPEG 압축 품질 (1-100). 85 면 시각적 손상 거의 없음. 용량 줄이려면 70~75. |
| `--title='...'` | `발표 자료` | 컴포넌트 제목 + 스니펫에 들어갈 라벨. |

### 스크립트가 만드는 것

| 파일 | 설명 |
|---|---|
| `public/docs/<slug>-presentation.pdf` | PDF 원본 (다운로드 버튼용) |
| `public/images/projects/<slug>/presentation/page-01.jpg` ~ `page-NN.jpg` | 페이지별 JPEG |

## 3. 데이터 등록

스크립트 출력 마지막 부분에 `src/data/projects/<slug>.ts` 에 붙여넣을 TypeScript 스니펫이 표시됩니다.

```typescript
import type { Project } from '@/types'

const IMG = '/my-portfolio/images/projects/mefit'

export const mefit: Project = {
  // ... 기존 필드
  presentation: {
    title: '발표 자료',
    caption: '18페이지',
    totalPages: 18,
    pdfUrl: '/my-portfolio/docs/mefit-presentation.pdf',
    pageImages: [
      `${IMG}/presentation/page-01.jpg`,
      // ... 자동 생성됨
    ],
  },
}
```

`presentation` 필드만 추가하면 [PresentationSlideViewer](../src/components/common/PresentationSlideViewer.vue) 가 자동으로 렌더링됩니다. 별도 컴포넌트 등록 불필요.

### Links 에 PDF 첨부 (선택)

원본 PDF 다운로드 버튼을 Links 섹션에도 노출하려면:

```typescript
links: [
  // ... 기존 링크
  {
    label: '발표 자료 (PDF)',
    url: '/my-portfolio/docs/mefit-presentation.pdf',
    type: 'pdf',
  },
],
```

## 4. 시각 확인

```bash
bun run dev
# 브라우저에서 http://localhost:5173/my-portfolio/projects/<slug>
```

확인 항목:
- 슬라이드 갤러리가 "발표 자료" 섹션에 렌더링됨
- 좌/우 화살표 버튼 + 키보드 ← → 동작
- 하단 썸네일 스트립 클릭으로 직접 이동
- 우측 상단 "PDF 원본" 다운로드 버튼

## 5. 빌드 + 배포

```bash
bun run type-check && bun run build
git add public/docs public/images/projects/<slug>/presentation src/data/projects/<slug>.ts
git commit -m "feat: <slug> 프로젝트 발표 자료 슬라이드 갤러리 추가"
```

## 트러블슈팅

| 증상 | 해결 |
|---|---|
| 변환 후 jpg가 너무 큼 (페이지당 1MB+) | `--dpi=60 --quality=75` 로 재실행 |
| 변환 결과가 흐림 | `--dpi=100 --quality=95` 로 재실행 (단, 용량 1.5~2배) |
| `pdftoppm: command not found` | `brew install poppler` |
| 변환 페이지 일부만 필요 | 스크립트는 전체 페이지 변환만 지원. 부분 변환은 직접 `pdftoppm -f START -l END ...` 실행 후 수동 배치 |
| PDF가 이미 `public/` 에 있을 때 | 그대로 첫 인자로 경로 전달 가능. 스크립트가 `public/docs/` 로 복사 + 원본은 별도 정리 필요 |

## 참고: 단순 PDF 링크만 추가하는 경우

작은 PDF는 변환 없이 첨부만:

```bash
mkdir -p public/docs
cp ~/Downloads/foo.pdf "public/docs/foo-presentation.pdf"
```

```typescript
links: [
  { label: '발표 자료 (PDF)', url: '/my-portfolio/docs/foo-presentation.pdf', type: 'pdf' },
],
```

## 관련 파일

- 스크립트: [scripts/add-project-presentation.sh](../scripts/add-project-presentation.sh)
- 컴포넌트: [src/components/common/PresentationSlideViewer.vue](../src/components/common/PresentationSlideViewer.vue)
- 타입: [`ProjectPresentation`](../src/types/project.ts)
- 적용 예시: [src/data/projects/kkambbaki.ts](../src/data/projects/kkambbaki.ts)
