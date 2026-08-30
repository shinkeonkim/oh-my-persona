# minecraft-economy-plugin

## 간단한 요약

서버 전체가 공유하는 잔액(재화) 시스템입니다. `/balance`, `/pay`, 그리고 운영자용 `/eco` 명령어를 제공하며, 다른 플러그인(체스트샵, 경매장, 직업 시스템 등)이 잔액을 조회하고 조작할 수 있도록 `EconomyApi` 인터페이스를 Bukkit `ServicesManager`에 등록해 노출합니다.

## 설명

이 플러그인은 UUID 기준으로 플레이어 잔액을 관리하는 가장 기초적인 경제 시스템입니다.

- **잔액 관리** (`EconomyPlugin`): 잔액은 `MutableMap<UUID, Double>`로 메모리에 들고 있다가, 변경이 생길 때마다 데이터 폴더의 `balances.yml`에 UUID를 키로 하여 저장합니다(`loadBalances`/`saveBalances`). 조회 시 계좌가 없으면 `STARTING_BALANCE`(100.0)를 기본값으로 반환합니다.
- **시작 잔액 지급** (`StartingBalanceListener`): 플레이어가 처음 접속(`PlayerJoinEvent`)하면 `ensureAccount(uuid)`를 호출해, 계좌가 없을 때만 100.0을 지급하고 저장합니다. 이미 계좌가 있으면 아무 일도 하지 않습니다.
- **명령어** (`commands/` 패키지): `BalanceCommand`(잔액 조회), `PayCommand`(송금), `EcoAdminCommand`(운영자 잔액 조정) 세 개가 있으며, 모두 `EconomyPlugin`의 `EconomyApi` 구현 메서드(`getBalance`/`deposit`/`withdraw`/`setBalance`)를 통해 동작합니다.
- **다른 플러그인용 API** (`EconomyApi.kt`): `getBalance`, `has`, `deposit`, `withdraw`, `setBalance` 다섯 개 메서드로 이루어진 인터페이스입니다. `EconomyPlugin`이 이 인터페이스를 구현하고, `onEnable()`에서 `server.servicesManager.register(EconomyApi::class.java, this, this, ServicePriority.Normal)`로 서비스로 등록합니다. 체스트샵, 경매장, 직업 시스템 등 다른 플러그인은 `EconomyPlugin` 클래스를 몰라도 `Bukkit.getServicesManager().load(EconomyApi::class.java)`(또는 `getRegistration`)로 이 인터페이스만 가져다 쓰면 됩니다. `withdraw`는 잔액이 부족하면 아무 것도 하지 않고 `false`를 반환하므로, 호출하는 쪽에서 반드시 반환값을 확인해야 합니다.

다른 플러그인에 대한 의존성은 없습니다. 이 플러그인은 오히려 다른 여러 플러그인이 의존하는 기반(base) 플러그인입니다.

## 사용 방법 (매뉴얼)

### 명령어

| 명령어 | 설명 |
| --- | --- |
| `/balance` | 실행한 플레이어 본인의 잔액을 조회합니다. |
| `/balance <닉네임>` | 지정한 플레이어(오프라인 포함)의 잔액을 조회합니다. |
| `/pay <닉네임> <금액>` | 현재 접속 중인 플레이어에게 송금합니다. 자기 자신에게는 보낼 수 없고, 금액은 0보다 커야 하며, 잔액이 부족하면 실패합니다. |
| `/eco <give\|take\|set> <닉네임> <금액>` | 운영자 전용. 지정한 플레이어의 잔액을 지급(`give`)/차감(`take`)/고정(`set`)합니다. 금액은 0 이상의 숫자여야 합니다. |

`/balance`는 콘솔에서 실행할 경우 반드시 닉네임 인자를 함께 지정해야 합니다. `/pay`는 플레이어만 실행할 수 있습니다.

### 권한 노드

- `economy.admin` (기본값: OP) — `/eco` 명령어 실행에 필요합니다. `EconomyPlugin.onEnable()`에서 `Permission("economy.admin", PermissionDefault.OP)`로 등록됩니다.
- `/balance`, `/pay`는 별도의 권한 노드가 없어 모든 플레이어가 사용할 수 있습니다.

### config.yml 설정 항목

별도의 `config.yml`은 없습니다. 데이터 폴더에 저장되는 `balances.yml`은 UUID를 키로, 잔액(Double)을 값으로 갖는 자동 생성 파일이며 직접 수정할 필요는 없습니다. 시작 잔액은 `EconomyPlugin.kt`의 `STARTING_BALANCE` 상수(100.0)로 코드에 고정되어 있습니다.

### 빌드 방법

저장소 루트에서 다음 명령어를 실행합니다.

```bash
./scripts/build-plugin.sh minecraft-economy-plugin
```

빌드된 jar(`build/libs/*-all.jar`)가 `data/plugins/`로 복사됩니다. 서버에 반영하려면 `./scripts/console.sh reload confirm`을 실행하거나 서버를 재시작하세요.

체스트샵, 경매장, 직업 시스템처럼 이 플러그인의 `EconomyApi`를 컴파일 시점에 참조하는 다른 플러그인을 빌드하려면, 먼저 이 플러그인 디렉터리에서 `./gradlew jar`를 실행해 (shadow가 아닌) plain jar를 `build/libs/`에 만들어두어야 합니다. 의존하는 플러그인들의 `build.gradle.kts`가 `compileOnly(files("../minecraft-economy-plugin/build/libs/..."))` 형태로 이 plain jar를 직접 참조하기 때문입니다.
