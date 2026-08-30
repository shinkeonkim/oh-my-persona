# minecraft-storage-plugin

## 요약
`/storage` 명령어로 언제 어디서든 열 수 있는, 플레이어별 다중 페이지 개인 보관창고를 제공하는 Paper 플러그인입니다. 27칸인 엔더상자의 한계를 보완하기 위해 페이지당 54칸(더블 상자 크기)인 인벤토리를 최대 3페이지까지 제공하며, 내용물은 서버 재시작 후에도 유지됩니다.

## 설명
- **명령어**: `StorageCommand`(`io.papermc.paper.command.brigadier.BasicCommand` 구현)가 `/storage [페이지]` 실행을 처리합니다. 인자로 받은 페이지 번호(기본값 1)에 해당하는 인벤토리를 열어줍니다.
- **인벤토리 관리**: `StoragePlugin.getOrLoadPage(uuid, page)`가 플레이어 UUID와 페이지 번호로 인벤토리를 조회하며, 메모리에 없으면 디스크에서 불러오고(`loadedPages` 맵에 `"uuid:page"` 키로 캐싱), 없으면 새 인벤토리를 생성합니다. 각 인벤토리는 `StorageHolder(ownerUuid, page)`를 `InventoryHolder`로 사용해 어떤 플레이어·페이지의 보관창고인지 식별합니다.
- **저장(영속화)**: `StoragePlugin.savePage(uuid, page, inventory)`가 인벤토리의 각 슬롯을 `YamlConfiguration`에 `ItemStack`으로 직렬화하여 `plugins/StoragePlugin/storage/<uuid>-<page>.yml` 파일에 저장합니다.
- **저장 시점**:
  - `StorageCloseListener`가 `InventoryCloseEvent`를 감지해, 닫힌 인벤토리의 holder가 `StorageHolder`이면 즉시 해당 페이지를 저장합니다.
  - `QuitSaveListener`가 `PlayerQuitEvent`를 감지해, 나간 플레이어가 열어봤던 모든 페이지를 저장하고 `loadedPages` 캐시에서 제거합니다.
  - `StoragePlugin.onDisable()`에서도 남아 있는 모든 페이지를 저장한 뒤 캐시를 비웁니다.
- **페이지 구성**: 페이지 크기는 54칸(`PAGE_SIZE`), 플레이어당 페이지 수는 3페이지(`PAGE_COUNT`)로 상수로 고정되어 있습니다. 페이지별 권한 등급 제한 기능은 구현되어 있지 않습니다.
- **외부 플러그인 의존성**: 없습니다. Paper API만 사용합니다.

## 사용 방법

### 명령어
| 명령어 | 설명 |
| --- | --- |
| `/storage` | 1페이지 보관창고를 엽니다. |
| `/storage <페이지>` | 지정한 페이지(1~3)의 보관창고를 엽니다. 범위를 벗어나면 오류 메시지가 출력됩니다. |

플레이어(콘솔이 아닌 실제 플레이어)만 사용할 수 있습니다.

### 권한
소스 코드와 `paper-plugin.yml`에 별도로 등록된 권한 노드가 없습니다. 즉, `/storage` 명령어는 별도의 권한 체크 없이 모든 플레이어가 사용할 수 있습니다.

### 설정 파일
`config.yml`은 존재하지 않으며, 별도의 설정 항목도 없습니다. 페이지 크기(54칸)와 페이지 수(3)는 `StoragePlugin.kt`의 상수(`PAGE_SIZE`, `PAGE_COUNT`)로 코드에 고정되어 있습니다.

### 빌드 방법
저장소 루트에서 다음 명령어를 실행합니다.

```bash
./scripts/build-plugin.sh minecraft-storage-plugin
```

빌드된 jar는 `data/plugins/`에 복사되며, 서버에 반영하려면 `./scripts/console.sh reload confirm`을 실행하거나 서버를 재시작하세요.
