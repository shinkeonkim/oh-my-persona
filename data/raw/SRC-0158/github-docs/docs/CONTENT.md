# 컨텐츠 워크플로

## 원본

원본은 `content-sources/`의 git submodule 세 개다. 원본 파일은 수정하지 않는다.

| 자격증 | 노트 | 문항 | 공개 범위 |
|---|---|---|---|
| AIF | `public/content/*.md` | `public/data/bank.json` | 공개 |
| CLF | `key-notes/*.md` | `[01-23]-*/*.md` | 승인 계정 |
| SAA | `study-notes/*.md` | `[01-22]-*/*.md` | 승인 계정 |

## 로컬 갱신

```bash
git submodule update --init --recursive
bun run content:audit
bun run content:build
```

`content:build`는 `packages/content/generated/content.json`을 만든다. `DATABASE_URL`이
있으면 같은 데이터를 PostgreSQL에도 upsert한다. 생성 JSON은 저작권 보호 문항을 포함하므로
git에 커밋하지 않는다. CI가 private GHCR API 이미지를 만들 때만 임시로 포함한다.

## 배포 시드

API 이미지에는 CI가 생성한 JSON과 다음 명령이 포함된다.

```bash
bun run packages/db/src/migrate.ts
bun run packages/content/src/cli/seed-generated.ts
bun run apps/api/dist/cli/create-admin.js
```

Helm의 ArgoCD Sync Job이 위 순서로 실행한다. 모든 작업은 upsert 기반이라 동일 이미지로 다시
동기화해도 중복 행이 생기지 않는다.

## 원본 버전 올리기

1. 별도 브랜치에서 해당 submodule 디렉토리로 이동한다.
2. 검토한 원격 커밋으로 checkout한다.
3. 루트에서 `bun run content:audit && bun run content:build`를 실행한다.
4. 생성 건수와 저작권 감사 결과를 PR에 적는다.

예상치 못한 대량 증가·감소는 원본 형식 변경 신호이므로 파서를 먼저 점검한다.
