# minecraft-mobdrops-plugin

## 간단한 요약

몬스터가 죽었을 때 바닐라 드롭에 더해 `config.yml`에 정의된 몬스터별 추가 드롭 테이블에 따라 아이템을 추가로 지급하는 플러그인입니다. 코드 수정 없이 설정 파일만 바꿔서 사냥 밸런스를 조정할 수 있습니다.

## 설명

- `MobDropsPlugin`이 `onEnable` 시점에 `config.yml`의 `drops` 섹션을 읽어 `EntityType → List<DropEntry>` 형태의 드롭 테이블(`dropTable`)을 메모리에 구성합니다.
- `MobDropListener`가 `EntityDeathEvent`를 구독하여, 죽은 엔티티의 타입에 해당하는 드롭 테이블이 있으면 각 `DropEntry`마다 독립적으로 확률(`chance`, 0.0~1.0)을 굴려 통과하면 `min`~`max` 사이의 무작위 개수만큼 아이템을 `event.drops`에 **추가**합니다. 즉 바닐라 드롭을 대체하지 않고 그 위에 더해지는 방식입니다.
- 확률 판정은 엔트리별로 독립적으로 이루어지므로, 한 몬스터에 여러 드롭 엔트리를 등록하면 여러 개가 동시에 나올 수도 있습니다.
- `min == max`이면 항상 해당 개수, `max > min`이면 `min`~`max`(포함) 범위에서 무작위 개수가 지급됩니다.
- 설정에서 존재하지 않는 `EntityType`이나 `Material` 이름, 또는 `material`/`chance` 필드가 없는 항목은 조용히 무시(skip)됩니다.
- 별도의 명령어나 권한 노드는 없습니다. 전적으로 `config.yml` 설정과 서버 재시작(또는 리로드)으로 동작합니다.
- 다른 플러그인에 대한 의존성은 없습니다.

## 사용 방법(매뉴얼)

### 명령어 / 권한

이 플러그인은 명령어와 권한 노드를 제공하지 않습니다. `config.yml`을 수정한 뒤 서버를 재시작하면 변경 사항이 적용됩니다.

### config.yml 설정

`drops` 아래에 몬스터의 바닐라 `EntityType` 이름(예: `ZOMBIE`, `SKELETON`, `CREEPER`, `SPIDER`)을 키로 하여 드롭 엔트리 리스트를 정의합니다. 각 엔트리는 다음 필드를 가집니다.

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `material` | String | 필수 | 드롭할 아이템의 바닐라 `Material` 이름 |
| `chance` | Double | 필수 | 드롭 확률 (0.0~1.0, 예: `0.05` = 5%) |
| `min` | Int | 선택 (기본값 1) | 드롭 시 최소 개수 |
| `max` | Int | 선택 (기본값 `min`과 동일) | 드롭 시 최대 개수 |

기본 제공 예시:

```yaml
drops:
  ZOMBIE:
    - material: EMERALD
      chance: 0.05
      min: 1
      max: 1
  SKELETON:
    - material: DIAMOND
      chance: 0.03
      min: 1
      max: 1
  CREEPER:
    - material: DIAMOND
      chance: 0.03
      min: 1
      max: 1
  SPIDER:
    - material: EMERALD
      chance: 0.04
      min: 1
      max: 2
```

한 몬스터에 여러 엔트리를 등록하면 각각 독립적으로 확률이 판정되어 여러 아이템이 동시에 나올 수 있습니다.

### 빌드 방법

저장소 루트에서 다음 명령으로 빌드합니다.

```bash
./scripts/build-plugin.sh minecraft-mobdrops-plugin
```
