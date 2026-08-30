# minecraft-backpack-plugin

## 요약

플레이어에게 개인 전용 휴대용 인벤토리("배낭")를 제공하는 Paper 플러그인입니다. 지급받은 배낭 아이템을 우클릭하거나 `/backpack` 명령어를 실행하면 27칸짜리 개인 GUI가 열리고, 그 안의 내용물은 서버를 재시작하거나 재접속해도 그대로 유지됩니다.

## 설명

- **배낭 아이템** (`BackpackItems.kt`): 이름이 "배낭"인 상자(`Material.CHEST`) 아이템입니다. 문자열 이름이 아니라 `ItemMeta`의 `PersistentDataContainer`에 `backpack_item`이라는 `NamespacedKey` 태그(`PersistentDataType.BYTE`)를 심어서 식별하므로, 이름만 같은 일반 상자와 구분됩니다.
- **배낭 GUI 열기** (`BackpackItemListener`): `PlayerInteractEvent`를 감지해 우클릭(`RIGHT_CLICK_AIR`/`RIGHT_CLICK_BLOCK`)한 아이템이 배낭 아이템이면 이벤트를 취소하고, 해당 플레이어의 배낭 인벤토리를 열어줍니다.
- **배낭 인벤토리 관리** (`BackpackPlugin`, `BackpackHolder`): 배낭은 크기 27(`BACKPACK_SIZE`)의 `Inventory`이며, `BackpackHolder`(플레이어 UUID를 들고 있는 `InventoryHolder`)를 통해 "이 인벤토리는 배낭이다"라는 것을 식별합니다. `BackpackPlugin.loadedBackpacks`라는 `UUID -> Inventory` 맵으로 현재 메모리에 올라온 배낭들을 관리하며, `getOrLoadBackpack()`이 없으면 디스크에서 불러오고 있으면 그대로 재사용합니다.
- **영속 저장** (`BackpackPlugin.saveBackpack` / `loadBackpackFromDisk`): 배낭 내용물은 `plugins/BackpackPlugin/backpacks/<UUID>.yml` 파일에 슬롯 번호(`items.<슬롯번호>`)를 키로 하여 `ItemStack`을 그대로 YAML로 직렬화해 저장합니다. 저장 시점은 세 가지입니다.
  - 배낭 GUI를 닫을 때 (`BackpackGuiListener.onClose`, `InventoryCloseEvent`)
  - 플레이어가 서버에서 나갈 때 (`QuitSaveListener.onQuit`, `PlayerQuitEvent`) — 저장 후 메모리(`loadedBackpacks`)에서도 제거해, 서버를 오래 켜둬도 배낭이 무한정 쌓이지 않게 합니다.
  - 서버/플러그인이 비활성화될 때 (`BackpackPlugin.onDisable`) — 그 시점에 메모리에 남아있는 모든 배낭을 일괄 저장합니다.
- **악용 방지** (`BackpackGuiListener.onClick`, `InventoryClickEvent`): 배낭 GUI(최상단 인벤토리의 holder가 `BackpackHolder`인 경우)에서 클릭이 일어날 때, 시프트클릭이면 클릭된 아이템(`currentItem`)을, 아니면 커서에 들고 있는 아이템(`cursor`)을 확인해서 그것이 배낭 아이템이면 클릭 자체를 취소하고 안내 메시지를 보냅니다. 즉 배낭 안에 배낭을 넣는 행위를 막습니다.
- 다른 플러그인에 대한 의존성은 없습니다. 서버가 기본 제공하는 Paper API(컴파일 시점에만 필요, `compileOnly`)만 사용합니다.

## 사용 방법

### 명령어

명령어는 `paper-plugin.yml`의 `commands:` 섹션이 아니라, `BackpackPlugin.onEnable()`에서 `registerCommand("backpack", BackpackCommand(this))`로 코드에서 직접 등록됩니다(`BasicCommand` 구현).

| 명령어 | 설명 |
| --- | --- |
| `/backpack` | 실행한 플레이어 본인의 배낭 GUI를 엽니다. 콘솔 등 플레이어가 아닌 발신자가 실행하면 "플레이어만 사용할 수 있습니다." 메시지를 받습니다. |
| `/backpack give <닉네임>` | 지정한 닉네임의 온라인 플레이어(`Bukkit.getPlayerExact`)에게 배낭 아이템을 한 개 지급합니다. `backpack.give` 권한이 필요합니다. 대상 플레이어가 접속해 있지 않거나 인자를 생략하면 "사용법: /backpack give <닉네임>" 안내를 받습니다. |

### 권한 노드

| 권한 | 기본값 | 설명 |
| --- | --- | --- |
| `backpack.give` | OP (`PermissionDefault.OP`) | `/backpack give <닉네임>` 명령어로 다른 플레이어에게 배낭 아이템을 지급할 수 있는 권한입니다. `BackpackPlugin.onEnable()`에서 `server.pluginManager.addPermission(Permission("backpack.give", PermissionDefault.OP))`으로 등록됩니다. |

`/backpack`(본인 배낭 열기)에는 별도의 권한 제한이 없어 모든 플레이어가 사용할 수 있습니다.

### config.yml 설정 항목

이 플러그인에는 `config.yml`이 없습니다. 배낭 크기는 설정 파일이 아니라 코드 상수 `BACKPACK_SIZE = 27`(`BackpackPlugin.kt`)로 고정되어 있으며, 등급별(작은/중간/큰) 배낭 크기 구분은 구현되어 있지 않습니다.

### 빌드 방법

저장소 루트에서 다음 명령어를 실행합니다.

```bash
./scripts/build-plugin.sh minecraft-backpack-plugin
```

빌드된 jar(`build/libs/*-all.jar`)가 `data/plugins/`로 복사됩니다. 서버에 반영하려면 `./scripts/console.sh reload confirm`을 실행하거나 서버를 재시작하세요.
