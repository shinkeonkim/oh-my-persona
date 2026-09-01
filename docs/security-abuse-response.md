# 악성 대화 대응 운영

## 방어 계층

1. 모든 공개 채팅 요청은 Cloudflare의 `CF-Connecting-IP`를 salted SHA-256으로 변환한다.
2. 원 IP는 애플리케이션 DB에 저장하지 않고 대화에는 hash와 12자리 fingerprint만 연결한다.
3. 관리자 `/admin`의 **대화 기록**에서 현재 대화 또는 같은 사용자의 새 대화까지 차단한다.
4. 차단 기간은 24시간, 7일, 영구 중 선택하고 사유와 감사 메모를 남긴다.
5. 차단 요청은 rate limit과 LLM 호출 전에 403으로 종료된다.
6. **이용 제한** 탭에서 활성·만료·해제 기록을 확인하고 해제한다.

공유 IP의 오탐을 줄이기 위해 기본값은 24시간으로 사용한다. 반복적인 악용은 7일,
명확한 자동 공격만 영구 차단한다. 기록은 삭제하지 않고 해제 시각을 남긴다.

## Cloudflare Turnstile

Cloudflare Dashboard의 **Turnstile → Add widget**에서 `persona.shinkeonkim.com` hostname과
**Managed** mode로 widget을 만든 다음 Kubernetes Secret에 다음 값을 추가한다.

```text
PERSONA_TURNSTILE_SITE_KEY=<public site key>
PERSONA_TURNSTILE_SECRET_KEY=<secret key>
```

두 값이 모두 있을 때만 React 채팅과 임베드 widget에서 Turnstile이 활성화된다. 서버는
매 요청마다 Siteverify API를 호출하며, 검증 실패 시 모델을 호출하지 않는다. 한 값만
설정하는 것은 활성화로 취급하지 않는다.

- Dashboard: https://dash.cloudflare.com/?to=/:account/turnstile
- 홈랩 설정 스크립트: `oh-my-homelab/scripts/persona/configure-turnstile-secrets.sh`
- 상세 운영 문서: `oh-my-homelab/docs/manuals/20_persona_Turnstile운영.md`
- 공식 문서: https://developers.cloudflare.com/turnstile/get-started/
- 서버 검증: https://developers.cloudflare.com/turnstile/get-started/server-side-validation/

Free 플랜은 계정당 widget 20개, widget당 hostname 10개와 challenge 요청 무제한을 무료로
제공하므로 현재 서비스 규모에서 별도 비용은 없다. Site Key는 공개 값이지만 Secret Key는
평문으로 Git에 커밋하지 않고 홈랩 SOPS Secret에만 보관한다.

## Cloudflare WAF 긴급 차단

대량 공격은 애플리케이션 관리자 차단보다 Cloudflare Security Events에서 원 IP와 패턴을
확인한 뒤 WAF custom rule 또는 IP Access Rule로 처리한다. 애플리케이션은 개인정보 보호를
위해 원 IP를 보존하지 않으므로 fingerprint에서 IP를 역산할 수 없다.

권장 순서는 다음과 같다.

1. Security Events에서 공격 요청과 원 IP 또는 ASN을 확인한다.
2. 정확한 단일 공격자는 IP rule, 분산 공격은 URI·ASN·Bot score 기반 custom rule을 쓴다.
3. 우선 Managed Challenge를 적용하고 명확한 공격만 Block으로 높인다.
4. 종료 시각과 근거를 운영 기록에 남기고 임시 rule은 만료 후 제거한다.

- WAF custom rules: https://developers.cloudflare.com/waf/custom-rules/
- IP Access Rules: https://developers.cloudflare.com/waf/tools/ip-access-rules/

Cloudflare Tunnel 이외의 경로로 origin을 공개하면 `CF-Connecting-IP`를 클라이언트가 위조할
수 있으므로, 운영 origin은 Tunnel과 클러스터 내부 Service에서만 접근 가능해야 한다.
