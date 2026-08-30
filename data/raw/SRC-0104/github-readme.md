# minecraft-chestshop-plugin

## 간단한 요약

상자에 표지판을 붙여 개인 상점을 만드는 플러그인입니다. 표지판에 `[shop]`이라고 쓰면 상점이 등록되고, 다른 플레이어가 그 표지판을 우클릭하면 아이템을 사고팔 수 있습니다. 잔액 처리는 `minecraft-economy-plugin`의 `EconomyApi`를 그대로 가져다 씁니다.

## 설명

이 플러그인은 명령어 없이 표지판·상자 상호작용만으로 동작합니다.

- **상점 생성** (`ShopCreateListener`, `SignChangeEvent`): 플레이어가 표지판(벽에 붙는 `WallSign`이어야 함)의 1번째 줄에 `[shop]`을 쓰면 상점 등록이 시작됩니다. 표지판 뒤에 상자(`InventoryHolder`)가 없으면 거부하고, 손에 판매할 아이템을 들고 있지 않아도 거부합니다. 2번째 줄은 수량(비어 있으면 1, 최소 1), 3번째 줄은 0보다 큰 가격이어야 하며, 4번째 줄은 손에 든 아이템의 `Material` 이름으로 플러그인이 자동으로 채웁니다. 표지판 텍스트 적용은 이벤트 처리가 끝난 다음 틱에 이루어지므로, 소유자 UUID·아이템·수량·가격은 표지판의 `PersistentDataContainer`(PDC)에 다음 틱에 저장됩니다(`ownerKey`, `itemKey`, `quantityKey`, `priceKey`).
- **거래** (`ShopTradeListener`, `PlayerInteractEvent`): 등록된 상점 표지판을 우클릭하면 PDC에서 소유자·아이템·수량·가격을 읽어와 거래를 처리합니다. 일반 우클릭은 **구매**(상자 → 플레이어), 웅크린(sneaking) 채 우클릭은 **판매**(플레이어 → 상자)입니다.
  - 구매: 상자 재고가 충분한지 확인 → 구매자 잔액에서 가격만큼 `withdraw` → 상자에서 아이템 차감, 플레이어 인벤토리에 지급(넘치면 바닥에 드롭) → 상점 주인에게 `deposit`.
  - 판매: 플레이어가 팔 아이템을 충분히 갖고 있는지 확인 → 상자에 아이템 추가(공간 부족하면 취소) → 플레이어 인벤토리에서 아이템 제거 → 상점 주인 잔액에서 `withdraw`(주인 잔액 부족 시 아이템·인벤토리 변경을 롤백하고 거래 취소) → 판매자에게 `deposit`.
- **경제 플러그인 의존성**: `ChestShopPlugin.onEnable()`에서 `server.servicesManager.getRegistration(EconomyApi::class.java)`로 `minecraft-economy-plugin`이 등록해둔 `EconomyApi` 서비스를 조회합니다. 등록된 서비스가 없으면 경고 로그를 남기고 스스로를 비활성화합니다(`disablePlugin`). `paper-plugin.yml`의 `dependencies.server.EconomyPlugin`(`load: BEFORE`, `required: true`, `join-classpath: true`)로 economy-plugin이 먼저 로드되고 클래스패스를 공유하도록 선언되어 있고, `build.gradle.kts`에서는 `compileOnly(files("../minecraft-economy-plugin/build/libs/economy-plugin-0.1.0.jar"))`로 `EconomyApi` 인터페이스만 컴파일 시점에 참조합니다(런타임 클래스는 economy-plugin이 로드한 것을 그대로 씀 — shade하지 않음).

## 사용 방법 (매뉴얼)

### 명령어

이 플러그인에는 명령어가 없습니다. 모든 기능은 표지판/상자 상호작용으로만 동작합니다.

1. 상자 옆면에 표지판을 붙입니다.
2. 판매할 아이템을 손에 든 채로 표지판의 1번째 줄에 `[shop]`을 적습니다. 2번째 줄에 수량(생략 시 1), 3번째 줄에 가격(0보다 큰 숫자, 필수)을 적습니다.
3. 다른 플레이어가 표지판을 그냥 우클릭하면 구매, 웅크린 채 우클릭하면 판매(상점에 되팔기)가 이루어집니다.

### 권한 노드

소스 코드 어디에도 `Permission` 등록이나 `permission()` 오버라이드가 없습니다. 즉 상점 생성·거래 모두 별도의 권한 제한 없이 모든 플레이어가 사용할 수 있습니다.

### config.yml 설정 항목

`config.yml`은 없습니다. 상점 표지판 형식(헤더 문자열 `[shop]`)은 `ShopCreateListener.kt`의 `HEADER` 상수로 코드에 고정되어 있습니다.

### 빌드 방법

이 플러그인은 economy-plugin의 `EconomyApi`를 컴파일 시점에 참조하므로, 먼저 `minecraft-economy-plugin` 디렉터리에서 plain jar를 만들어두어야 합니다.

```bash
cd plugins-dev/minecraft-economy-plugin
./gradlew jar
```

그다음 저장소 루트에서 chestshop-plugin을 빌드합니다.

```bash
./scripts/build-plugin.sh minecraft-chestshop-plugin
```

빌드된 jar(`build/libs/*-all.jar`)가 `data/plugins/`로 복사됩니다. 서버에는 economy-plugin과 chestshop-plugin이 둘 다 설치되어 있어야 하며, `paper-plugin.yml`의 의존성 선언에 따라 economy-plugin이 먼저 활성화됩니다. 반영하려면 `./scripts/console.sh reload confirm`을 실행하거나 서버를 재시작하세요.
