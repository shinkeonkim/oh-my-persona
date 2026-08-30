# 트랜잭션 격리수준 완벽 가이드

트랜잭션 격리수준(Transaction Isolation Level)을 시각적으로 소개하는 정적 웹사이트입니다.

## 주요 내용

### 4가지 격리수준

| 수준 | 설명 |
|------|------|
| READ UNCOMMITTED | 커밋되지 않은 변경 데이터까지 읽음. 가장 낮은 격리 수준 |
| READ COMMITTED | 커밋 완료된 데이터만 읽음. PostgreSQL/Oracle/SQL Server 기본값 |
| REPEATABLE READ | 동일 행 재조회 시 같은 값 보장. MySQL InnoDB 기본값 |
| SERIALIZABLE | 완전한 직렬화. 가장 높은 정합성, 가장 낮은 성능 |

### 3가지 동시성 문제

- **Dirty Read** — 아직 커밋되지 않은 데이터를 읽는 현상
- **Non-Repeatable Read** — 동일 행을 두 번 읽었을 때 값이 다른 현상
- **Phantom Read** — 동일 쿼리를 두 번 실행했을 때 결과 집합이 다른 현상

### 격리수준별 문제 발생 여부

| 격리수준 | Dirty Read | Non-Repeatable Read | Phantom Read |
|---------|:----------:|:-------------------:|:------------:|
| READ UNCOMMITTED | 발생 | 발생 | 발생 |
| READ COMMITTED | 미발생 | 발생 | 발생 |
| REPEATABLE READ | 미발생 | 미발생 | 발생 |
| SERIALIZABLE | 미발생 | 미발생 | 미발생 |

## 개발

```bash
bun install
bun run dev
bun run build
bun run deploy
```

Vite + React + TypeScript 기반이며, Cloudflare Workers Static Assets를 통해 `dist` 디렉터리를 배포합니다.

## 디자인 시스템

`DESIGN.md`의 **Corporate Trust** 디자인 시스템을 기반으로 제작되었습니다.

- **색상**: Indigo / Violet 그라디언트와 Slate 기반 엔터프라이즈 팔레트
- **타이포그래피**: Plus Jakarta Sans
- **시각화**: 격리 수준과 SQL 시나리오를 결합한 Sticky Scroll Story
- **애니메이션**: IntersectionObserver 기반 단계 전환과 트랜잭션 타임라인

## 구현 특징

- React 컴포넌트 및 콘텐츠 데이터 모듈 분리
- 완전 반응형 (모바일 우선)
- `prefers-reduced-motion` 지원
- WCAG AA 대비 준수
- 인터랙티브 비교표 (격리수준 선택 하이라이트)
- IntersectionObserver 기반 스크롤 리빌 + 바 애니메이션
- 키보드 내비게이션 지원 (테이블 행 Enter/Space)
- JSON-LD 구조화 데이터, Open Graph, Twitter Card SEO

## 참고 자료

- [MySQL 트랜잭션 격리수준 완벽 이해](https://mangkyu.tistory.com/299)
- [Wikipedia — Isolation (database systems)](https://en.wikipedia.org/wiki/Isolation_(database_systems))
- [Stack Overflow — MySQL 팬텀 리드 재연](http://stackoverflow.com/questions/42794425/unable-to-produce-a-phantom-read/42796969#42796969)
- [10분 테코톡 — 러쉬의 MySQL 트랜잭션 격리 수준](https://youtu.be/QHWwNTGkwAU?si=AMYGpIry6nCPosuu)
