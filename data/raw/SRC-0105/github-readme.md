# CustomEnchants Plugin

## 간단한 요약

바닐라 인챈트인 날카로움(Sharpness), 보호(Protection), 힘(Power), 강타(Smite), 절지(Bane of Arthropods)의 최대 레벨을 기본값(5)에서 **10**까지 실제로 확장하는 플러그인입니다. `/customenchant` 명령으로 확장된 6~10레벨 인챈트를 아이템에 직접 부여할 수 있습니다.

## 설명

이 플러그인의 핵심은 "가짜로 흉내 낸" 인챈트가 아니라, 서버 부트스트랩 단계에서 Paper의 인챈트 레지스트리 이벤트(`RegistryEvents.ENCHANTMENT`)를 이용해 바닐라 `minecraft:sharpness`, `minecraft:protection` 등 인챈트 자체의 `max_level` 값을 올리는 방식입니다. Sharpness/Protection 등은 데미지·방어 공식이 선형(`minecraft:linear`) 값 제공자로 되어 있어서, `max_level`만 올리면 수치도 자동으로 비례 확장됩니다.

- `CustomEnchantsBootstrap`(`PluginBootstrap` 구현체)이 월드가 로드되기 전인 부트스트랩 단계에서 실행되어, 아래 5개 인챈트에 대해 `maxLevel(10)`을 등록합니다.
  - `minecraft:sharpness`
  - `minecraft:protection`
  - `minecraft:power`
  - `minecraft:smite`
  - `minecraft:bane_of_arthropods`
- `paper-plugin.yml`에 `bootstrapper: com.example.enchants.CustomEnchantsBootstrap` 로 등록되어 있어야 이 부트스트랩이 실제로 동작합니다.
- 인챈트 테이블/모루로는 책장 개수 제한 때문에 자연스럽게 6~10레벨을 얻기 어렵습니다. 따라서 확장된 레벨은 `/customenchant` 명령으로 `ItemMeta#addEnchant(Enchantment, level, true)`(레벨 제한 무시 플래그)를 사용해 직접 부여하는 것을 전제로 설계되었습니다. 상점 보상, 퀘스트 보상 등에서 활용할 수 있습니다.
- 다른 플러그인에 대한 의존성은 없습니다.

## 사용 방법(매뉴얼)

### 명령어

| 명령어 | 설명 |
| --- | --- |
| `/customenchant <인챈트키> <레벨>` | 손에 든 아이템에 지정한 인챈트를 지정한 레벨로 부여합니다. 예: `/customenchant sharpness 10` |

- `<인챈트키>`는 `sharpness`처럼 바닐라 인챈트의 키 이름(소문자)입니다. 알 수 없는 키를 입력하면 오류 메시지가 나옵니다.
- `<레벨>`은 1부터 해당 인챈트의 (확장된) 최대 레벨까지 입력할 수 있습니다. 범위를 벗어나면 오류 메시지가 나옵니다.
- 손에 아이템을 들고 있지 않으면 사용할 수 없습니다.
- 플레이어만 사용할 수 있습니다(콘솔 사용 불가).

### 권한 노드

| 권한 | 기본값 | 설명 |
| --- | --- | --- |
| `customenchants.use` | OP | `/customenchant` 명령 사용 권한 |

### 설정 파일

별도의 `config.yml`은 없습니다. 확장 대상 인챈트 목록과 최대 레벨(`MAX_ENCHANT_LEVEL = 10`)은 `CustomEnchantsBootstrap.kt` 코드에 하드코딩되어 있습니다.

### 빌드 방법

저장소 루트에서 다음 명령으로 빌드합니다.

```bash
./scripts/build-plugin.sh minecraft-customenchants-plugin
```
