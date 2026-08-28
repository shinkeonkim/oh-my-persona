# T11 — 2만~5만 corpus와 운영 전환

상태: DONE (2만 청크 품질 게이트 완료, 5만은 품질 기반 선택 확장)
선행: T09, T10

## 2026-08-29 실행 기록

- `my-resume` 77개, `my-portfolio` 130개 공개 텍스트 문서를 commit SHA와 blob URL로 snapshot
- GitHub profile/Gists, 개인 사이트, Tistory, SIPE, twin-ai 7개 페이지를 robots.txt 확인 후 저속 수집
- 총 source 10, snapshot document 214, 중복 제거 청크 654
- exact duplicate 0, 민감정보 패턴 0, source 역추적 가능 청크 634/654(96.94%)
- 나머지 20개는 이 프로젝트가 작성한 운영/설계 문서이므로 외부 source URL이 없는 것이 정상
- temporal/activity/privacy 평가 통과
- `oh-my-homelab`의 별도 `feat/persona-service` worktree에 Application, CNPG, Deployment,
  Service, PDB, NetworkPolicy, SOPS 예시를 작성하고 GitOps 전체 검증 통과
- 공개 저장소 `https://github.com/shinkeonkim/oh-my-persona` 생성·초기 push 및 CI 통과
- 공개 멀티아키텍처 이미지 `ghcr.io/shinkeonkim/oh-my-persona:main` 발행
- `oh-my-homelab` draft PR #78 생성 및 GitOps CI 통과
- `my-cv`, `oh-my-interview-helper`, GitHub profile repository, legacy GitHub Pages blog를
  추가하고 6개 저장소의 전체 커밋 이력을 날짜·영구 commit URL과 함께 snapshot
- source 14, snapshot document 2,715, 중복 제거 청크 5,773으로 첫 5천 목표 통과
- exact duplicate 0, 민감정보 패턴 0, source 역추적 가능 청크 5,752/5,773(99.64%)
- `data/processed/chunks.jsonl`을 재현 가능한 검색 산출물로 이미지에 포함해 운영 챗봇이
  전체 코퍼스를 실제로 검색하도록 수정
- 동일인임을 확인한 공개 저장소 44개를 추가하고 파일 snapshot과 날짜가 명확한 Git commit
  이력을 영구 URL로 수집
- source 59, snapshot document 13,715, 중복 제거 청크 21,211로 2만 목표 통과
- exact duplicate 0, 민감정보 패턴 0, source 역추적 가능 청크 21,183/21,211(99.87%)
- 시간·활동·개인정보를 포함한 검색 평가 6개 전부 통과

## 선택 입력과 후속 확장

1. 사용자가 제공할 PDF/Markdown ZIP의 공개·검색 허용 범위
2. 50,000개 선택 확장을 위한 추가 공개 저장소·발표·기고 범위
3. 블로그별 robots/약관 검토 후 게시물 단위 crawl 실행

## 배치 반복

```bash
persona inspect-inbox
persona ingest-inbox --approve
persona chunk
persona validate
persona inventory
persona evaluate
```

매 500 청크마다 exact/near duplicate, identity precision, citation traceability, PII 표본 검사를 수행한다. 20,000은 운영 목표이고 50,000은 검색 품질이 유지될 때만 확장한다.
