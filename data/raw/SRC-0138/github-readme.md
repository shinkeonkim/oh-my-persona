# 🃏 DevTarot

> 개발자를 위한 타로 운세 — 오늘의 코딩 운세를 뽑아보세요!

[![Live](https://img.shields.io/badge/Live-dev--tarot.코드.kr-blue)](https://dev-tarot.xn--hy1by51c.kr/)
[![GitHub](https://img.shields.io/github/stars/kokoa-lab/dev-tarot?style=social)](https://github.com/kokoa-lab/dev-tarot)

## 🔗 Links

- **사이트**: [https://dev-tarot.코드.kr](https://dev-tarot.xn--hy1by51c.kr/)
- **GitHub**: [https://github.com/kokoa-lab/dev-tarot](https://github.com/kokoa-lab/dev-tarot)

## ✨ Features

- **타로 카드 뽑기** — 3장의 후보 카드 중 1장을 선택하여 오늘의 코딩 운세를 확인
- **3D 카드 플립 애니메이션** — 카드 선택 후 클릭하면 자연스러운 뒤집기 효과
- **이미지 저장 & 복사** — 뽑은 카드를 이미지로 저장하거나 클립보드에 복사
- **뽑기 히스토리** — 이전에 뽑았던 카드 기록 확인
- **22장의 메이저 아르카나** — 각 카드마다 개발자 맞춤 운세, 조언, 럭키 스택 제공
- **사운드 효과** — 카드 플립/리셋 시 효과음
- **파티클 이펙트** — 카드 공개 시 시각적 연출

## 🛠️ Tech Stack

| 분류 | 기술 |
|------|------|
| Framework | React + TypeScript |
| Build Tool | Vite |
| Styling | Tailwind CSS |
| UI Components | shadcn/ui |
| Image Capture | html2canvas |
| Animation | CSS 3D Transforms, Framer Motion |

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ & npm (또는 bun)

### Installation

```bash
# 1. 레포지토리 클론
git clone https://github.com/kokoa-lab/dev-tarot.git

# 2. 프로젝트 디렉토리 이동
cd dev-tarot

# 3. 의존성 설치
npm install

# 4. 개발 서버 실행
npm run dev
```

브라우저에서 `http://localhost:5173`으로 접속하세요.

## 📁 Project Structure

```
src/
├── assets/
│   ├── cards/          # 22장의 타로 카드 이미지
│   └── card-back.png   # 카드 뒷면 이미지
├── components/
│   ├── CardPicker.tsx       # 3장 중 1장 선택 UI
│   ├── TarotCard.tsx        # 3D 플립 카드 컴포넌트
│   ├── TarotCardFront.tsx   # 카드 앞면 (운세 표시)
│   ├── CardHistory.tsx      # 히스토리 목록
│   ├── ParticleEffect.tsx   # 파티클 연출
│   └── ui/                  # shadcn/ui 컴포넌트
├── data/
│   ├── tarotCards.ts        # 22장 카드 데이터 (운세, 조언, 럭키 스택)
│   └── cardImages.ts        # 카드 이미지 매핑
├── lib/
│   ├── history.ts           # localStorage 기반 히스토리
│   ├── imageCapture.ts      # html2canvas 캡처 로직
│   ├── sounds.ts            # 효과음
│   └── utils.ts             # 유틸리티
└── pages/
    └── Index.tsx             # 메인 페이지
```

## 🎴 카드 목록

| # | 카드 | 분위기 | 럭키 스택 |
|---|------|--------|-----------|
| 0 | 바보 (The Fool) | 🟢 great | Rust |
| 1 | 마법사 (The Magician) | 🟢 great | TypeScript |
| 2 | 여사제 (The High Priestess) | 🔵 good | Python |
| 3 | 여황제 (The Empress) | 🟢 great | Swift |
| 4 | 황제 (The Emperor) | 🔵 good | Java |
| 5 | 교황 (The Hierophant) | ⚪ neutral | C++ |
| 6 | 연인 (The Lovers) | 🟢 great | React |
| 7 | 전차 (The Chariot) | 🟢 great | Go |
| 8 | 힘 (Strength) | 🔵 good | Kotlin |
| 9 | 은둔자 (The Hermit) | 🔵 good | Vim |
| 10 | 운명의 수레바퀴 (Wheel of Fortune) | 🟡 caution | Docker |
| 11 | 정의 (Justice) | ⚪ neutral | ESLint |
| 12 | 매달린 사람 (The Hanged Man) | ⚪ neutral | Haskell |
| 13 | 죽음 (Death) | 🟡 caution | Bash |
| 14 | 절제 (Temperance) | ⚪ neutral | Ruby |
| 15 | 악마 (The Devil) | 🟡 caution | PHP |
| 16 | 탑 (The Tower) | 🔴 danger | Grafana |
| 17 | 별 (The Star) | 🟢 great | Next.js |
| 18 | 달 (The Moon) | ⚪ neutral | Neovim |
| 19 | 태양 (The Sun) | 🟢 great | Svelte |
| 20 | 심판 (Judgement) | 🔵 good | Webpack |
| 21 | 세계 (The World) | 🟢 great | Full Stack |

## 👤 Author

- **shinkeonkim** — [@shinkeonkim](https://github.com/shinkeonkim)

## 📄 License

This project is open source under the [MIT License](LICENSE).
