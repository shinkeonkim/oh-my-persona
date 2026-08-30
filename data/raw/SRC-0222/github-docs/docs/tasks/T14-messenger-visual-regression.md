# T14 — 메신저 UI 재설계와 시각 회귀

상태: DONE (2026-08-30)
선행: T13

## 변경

- 데스크톱: 연락처·추천 질문 사이드바와 독립 채팅 패널의 2열 메신저
- 모바일: 화면 전체를 사용하는 단일 대화, safe-area 하단 입력창, 가로 overflow 방지
- 공통: 온라인 상태, 보이는 모델명, 추천 질문, 메시지 시각, 접을 수 있는 근거, 새 대화
- Playwright 1440×1000 및 iPhone 15 스냅샷과 레이아웃·상호작용 검증

## 완료 기준

- `npm run test:ui`의 데스크톱·모바일 스냅샷 비교가 통과한다.
- 입력창이 뷰포트 밖으로 나가지 않고 모바일 가로 overflow가 없다.
- 추천 질문을 누르면 입력창에 값이 채워지고 포커스된다.
- 운영 배포 후 동일 viewport의 Playwright 캡처를 다시 확인한다.

## 검증 결과

- GitHub CI: Python 18개 테스트, Docker build, Playwright 데스크톱·모바일 시각 회귀 통과
- 운영 URL: `https://persona.shinkeonkim.com`
- 데스크톱 1440×1000: messenger 1180×860, 사이드바 표시, composer 내부 배치
- 모바일 390×844: messenger 390×844, 사이드바 숨김, 가로 overflow 0
- 운영 이미지: `sha256:88964b4bfb5ea154bbacd5532f5ccf68adb76facc6703b209908670a69594be6`
- GitOps: `oh-my-homelab` PR #90 및 #91 검증·병합 완료
