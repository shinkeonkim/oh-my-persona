# Minecraft Vanish Plugin

### 1. 간단한 요약

`/vanish` 명령어로 잠수 모드를 켜고 끄는 Paper 플러그인입니다. 잠수 모드 중에는 다른 플레이어들에게 보이지 않으며, 접속/퇴장 시에도 자연스럽게 숨김 처리가 유지됩니다.

### 2. 설명

- **잠수 모드 토글**: `/vanish` 명령어를 실행하면 `VanishPlugin.toggleVanish`가 호출되어 잠수 상태를 켜거나 끕니다. 플러그인 내부적으로 잠수 중인 플레이어의 UUID를 `vanished: MutableSet<UUID>`에 담아 관리합니다.
  - 잠수 모드를 켤 때: 현재 접속 중인 자신을 제외한 모든 플레이어에게 `Player#hidePlayer(plugin, player)`를 호출해 자신을 숨기고, "잠수 모드를 시작했습니다. 다른 플레이어에게 보이지 않습니다." 메시지를 본인에게 보냅니다.
  - 잠수 모드를 끌 때: 모든 온라인 플레이어에게 `Player#showPlayer(plugin, player)`를 호출해 다시 보이게 하고, "잠수 모드를 해제했습니다." 메시지를 본인에게 보냅니다.
- **새로 접속한 플레이어에게도 숨김 유지**: `VanishJoinQuitListener`가 `PlayerJoinEvent`를 처리하여, 새로 접속한 플레이어의 화면에 현재 잠수 중인 모든 플레이어가 보이지 않도록 즉시 `hidePlayer`를 적용합니다. 이 처리 덕분에 잠수 중인 플레이어는 이후 접속하는 사람에게도 계속 숨겨집니다.
- **퇴장 메시지 숨김**: `VanishJoinQuitListener`가 `PlayerQuitEvent`를 처리하여, 퇴장하는 플레이어가 잠수 중이었다면 잠수 목록에서 제거함과 동시에 `event.quitMessage(null)`로 퇴장 메시지 자체를 숨깁니다. (접속 메시지 숨김이나 인벤토리/아이템 상호작용 제한, 블록 상호작용 제한 등은 현재 구현되어 있지 않습니다.)
- **서버 종료 시 상태 초기화**: `onDisable`에서 `vanished` 목록을 비워, 다음 서버 기동 시 잔여 상태 없이 시작합니다.
- 다른 플러그인에 대한 의존관계는 없습니다 (Paper API만 사용).

### 3. 사용 방법 (매뉴얼)

**명령어**

| 명령어 | 설명 | 권한 노드 |
| --- | --- | --- |
| `/vanish` | 잠수 모드를 켜거나 끕니다 (토글). 인자는 받지 않습니다. | `vanish.use` |

- `/vanish`는 플레이어만 사용할 수 있으며, 콘솔 등 플레이어가 아닌 발신자가 실행하면 "플레이어만 사용할 수 있습니다." 메시지가 표시되고 아무 동작도 하지 않습니다.

**권한 노드**

- `vanish.use` — `/vanish` 명령어 실행 권한. 기본값은 `OP`이며 (`PermissionDefault.OP`), 플러그인이 활성화될 때 `server.pluginManager.addPermission(...)`으로 등록됩니다.

**설정 파일**

- 별도의 `config.yml`은 존재하지 않습니다. 현재는 설정 가능한 항목이 없습니다.

**빌드 방법**

저장소 루트에서 다음 명령어를 실행합니다.

```bash
./scripts/build-plugin.sh minecraft-vanish-plugin
```
