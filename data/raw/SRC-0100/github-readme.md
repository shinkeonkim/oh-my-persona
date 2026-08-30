# minecraft-back-plugin

## 간단한 요약

`/back` 명령어 하나로 죽은 위치나 직전 텔레포트 위치로 돌아갈 수 있게 해주는 작은 편의 플러그인입니다. 플레이어별로 가장 최근 위치 하나만 메모리에 기억합니다.

## 설명

이 플러그인은 플레이어 UUID를 키로 하는 `MutableMap<UUID, Location>` (`BackPlugin.lastLocation`) 하나로 동작하며, 이 맵은 두 리스너에 의해 갱신됩니다.

- **`DeathTrackingListener`**: `PlayerDeathEvent`가 발생하면 죽은 플레이어의 현재 위치(`event.player.location`)를 기록합니다. 사망은 텔레포트가 아니므로 아래 리스너로는 잡히지 않아 별도로 처리합니다.
- **`TeleportTrackingListener`**: `PlayerTeleportEvent`가 발생하면 텔레포트 "직전" 위치(`event.from`)를 기록합니다. 이 이벤트는 어떤 이유로 텔레포트가 일어났는지(홈, 워프, TPA, `/back` 자신 포함)를 가리지 않고 전부 관찰하므로, 새로운 텔레포트 관련 플러그인이 추가되어도 이 플러그인은 수정할 필요가 없습니다.

두 리스너 모두 같은 맵에 위치를 덮어쓰기 때문에, 플레이어당 최근 위치 1개만 유지되며(스택처럼 여러 개 쌓지 않음) 시간상 더 나중에 발생한 이벤트(사망 또는 텔레포트)의 위치가 남습니다.

`/back` 명령어(`BackCommand`)를 실행하면 이 맵에서 자신의 UUID에 해당하는 위치를 찾아 `player.teleportAsync(location)`으로 그 자리에 순간이동합니다. 기록된 위치가 없으면 "돌아갈 위치가 없습니다." 메시지만 보냅니다.

기획 문서(`docs/plugin-ideas/03-back-command.md`)에 언급된 대로, 이 정보는 서버가 재시작되면 초기화되어도 무방한 수준의 편의 기능이라고 보고 있어 파일이나 DB에 영속 저장하지 않고 메모리(`onDisable()`에서 `lastLocation.clear()`)에만 보관합니다.

다른 플러그인에 대한 의존성은 없습니다. 이벤트를 관찰하는 방식으로 동작하므로 홈/워프나 TPA 플러그인이 이 플러그인의 API를 직접 호출할 필요가 없고, 서버가 기본 제공하는 Paper API(컴파일 시점에만 필요, `compileOnly`)만 사용합니다.

## 사용 방법 (매뉴얼)

### 명령어

| 명령어 | 설명 |
| --- | --- |
| `/back` | 기록된 마지막 위치(죽은 위치 또는 직전 텔레포트 위치 중 더 최근 것)로 돌아갑니다. 콘솔 등 플레이어가 아닌 발신자가 실행하면 "플레이어만 사용할 수 있습니다." 메시지만 표시됩니다. 기록된 위치가 없으면 "돌아갈 위치가 없습니다." 메시지를 표시합니다. |

`BackCommand`는 `BasicCommand`를 구현하며 `BackPlugin.onEnable()`에서 `registerCommand("back", BackCommand(this))`로 등록됩니다. 인자는 받지 않습니다.

### 권한 노드

소스 코드(`BackPlugin`, `BackCommand`, `paper-plugin.yml`) 어디에도 별도의 권한(permission) 등록이 없습니다. 즉 `/back` 명령어에는 권한 제한이 걸려 있지 않으며, 서버에 접속한 모든 플레이어가 사용할 수 있습니다.

### config.yml 설정 항목

이 플러그인에는 `config.yml`이 없습니다. 별도의 설정 항목도 없습니다.

### 빌드 방법

저장소 루트에서 다음 명령어를 실행합니다.

```bash
./scripts/build-plugin.sh minecraft-back-plugin
```

빌드된 jar(`build/libs/*-all.jar`)가 `data/plugins/`로 복사됩니다. 서버에 반영하려면 `./scripts/console.sh reload confirm`을 실행하거나 서버를 재시작하세요.
