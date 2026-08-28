# T11 — 5천~1만 corpus와 운영 전환

상태: DOING (첫 500청크 품질 게이트 완료, 추가 자료 대기)
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

## 차단 입력

1. 사용자가 제공할 PDF/Markdown ZIP의 공개·검색 허용 범위
2. 5,000개 이상 확장을 위한 GitHub API token 또는 추가 공개 저장소 범위
3. 블로그별 robots/약관 검토 후 실제 crawl 실행
4. 준비된 `feat/persona-service` 브랜치의 리뷰/PR과 실제 SOPS secret
5. LiteLLM virtual key, DB secret, Cloudflare Public Hostname 생성

## 배치 반복

```bash
persona inspect-inbox
persona ingest-inbox --approve
persona chunk
persona validate
persona inventory
persona evaluate
```

매 500 청크마다 exact/near duplicate, identity precision, citation traceability, PII 표본 검사를 수행한다. 5,000은 첫 품질 게이트이고 10,000은 품질을 유지할 때만 확장한다.
