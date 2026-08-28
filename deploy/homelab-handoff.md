# oh-my-homelab GitOps handoff

대상 저장소 규칙에 따라 직접 `kubectl apply`하지 않고 다음을 별도 PR로 옮긴다.

1. `deploy/kubernetes/*`를 `helm-charts/persona/`로 옮긴다.
2. `helm-charts/apps/persona.yaml`에서 `https://github.com/shinkeonkim/oh-my-persona.git`의 배포 경로와 homelab의 secret/network-policy 경로를 multi-source로 연결한다.
3. `helm-charts/secrets/persona/`에 DB credentials, `PERSONA_LITELLM_URL`, virtual key를 SOPS+ksops로 암호화한다.
4. CNPG 이미지에 pgvector가 포함됐는지 검증하고, 아니면 homelab의 `docker/postgresql-pgvector` 이미지를 사용한다.
5. Cloudflare Zero Trust에서 `persona.shinkeonkim.com → http://persona.persona.svc.cluster.local:80` Public Hostname을 수동 추가한다.
6. `./scripts/ci/validate-gitops.sh` 통과 후 브랜치/PR로 병합한다.

현재 파일에는 실제 secret 값이 전혀 없다.
