# minecraft-landclaim-plugin

## 간단한 요약

플레이어가 자신이 서 있는 청크(chunk)를 클레임(소유권 등록)해서, 소유자와 신뢰(trust)한 사람 외에는 블록을 부수거나 설치하지 못하고 상자류도 열 수 없도록 보호하는 플러그인입니다.

## 설명

영역은 임의의 사각형이 아니라 **청크 단위**로 단순화되어 있습니다.

- **클레임 데이터** (`LandClaimPlugin`): `claims: MutableMap<String, UUID>`에 `"월드이름:청크X:청크Z"` 문자열을 키로, 소유자 UUID를 값으로 저장합니다. `trusted: MutableMap<UUID, MutableSet<UUID>>`는 청크별이 아니라 **소유자 단위**로 신뢰 목록을 관리합니다 — 즉 한 플레이어를 신뢰하면 그 플레이어가 가진 클레임 전체에 접근할 수 있게 됩니다(청크마다 따로 신뢰를 걸 필요가 없도록 단순화). 데이터는 플러그인 데이터 폴더의 `claims.yml`에 `claims.*`, `trusted.*` 섹션으로 영속 저장됩니다.
- **클레임 개수 제한**: `LandClaimPlugin.kt`의 `MAX_CLAIMS_PER_PLAYER` 상수(10)로 고정되어 있으며, `claimCountOf(uuid)`로 현재 개수를 세어 초과 시 `/claim`이 거부됩니다.
- **보호 로직** (`ClaimProtectionListener`): `BlockBreakEvent`, `BlockPlaceEvent`, `PlayerInteractEvent`(우클릭으로 `InventoryHolder`인 블록, 즉 상자류를 열려는 시도) 세 이벤트를 감시합니다. 각 이벤트에서 대상 블록이 속한 청크 키를 구한 뒤 `canModify(uuid, key)`를 확인해, 클레임되지 않은 청크는 누구나, 클레임된 청크는 소유자 또는 그 소유자가 신뢰한 사람만 허용합니다. 조건을 만족하지 못하면 이벤트를 취소하고 "이 지역은 다른 사람이 보호 중입니다" 메시지를 보냅니다. 세 이벤트 리스너 모두 `event.player.isOp`인 경우 검사를 건너뛰어 운영자는 항상 통과합니다.
- 이 플러그인은 다른 플러그인에 대한 의존성이 없습니다 (`build.gradle.kts`에는 `paper-api`만 `compileOnly`로 선언되어 있음).

## 사용 방법 (매뉴얼)

### 명령어

| 명령어 | 설명 |
| --- | --- |
| `/claim` | 현재 서 있는 청크를 자신의 소유로 등록합니다. 이미 클레임된 청크거나, 본인이 이미 `MAX_CLAIMS_PER_PLAYER`(10)개를 클레임했다면 실패합니다. |
| `/trust <닉네임>` | 지정한 플레이어를 신뢰 목록에 추가합니다. 신뢰받은 플레이어는 신뢰를 건 사람의 클레임 전체(현재+이후 클레임 포함)에서 블록 설치/파괴, 상자 열기가 허용됩니다. |
| `/unclaim` | 현재 서 있는 청크의 클레임을 해제합니다. 본인 소유의 클레임만 해제할 수 있습니다. |

세 명령어 모두 플레이어만 실행할 수 있습니다(콘솔 실행 불가).

### 권한 노드

소스 코드 어디에도 `Permission(...)` 등록이나 명령어별 `permission()` 오버라이드가 없습니다. 즉 별도의 권한 노드는 존재하지 않으며, 모든 플레이어가 `/claim`, `/trust`, `/unclaim`을 사용할 수 있습니다. 다만 보호 검사(`ClaimProtectionListener`) 자체는 `event.player.isOp`(서버 OP 여부)를 확인해, OP 권한을 가진 플레이어는 클레임 보호를 무시하고 어디서나 블록을 설치/파괴하고 상자를 열 수 있습니다.

### config.yml 설정 항목

`config.yml`은 없습니다. 클레임 개수 제한(`MAX_CLAIMS_PER_PLAYER = 10`)은 설정 파일이 아니라 코드에 상수로 고정되어 있어, 변경하려면 소스를 수정하고 다시 빌드해야 합니다. 데이터 폴더의 `claims.yml`은 자동 생성/저장되는 파일로 직접 수정할 필요는 없습니다.

### 빌드 방법

저장소 루트에서 다음 명령어를 실행합니다.

```bash
./scripts/build-plugin.sh minecraft-landclaim-plugin
```

빌드된 jar(`build/libs/*-all.jar`)가 `data/plugins/`로 복사됩니다. 서버에 반영하려면 `./scripts/console.sh reload confirm`을 실행하거나 서버를 재시작하세요.
