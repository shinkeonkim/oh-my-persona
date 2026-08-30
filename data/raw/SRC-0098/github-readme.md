# minecraft-auctionhouse-plugin

## 간단한 요약

어디서든 명령어와 GUI로 아이템을 등록하고 사고팔 수 있는 경매장 플러그인입니다. `/ah`로 목록을 열람/구매하고, `/ah sell <가격>`으로 손에 든 아이템을 등록합니다. 공공 장소 플러그인에 `AUCTION_BOARD` 구역이 등록돼 있으면 그 구역 안에서만 판매 등록을 허용하도록 연동됩니다.

## 설명

- **등록** (`AuctionCommand.handleSell`): 플레이어가 손에 든 아이템을 `price`와 함께 `Listing`으로 만들어 `AuctionHousePlugin.listings`(메모리 맵)에 저장하고, 손에 든 아이템은 인벤토리에서 제거됩니다. 등록된 목록은 `onDisable`뿐 아니라 상태가 바뀔 때마다(`saveData`) 데이터 폴더의 `auctions.yml`에 즉시 직렬화되어 서버 재시작에도 유지됩니다.
- **조회/구매 GUI** (`AuctionGui.kt`, `AuctionGuiListener`): `/ah`를 실행하면 최신 등록순으로 최대 45개까지 보여주는 54칸 인벤토리(`AuctionHolder`)를 엽니다. 목록에 아직 페이지네이션은 없습니다. GUI는 읽기 전용이며, `InventoryClickEvent`를 가로채 클릭한 아이템의 `listing_id`(PersistentDataContainer에 저장된 값)로 즉시 구매를 시도합니다. 자신이 등록한 물품은 구매할 수 없고, 구매자의 잔액이 부족하면 실패합니다.
- **만료/회수**: `runTaskTimer`로 5분(`EXPIRY_CHECK_INTERVAL_TICKS`)마다 등록된 지 24시간(`LISTING_EXPIRY_MILLIS`)이 지난 물품을 찾아 목록에서 제거하고 판매자의 `pendingReturns`로 옮깁니다. 판매자는 접속 여부와 무관하게 `/ah collect`로 회수합니다.
- **economy-plugin 의존(필수)**: `onEnable()`에서 `server.servicesManager.getRegistration(EconomyApi::class.java)`로 `EconomyApi`를 조회합니다. 조회에 실패하면(`EconomyPlugin`이 없으면) 로그를 남기고 `disablePlugin(this)`로 스스로 비활성화됩니다. 구매가 확정되면 `plugin.economy.withdraw(buyer, price)`로 구매자에게서 차감하고, 성공 시 `plugin.economy.deposit(seller, price)`로 판매자에게 지급합니다.
- **publicplace-plugin 의존 (선택)**: `onEnable()`에서 `server.servicesManager.getRegistration(PublicPlaceApi::class.java)?.provider`로 조회하며, 없어도(`null`이어도) 정상 동작합니다. `handleSell`에서 `publicPlace?.getPlacesByType(PlaceType.AUCTION_BOARD)`로 등록된 `AUCTION_BOARD` 구역이 하나라도 있으면, `publicPlace?.isInside(player.location, PlaceType.AUCTION_BOARD)`가 `true`일 때만 등록을 허용합니다. `AUCTION_BOARD` 구역이 아예 없으면(공공 장소 플러그인이 없거나 아직 구역을 안 만들었으면) 제한 없이 어디서든 등록할 수 있습니다.
- `paper-plugin.yml`의 `dependencies.server`에도 `EconomyPlugin`(`required: true`, `load: BEFORE`, `join-classpath: true`)과 `PublicPlacePlugin`(`required: false`, 나머지 동일)이 명시되어 있어, 서버가 두 플러그인을 이 플러그인보다 먼저 로드하고 클래스패스에 연결해줍니다.

## 사용 방법 (매뉴얼)

### 명령어

| 명령어 | 설명 |
| --- | --- |
| `/ah` | 경매장 GUI(최신 등록순 최대 45개)를 엽니다. |
| `/ah sell <가격>` | 손에 든 아이템을 지정한 가격에 경매장에 등록합니다. 가격은 0보다 커야 합니다. `AUCTION_BOARD` 구역이 존재하면 그 구역 안에서만 가능합니다. |
| `/ah collect` | 만료되어 반환 대상이 된 물품을 인벤토리로 회수합니다. 인벤토리가 가득 차면 바닥에 드롭됩니다. |

세 명령어 모두 플레이어만 실행할 수 있습니다.

### 권한 노드

`AuctionCommand`, `AuctionHousePlugin` 어디에도 `permission()` 오버라이드나 `Permission(...)` 등록이 없습니다. 즉 별도의 권한 제한 없이 접속한 모든 플레이어가 `/ah`, `/ah sell`, `/ah collect`를 사용할 수 있습니다.

### config.yml 설정 항목

별도의 `config.yml`은 없습니다. 데이터 폴더의 `auctions.yml`은 등록된 물품(`listings`)과 회수 대기 물품(`returns`)을 저장하는 자동 생성 파일이며 직접 수정할 필요는 없습니다. 만료 기간(24시간)과 만료 확인 주기(5분)는 `AuctionHousePlugin.kt`의 `LISTING_EXPIRY_MILLIS`, `EXPIRY_CHECK_INTERVAL_TICKS` 상수로 코드에 고정되어 있습니다.

### 빌드 방법

이 플러그인은 economy-plugin의 `EconomyApi`를 필수로, publicplace-plugin의 `PublicPlaceApi`를 선택적으로 컴파일 시점에 참조합니다. `build.gradle.kts`가 두 plain jar를 상대 경로로 직접 가리키고 있으므로(`compileOnly(files("../minecraft-economy-plugin/build/libs/economy-plugin-0.1.0.jar"))`, `compileOnly(files("../minecraft-publicplace-plugin/build/libs/publicplace-plugin-0.1.0.jar"))`), 먼저 두 플러그인 디렉터리에서 각각 `./gradlew jar`를 실행해 (shadowJar가 아닌) plain jar를 `build/libs/`에 만들어두어야 합니다.

그 다음 저장소 루트에서 다음 명령어를 실행합니다.

```bash
./scripts/build-plugin.sh minecraft-auctionhouse-plugin
```

빌드된 jar(`build/libs/*-all.jar`)가 `data/plugins/`로 복사됩니다. 서버에 반영하려면 `./scripts/console.sh reload confirm`을 실행하거나 서버를 재시작하세요. 실행 시에는 `EconomyPlugin`이 반드시 함께 설치돼 있어야 하며, `PublicPlacePlugin`은 없어도 동작하되 `AUCTION_BOARD` 구역 연동 기능만 비활성화됩니다.
