# PatternType — 나의 디자인 패턴 성격 유형은?

> 12개의 코딩 상황 질문을 통해 당신의 코딩 성격을 7가지 디자인 패턴 중 하나로 진단하는 심리테스트

🔗 **사이트**: [pattern-type.코드.kr](https://pattern-type.xn--hy1by51c.kr/)  
📦 **GitHub**: [github.com/kokoa-lab/pattern-type](https://github.com/kokoa-lab/pattern-type)  
👤 **개발자**: [@shinkeonkim](https://github.com/shinkeonkim)

---

## 📖 소개

PatternType은 개발자를 위한 성격 유형 테스트입니다. 프로젝트 설계, 버그 대응, 코드 리뷰, 성능 최적화 등 실제 개발 상황에서의 선택을 통해 당신이 어떤 디자인 패턴에 가까운 개발자인지 알아볼 수 있습니다.

### 7가지 디자인 패턴 유형

| 유형 | 이름 | 한 줄 소개 |
|------|------|-----------|
| 👁️ | **Observer** | 변화의 감지자 — 실시간 데이터 흐름과 상태 변화를 직관적으로 파악 |
| 👑 | **Singleton** | 유일무이한 존재 — 일관된 방식을 고수하는 신뢰의 아이콘 |
| 🏭 | **Factory** | 창조의 대가 — 다양한 솔루션을 빠르게 만들어내는 메이커 |
| 🎯 | **Strategy** | 전략의 마스터 — 상황에 따라 최적의 방법을 선택하는 전략가 |
| 🎨 | **Decorator** | 기능의 연금술사 — 기존의 좋은 것을 더 좋게 만드는 개선의 달인 |
| 🔌 | **Adapter** | 연결의 중재자 — 서로 다른 시스템 간의 소통을 가능하게 하는 조율자 |
| 🏗️ | **Builder** | 체계적인 건축가 — 복잡한 것도 단계별로 차근차근 완성하는 실행가 |

---

## 🚀 시작하기

### 사전 요구사항

- [Node.js](https://nodejs.org/) (v18 이상)
- npm 또는 bun

### 설치 및 실행

```bash
# 저장소 클론
git clone https://github.com/kokoa-lab/pattern-type.git

# 프로젝트 디렉토리 이동
cd pattern-type

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

개발 서버가 실행되면 `http://localhost:5173`에서 확인할 수 있습니다.

### 빌드

```bash
# 프로덕션 빌드
npm run build

# 빌드 미리보기
npm run preview
```

---

## 🛠️ 기술 스택

| 분류 | 기술 |
|------|------|
| **프레임워크** | React 18 + TypeScript |
| **빌드 도구** | Vite |
| **스타일링** | Tailwind CSS |
| **UI 컴포넌트** | shadcn/ui (Radix UI 기반) |
| **애니메이션** | Framer Motion |
| **이미지 저장** | html-to-image |
| **라우팅** | React Router DOM |
| **테스트** | Vitest |

---

## 📁 프로젝트 구조

```
src/
├── components/
│   ├── StartScreen.tsx        # 시작 화면
│   ├── QuestionCard.tsx       # 질문 카드
│   ├── ResultCard.tsx         # 결과 카드
│   ├── PatternDiagram.tsx     # 패턴 다이어그램
│   ├── SocialShareButtons.tsx # 공유 버튼
│   ├── AllPatternsSection.tsx # 전체 패턴 목록
│   ├── NavLink.tsx            # 네비게이션 링크
│   └── ui/                    # shadcn/ui 컴포넌트
├── data/
│   └── questions.ts           # 질문 및 결과 데이터
├── pages/
│   ├── Index.tsx              # 메인 페이지
│   └── NotFound.tsx           # 404 페이지
├── hooks/                     # 커스텀 훅
├── lib/                       # 유틸리티
└── docs/
    └── pattern-types.md       # 패턴 유형 상세 문서
```

---

## 🎮 동작 방식

1. **시작 화면** — 테스트 소개 및 시작 버튼
2. **12개 질문** — 각 질문마다 4개의 선택지 제시
3. **점수 산정** — 각 선택지에는 7개 패턴별 가중치(0~3점)가 부여되며, 응답마다 누적
4. **결과 표시** — 최고 점수 패턴을 사용자의 유형으로 진단
5. **결과 공유** — 이미지 저장, 링크 복사 기능 제공

### 결과 URL 공유

결과는 URL 쿼리 파라미터로 공유됩니다:

```
https://pattern-type.xn--hy1by51c.kr/?result=observer
```

---

## 🧪 테스트

```bash
# 테스트 실행
npm test

# 워치 모드
npm run test:watch
```

---

## 📄 라이선스

이 프로젝트는 오픈소스입니다. 자세한 내용은 [GitHub 저장소](https://github.com/kokoa-lab/pattern-type)를 참고해주세요.

---

## 🤝 기여

버그 리포트, 기능 제안, PR 모두 환영합니다! [Issues](https://github.com/kokoa-lab/pattern-type/issues)에서 시작해주세요.
