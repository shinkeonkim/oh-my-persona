<p align="center">
  <img width="678" height="200" alt="Image" src="https://github.com/user-attachments/assets/a114446f-2e47-44f1-8f96-e76a4d681422" />  
</p>


> 슬롯머신을 돌려서 코드리뷰 코멘트를 생성하는 웹 애플리케이션

[![GitHub](https://img.shields.io/badge/GitHub-shinkeonkim/review--slot-181717?logo=github)](https://github.com/shinkeonkim/review-slot)

## 📖 소개

**ReviewSlot**은 코드리뷰 코멘트 작성이 어려운 개발자를 위한 재미있는 도구입니다.
슬롯머신 UI를 통해 **톤 × 내용 × 액션** 조합으로 다양한 리뷰 코멘트를 랜덤 생성합니다.

## ✨ 주요 기능

### 🎰 슬롯머신 코멘트 생성
- **5가지 톤**: 정중한 🎩 | 직설적 🔥 | 유머러스 😂 | 감성적 🌙 | 선배미 💼
- **5가지 내용**: 네이밍 📝 | 성능 ⚡ | 가독성 👁️ | 아키텍처 🏗️ | 에러처리 🛡️
- **4가지 액션**: 수정 요청 🔧 | 칭찬 👏 | 질문 ❓ | 제안 💡
- 총 **100가지** 고유한 코멘트 조합

### 🔊 사운드 이펙트
- Web Audio API 기반 프로시저럴 SFX (외부 에셋 불필요)
- 릴 회전음, 정지음, 잭팟 효과음, 복사 효과음
- 사운드 ON/OFF 토글 지원

### 🎆 잭팟 이펙트
- 세 릴의 인덱스가 모두 일치하면 잭팟 발동
- 화면 번쩍임 + 파티클 폭발 애니메이션

### 📋 클립보드 복사
- 생성된 코멘트를 원클릭으로 클립보드에 복사
- 히스토리 항목도 바로 복사 가능

### 📜 히스토리
- 최근 3개의 생성 결과를 자동 저장
- 톤/내용/액션 태그와 함께 표시

### 📱 반응형 디자인
- 모바일, 태블릿, 데스크톱 모두 지원
- 레트로 아케이드 테마 UI

## 🛠️ 기술 스택

| 기술 | 용도 |
|------|------|
| **React 18** | UI 프레임워크 |
| **TypeScript** | 타입 안전성 |
| **Vite** | 빌드 도구 |
| **Tailwind CSS** | 스타일링 |
| **shadcn/ui** | UI 컴포넌트 |
| **Web Audio API** | 사운드 이펙트 |

## 🚀 시작하기

### 사전 요구사항

- Node.js 18+ 
- npm 또는 bun

### 설치 및 실행

```bash
# 1. 저장소 클론
git clone https://github.com/shinkeonkim/review-slot.git

# 2. 디렉토리 이동
cd review-slot

# 3. 의존성 설치
npm install

# 4. 개발 서버 실행
npm run dev
```

브라우저에서 `http://localhost:5173`으로 접속하세요.

### 빌드

```bash
# 프로덕션 빌드
npm run build

# 빌드 프리뷰
npm run preview
```

### 테스트

```bash
npm run test
```

## 📁 프로젝트 구조

```
src/
├── components/
│   ├── JackpotEffect.tsx      # 잭팟 시각 효과 (번쩍임 + 파티클)
│   ├── ReviewSlotMachine.tsx   # 메인 슬롯머신 컴포넌트
│   ├── SlotReel.tsx            # 개별 릴 컴포넌트
│   ├── NavLink.tsx             # 네비게이션 링크
│   └── ui/                    # shadcn/ui 컴포넌트
├── data/
│   └── reviewComments.ts      # 100가지 코멘트 매트릭스 데이터
├── lib/
│   ├── sounds.ts              # Web Audio API 사운드 생성
│   └── utils.ts               # 유틸리티 함수
├── pages/
│   ├── Index.tsx               # 메인 페이지
│   └── NotFound.tsx            # 404 페이지
├── App.tsx                     # 라우팅 설정
└── main.tsx                    # 엔트리포인트
```

## 🎮 사용 방법

1. **SPIN 버튼**을 클릭하여 슬롯머신을 돌립니다
2. 세 개의 릴이 차례로 멈추며 **톤**, **내용**, **액션**이 결정됩니다
3. 조합에 해당하는 **코드리뷰 코멘트**가 생성됩니다
4. **복사 버튼**을 눌러 클립보드에 복사합니다
5. PR 리뷰에 붙여넣기 하세요!

> 💡 **팁**: 세 릴의 인덱스가 모두 같으면 🎆 **잭팟 이펙트**가 발동합니다!

## 👤 만든 사람

- **shinkeonkim** — [GitHub](https://github.com/shinkeonkim)

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
