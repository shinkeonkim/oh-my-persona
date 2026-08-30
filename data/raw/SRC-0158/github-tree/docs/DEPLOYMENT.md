# 홈랩 배포 실행서

이 문서는 **사용자가 수행할 마지막 조작**만 남긴 상태의 체크리스트다. 클러스터에 직접
`kubectl apply`하지 않는다. 모든 변경은 `oh-my-homelab` PR과 ArgoCD를 통한다.

## 1. GitHub 준비

1. 이 저장소 Settings → Actions secrets에 `CONTENT_REPO_TOKEN`을 추가한다.
   - `kokoa-study-room/aws-saa-sutdy-notes`, `clf-c02-study-notes` read 권한 필요
2. branch protection을 켠다: main PR 필수, 1 review, `quality` check 필수.
3. 변경을 브랜치에 커밋하고 PR로 merge한다.
4. `Build images` workflow 완료 후 두 GHCR image의 `sha-xxxxxxx` tag와 `sha256:` digest를 기록한다.
5. GHCR package는 private로 유지한다.

## 2. 홈랩 파일 준비

다음 파일을 `oh-my-homelab`의 대응 경로로 복사한다.

| 이 저장소 | oh-my-homelab 목적지 |
|---|---|
| `deploy/homelab/aws-study-site-application.yaml` | `helm-charts/apps/aws-study-site.yaml` |
| `deploy/homelab/aws-study-site-values.yaml` | `helm-charts/values/aws-study-site.yaml` |
| `deploy/homelab/kustomization.yaml` | `helm-charts/secrets/aws-study-site/kustomization.yaml` |
| `deploy/homelab/ksops-generator.yaml` | `helm-charts/secrets/aws-study-site/ksops-generator.yaml` |

values의 web/api tag와 digest를 1-4에서 기록한 SHA tag 및 digest로 교체한다. 실제 Pod는
digest를 사용하며 tag는 사람이 릴리스를 식별하는 메타데이터로 남긴다.

## 3. 시크릿

1. `secret.plaintext.example.yaml`을 작업 디렉토리에 복사하고 실제 값을 채운다.
2. JWT는 `openssl rand -base64 48`처럼 32자 이상으로 만든다.
3. SOPS로 암호화해 `helm-charts/secrets/aws-study-site/secret.enc.yaml`에 둔다.
4. 평문 파일은 즉시 삭제하고 git diff에 값이 없는지 확인한다.
5. `ghcr-pull-secret`은 홈랩 가이드 방식으로 별도 SOPS Secret에 추가한다.

## 4. 검증과 PR

```bash
./scripts/ci/validate-gitops.sh
git checkout -b feat/aws-study-site
git add helm-charts/apps/aws-study-site.yaml \
  helm-charts/values/aws-study-site.yaml \
  helm-charts/secrets/aws-study-site
git commit -m "feat(aws-study-site): add study platform"
git push -u origin feat/aws-study-site
gh pr create --fill
```

사람이 PR을 merge하면 ArgoCD가 namespace, CNPG, migration Job, web/api, IngressRoute를 만든다.

## 5. Cloudflare 수동 단계

Zero Trust → Networks → Tunnels → Public Hostnames에 다음을 추가한다.

- Hostname: `aws-study.shinkeonkim.com`
- Service: 홈랩 Traefik HTTPS endpoint
- TLS: 홈랩의 기존 origin 설정과 동일

ArgoCD가 Healthy가 되기 전에는 public hostname을 활성화하지 않는다.

## 6. 배포 확인

읽기 명령만 사용한다.

```bash
kubectl -n argocd get application aws-study-site
kubectl -n aws-study-site get pods,jobs
kubectl -n aws-study-site logs job/aws-study-site-migrate-1
curl -fsS https://aws-study.shinkeonkim.com/healthz
```

마지막으로 공개 AIF, 보호된 SAA/CLF, 로그인, 관리자 승인, 진도 저장을 브라우저에서 확인한다.
