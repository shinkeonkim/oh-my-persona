# AWS Certified Cloud Practitioner (CLF-C02) 문제 은행

> **726문항 · 23 카테고리** · 브라우저에서 바로 돌아가는 정적 웹 퀴즈

## 빠른 시작 (30초)

```bash
# 1) 최초 1회만: 마크다운 → JSON 빌드
python3 system/build_bank.py

# 2) 웹 뷰 실행 (택 1)
open system/index.html                  # macOS 기본 브라우저에서 열기
# 또는 로컬 서버 (일부 브라우저의 file:// 제약 회피용)
python3 -m http.server 8765 --directory system
```

브라우저에서 `index.html`을 더블 클릭해도 그대로 열립니다. 의존성/빌드 도구/네트워크 모두 불필요.

## 기능

- **모드**: 전체 / 미풀이만 / 오답만 재풀이
- **순서**: 랜덤 / 순차 (`01-001` → `23-035`)
- **카테고리 필터**: 23개 카테고리 개별 선택 (전체 선택/해제 토글)
- **세션 문항 수**: 무제한 / 10 / 25 / 65(실전 모의고사) / 커스텀
- **진도 자동 저장**: 브라우저 localStorage (문항별 시도/정답/최근 결과 기록)
- **오답 자동 축적** + **오답 노트 마크다운 export**
- **키보드 단축키**: `A~E` / `1~5` 선택 · `Enter` 제출/다음 · `Esc` 나가기
- **다크/라이트 테마**: 자동 감지 + 수동 토글
- **모바일 반응형**: 375px 뷰포트까지 대응

## 파일 구조

```
aws-clf/
├── [01-23]-*/                # 카테고리별 문항 마크다운 (원본)
│   └── *.md                  # 파일당 1문항
├── key-notes/                # 학습 정리 노트 (퀴즈와 무관)
├── README.md                 # 이 문서
└── system/                   # 퀴즈 앱
    ├── build_bank.py         # 마크다운 → bank.js/bank.json 빌더
    ├── bank.js               # 브라우저에서 로드하는 자동 생성 데이터 (커밋 대상)
    ├── bank.json             # 동일 데이터 JSON (스크립트 소비용)
    ├── index.html            # 웹 뷰 진입점
    ├── app.js                # 프론트엔드 로직 (vanilla JS)
    └── style.css             # 스타일 (다크/라이트 · 반응형)
```

## 문항 편집 워크플로

문항 마크다운을 수정하거나 추가한 뒤 데이터를 재빌드하세요:

```bash
python3 system/build_bank.py
# ✅ Built 726 questions across 23 categories
```

퀴즈 앱은 새로고침 시 새 데이터를 로드합니다. 진도는 유지됩니다 (`localStorage` 기반).

### 지원하는 마크다운 형식

```markdown
## Question

<문제 텍스트>  (2개를 선택하세요.)   ← 복수 정답이면 개수 힌트 표기 권장

- [ ] A. <옵션 A>
- [ ] B. <옵션 B>
- [ ] C. <옵션 C>
- [ ] D. <옵션 D>
- [ ] E. <옵션 E>   ← A~E 임의 개수

## Answer

정답: A               ← 단일 정답
정답: B, C            ← 복수 정답 (쉼표 구분)

## Explanation

<정답 설명>

오답 분석

A: <오답 이유>
B: <오답 이유>
...
```

## 진도/오답 데이터

브라우저 localStorage (키 프리픽스 `aws-clf-quiz-v1:`)에 저장됩니다:

| 키 | 내용 |
|---|---|
| `progress` | `{ qid: { attempts, correct, last, lastResult } }` |
| `wrongLog` | 오답 목록 (제출·정답 이력) — 정답 처리 시 자동 제거 |
| `lastSettings` | 홈 화면 마지막 필터 (모드/카테고리/순서/limit) |
| `theme` | `dark` / `light` |

**초기화**: 홈 화면 [진도 초기화] 버튼 (confirm 필요) 또는 브라우저 DevTools → Application → Local Storage에서 해당 origin 정리.

**주의**: localStorage는 브라우저/origin별로 격리됩니다. `file://`로 열 때와 `http://localhost:8765`로 열 때 진도가 분리됩니다. 한 방식으로 고정해 사용하세요.

## 브라우저 지원

- Chrome / Edge 111+
- Safari 16.2+
- Firefox 113+

(`:has()`, `color-mix()` CSS 사용)

## 라이선스/출처

문항 마크다운은 각 저작자의 학습 노트이며, 이 도구는 파싱과 UI만 제공합니다.
