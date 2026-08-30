# minecraft-publicplace-plugin

## 간단한 요약

서버 안의 특정 좌표(청크)에 "이곳은 무슨 용도의 공공 장소다"라는 이름표를 붙여 등록해두는 공용 기반 플러그인입니다. 자체적으로는 눈에 띄는 기능이 없고, 등록·조회 API를 `PublicPlaceApi` 인터페이스로 Bukkit `ServicesManager`에 등록해 다른 플러그인이 가져다 쓰게 하는 것이 핵심입니다.

## 설명

- **장소 등록/조회** (`PublicPlacePlugin`): 이름을 키로 하는 `MutableMap<String, PublicPlace>`에 장소를 보관하고, 데이터 폴더의 `places.yml`에 저장/복원합니다(`loadPlaces`/`savePlaces`). 하나의 `PublicPlace`는 이름, 타입(`PlaceType`), 월드 이름, 그리고 등록 당시 플레이어가 서 있던 청크 좌표(`chunkX`, `chunkZ`)로 구성됩니다 — 즉 영역 판정은 두 좌표를 잇는 직육면체가 아니라 **청크 단위**로 단순화되어 있습니다.
- **타입** (`PlaceType`): `AUCTION_BOARD`(경매장 게시판), `NOTICE_BOARD`(공지 게시판), `SHOP_DISTRICT`(상점가) 세 가지가 정의되어 있습니다.
- **명령어** (`PublicPlaceCommand`): `/publicplace create`로 실행 플레이어의 현재 위치가 속한 청크를 해당 타입의 장소로 등록하고, `remove`로 이름 기준 삭제, `list`로 등록된 전체 목록(이름/타입/월드/청크 좌표)을 확인합니다.
- **다른 플러그인용 API** (`PublicPlaceApi.kt`): `getPlacesByType(type)`, `getAllPlaces()`, `isInside(location, type)` 세 메서드로 구성된 인터페이스입니다. `PublicPlacePlugin`이 이를 구현하고 `onEnable()`에서 `server.servicesManager.register(PublicPlaceApi::class.java, this, this, ServicePriority.Normal)`로 서비스에 등록합니다.
- **물리적 표시물(홀로그램/디스플레이 엔티티 등)은 아직 구현되어 있지 않습니다.** 기획 문서(31번)에서 언급한 확장 아이디어이며, 현재 코드는 "영역 등록 + 타입 조회 API"까지만 제공합니다.

### 의존 관계

`minecraft-auctionhouse-plugin`이 이 플러그인의 `PublicPlaceApi`를 실제로 사용합니다. `AuctionHousePlugin.onEnable()`에서 `server.servicesManager.getRegistration(PublicPlaceApi::class.java)?.provider`로 서비스를 조회해 `publicPlace` 필드에 보관하고, `AuctionCommand`에서 `/ah` 명령 실행 시 `getPlacesByType(PlaceType.AUCTION_BOARD)`로 경매장 게시판이 하나라도 등록되어 있으면 `isInside(player.location, PlaceType.AUCTION_BOARD)`로 플레이어가 그 구역 안에 있는지 검사합니다. auctionhouse-plugin의 `paper-plugin.yml`에도 `PublicPlacePlugin`이 `load: BEFORE`, `required: false`인 서버 의존성으로 선언되어 있어, 이 플러그인이 없어도 auctionhouse-plugin은 동작하지만(경매장 게시판 제한이 걸리지 않음) 있으면 자동으로 연동됩니다.

## 사용 방법 (매뉴얼)

### 명령어

| 명령어 | 설명 |
| --- | --- |
| `/publicplace create <이름> <타입>` | 실행 플레이어가 서 있는 청크를 지정한 이름/타입(`AUCTION_BOARD`, `NOTICE_BOARD`, `SHOP_DISTRICT`)의 공공 장소로 등록합니다. 이미 존재하는 이름이면 실패합니다. |
| `/publicplace remove <이름>` | 지정한 이름의 공공 장소를 제거합니다. |
| `/publicplace list` | 등록된 모든 공공 장소를 이름/타입/월드/청크 좌표와 함께 나열합니다. |

`create`와 `remove`는 플레이어(또는 권한을 가진 실행자)만, `create`는 반드시 플레이어가 실행해야 합니다(현재 위치가 필요하므로 콘솔에서는 사용할 수 없습니다).

### 권한 노드

- `publicplace.admin` (기본값: OP) — `/publicplace create`, `/publicplace remove` 실행에 필요합니다. `PublicPlacePlugin.onEnable()`에서 `Permission("publicplace.admin", PermissionDefault.OP)`로 등록됩니다.
- `/publicplace list`는 별도의 권한 노드 없이 누구나 사용할 수 있습니다.

### config.yml 설정 항목

별도의 `config.yml`은 없습니다. 데이터 폴더에 저장되는 `places.yml`은 등록된 장소 목록(이름/타입/월드/청크 좌표)을 담는 자동 생성 파일이며 직접 수정할 필요는 없습니다.

### 빌드 방법

저장소 루트에서 다음 명령어를 실행합니다.

```bash
./scripts/build-plugin.sh minecraft-publicplace-plugin
```

빌드된 jar(`build/libs/*-all.jar`)가 `data/plugins/`로 복사됩니다. 서버에 반영하려면 `./scripts/console.sh reload confirm`을 실행하거나 서버를 재시작하세요.

auctionhouse-plugin처럼 이 플러그인의 `PublicPlaceApi`를 컴파일 시점에 참조하는 다른 플러그인을 빌드하려면, 먼저 이 플러그인 디렉터리에서 `./gradlew jar`를 실행해 plain jar를 `build/libs/`에 만들어두어야 합니다.
