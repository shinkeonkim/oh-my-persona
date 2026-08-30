# SleepVotePlugin

## 요약

일정 비율 이상의 플레이어가 침대에 누우면 즉시 밤을 스킵(투표형 수면)해 주는 플러그인입니다. 접속자 전원이 잘 필요 없이 과반(기본 50%)만 자면 시간이 아침으로 넘어가고 폭풍우도 함께 그칩니다. 명령어나 설정 파일 없이 자동으로 동작합니다.

## 설명

- **수면 진행 상황 추적** (`BedListener`): `PlayerBedEnterEvent`/`PlayerBedLeaveEvent`를 감시해 현재 잠든 플레이어의 UUID를 `SleepVotePlugin.sleepingPlayers` 집합에 추가/제거하며 추적합니다.
- **투표 집계 및 스킵 판정**: 플레이어가 침대에 누우면(`onEnterBed`) 즉시 판정하지 않고, 다음 틱(`Bukkit.getScheduler().runTask`)으로 미뤄서 `checkAndSkip()`을 실행합니다. `PlayerBedEnterEvent` 발생 시점에는 서버가 아직 "잠들었다" 상태를 완전히 반영하기 전이라, 같은 핸들러 안에서 곧바로 `wakeup()`을 호출하면 `Cannot wakeup if not sleeping` 예외가 발생하기 때문입니다.
  - `checkAndSkip()`은 같은 월드에 접속 중인 플레이어 수 대비 잠든 플레이어 수의 비율을 계산해 채팅으로 안내합니다 (예: `잠든 인원: 2 / 4`).
  - 비율이 `SLEEP_RATIO_THRESHOLD`(기본값 `0.5`, 즉 50%) 이상이면 `world.setTime(0)`으로 시간을 아침으로 돌리고, `setStorm(false)`/`setThundering(false)`로 폭풍우·번개도 함께 멈춘 뒤, 아직 침대에 남아 있는 플레이어들을 `player.wakeup(false)`로 깨우고 채팅으로 스킵 완료를 안내합니다.
  - 비율 기준에 못 미치면 아무 것도 하지 않고 다음 플레이어의 수면/기상을 계속 기다립니다.
- **주민 거래 재고 초기화** (`restockVillagers`): `setTime(0)`처럼 시간이 자연스럽게 흐르지 않고 한 틱만에 점프하면, 주민의 Brain 스케줄이 낮/밤 전환을 놓쳐 그날의 거래 재고가 갱신되지 않는 문제가 있습니다. 이를 보정하기 위해 밤 스킵이 확정된 직후, 같은 월드에 있는 모든 `Villager` 엔티티의 거래 목록(`recipes`)을 순회하며 각 거래의 사용 횟수(`uses`)를 `0`으로 되돌려 강제로 재고를 초기화합니다.
- **접속 종료 정리** (`QuitCleanupListener`): 플레이어가 서버를 나가면(`PlayerQuitEvent`) 해당 플레이어를 `sleepingPlayers` 집합에서 제거해, 오프라인 플레이어가 잠든 인원으로 잘못 집계되지 않도록 합니다.
- 다른 플러그인에 대한 의존성은 없습니다.
- 참고: 바닐라의 `server.properties`에 있는 `players-sleeping-percentage` 설정과 동작이 겹치므로, 이 값을 100 이상으로 올려 바닐라 스킵을 사실상 비활성화하고 이 플러그인이 전담하도록 구성하는 것을 전제로 합니다.

## 사용 방법

이 플러그인은 등록된 명령어와 권한 노드가 없습니다. 플레이어가 침대에 누우면 자동으로 수면 비율을 계산해 동작합니다.

- **명령어**: 없음
- **권한**: 없음
- **config.yml**: 없음 (수면 스킵 비율은 `SleepVotePlugin.kt`의 상수 `SLEEP_RATIO_THRESHOLD`에 하드코딩되어 있으며 기본값은 `0.5`입니다)

### 빌드 방법

저장소 루트에서 다음을 실행합니다.

```bash
./scripts/build-plugin.sh minecraft-sleepvote-plugin
```
