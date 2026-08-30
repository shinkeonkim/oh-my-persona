# 저작권 보호 정책

## 원칙

SAA/CLF 문항 원문은 개인 학습용 보호 자료다. 외부 공개 페이지, 로그, 검색 엔진, Git diff,
정적 frontend bundle에 포함하지 않는다. AIF 원본은 현재 공개 저장소지만 출처 정책이 바뀌면
동일한 보호 수준으로 전환한다.

## 공개 가능한 내용

- AWS 서비스의 일반 개념과 관계
- 시나리오의 대표 신호어
- 정답 방향과 함정 유형을 일반화한 설명
- AWS 공식 문서에서 확인 가능한 사양

## 제거 대상

- 원본 문제 수와 문항 수
- 문제 분포, 정답 분포, 비율
- 원본 문항 파일로 가는 직접 링크
- “N문제 풀기”, “문제 은행 홈” 등 원본 수량을 드러내는 UI

`packages/content/src/copyright-filter.ts`가 학습 노트 적재 전에 이를 제거한다.

## 검증

```bash
bun run content:audit
```

보호 노트 전체를 다시 파싱한 뒤 민감 패턴이 하나라도 남으면 exit code 1이다. 새 표현이
발견되면 원본을 수정하지 말고 필터와 회귀 테스트를 함께 갱신한다.

## 접근 제어

- 모든 자격증의 카테고리와 학습 노트는 공개:
  `/api/content/categories/:code`, `/api/content/notes/:code/:slug`
- 모든 자격증의 퀴즈·답안·진도 API는 JWT cookie 또는 Bearer token 필요:
  `/api/content/quiz/:code`, `/api/content/questions/:id/answer`, `/api/progress/*`
- 신규 계정은 `pending`, 관리자가 승인하면 `reader`
- 관리자 API는 `admin` 역할만 접근
- GHCR API 이미지는 private로 유지하고 홈랩에는 image pull secret을 둔다.

## 사고 대응

1. Cloudflare Tunnel public hostname을 비활성화한다.
2. 유출된 이미지 tag와 패키지를 private/삭제 처리한다.
3. 원인이 된 API 또는 정적 산출물을 확인한다.
4. 필터 회귀 테스트를 추가하고 새 이미지로 교체한다.
5. 필요 시 저작권자 요청 절차를 따른다.
