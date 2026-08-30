# DoubleJumpPlugin

## 간단한 요약

공중에서 스페이스바를 한 번 더 누르면 위로 튀어 오르는 "이단 점프(더블 점프)"를 흉내내는 Paper 플러그인입니다. 명령어나 설정 파일 없이, 서버에 설치하기만 하면 모든 플레이어에게 자동으로 적용됩니다.

## 설명

바닐라 마인크래프트는 공중에서의 추가 점프를 지원하지 않습니다. 이 플러그인은 클라이언트가 공중에서 비행을 시도할 때 보내는 `PlayerToggleFlightEvent`를 가로채서, 실제 비행 대신 위쪽으로 한 번 속도를 부여하는 방식으로 이단 점프를 구현합니다.

### 트리거 조건

- `PlayerToggleFlightEvent`가 발생했을 때, 해당 플레이어가
  - 서버가 판정한 `PlayerJumpEvent`(이륙) 이후 아직 착지하지 않은 "공중" 상태이고,
  - 이번에 뜬 이후 아직 이단 점프를 한 번도 쓰지 않았다면
  - 이단 점프가 발동합니다.
- 크리에이티브/관전자 모드는 이미 자체 비행 기능이 있으므로 건드리지 않습니다(`GameMode.CREATIVE`, `GameMode.SPECTATOR`는 항상 무시).
- 비행 전환 이벤트는 이 플러그인이 관리하는 "이단 점프 스위치" 용도이므로, 발동 여부와 관계없이 실제 비행 모드 전환은 항상 취소(`isCancelled = true`)됩니다.

### velocity 계산 방식

- 수직 속도: 이단 점프 시 `velocity.y`를 `0.5`로 설정합니다(바닐라 점프의 약 `0.42`보다 약간 큰 값). 이후 중력은 서버가 매 틱 평소처럼 적용하므로 별도 처리가 필요 없습니다.
- 수평 속도(관성): `Player#getVelocity()`의 X/Z 성분은 넉백처럼 서버가 명시적으로 부여한 속도만 반영하고, 걷기/달리기 같은 클라이언트 자체 이동은 반영하지 않습니다. 그래서 `MovementTrackingListener`가 매 `PlayerMoveEvent`마다 직전 위치와의 실제 이동량(수평 델타)을 캐싱해두고, 이단 점프 시 그 값을 그대로 수평 속도(X/Z)로 넘겨줍니다. 이렇게 해서 달리면서 이단 점프해도 진행 방향으로 계속 나아갑니다.

### 쿨다운(재사용 조건)

별도의 시간 기반 쿨다운은 없고, "공중에서 한 번 뜬 뒤 착지하기 전까지 최대 한 번"이라는 상태 기반 제한만 있습니다.

- `TakeoffListener`가 `PlayerJumpEvent`(서버가 이동 패킷으로 판정하는 신뢰할 수 있는 이륙 이벤트)를 받으면 플레이어를 "공중(airborne)" 상태로 기록합니다.
- 이단 점프를 한 번 쓰면 "사용함(doubleJumpUsed)"으로 기록하고, 클라이언트가 공중에서 스페이스바를 또 눌러도 아무 반응이 없도록 `allowFlight`를 즉시 꺼버립니다(계속 켜두면 클라이언트가 매번 짧게 예측 비행을 시도했다가 서버 취소로 되돌아오며 멈칫거리는 현상이 있었기 때문).
- `MovementTrackingListener`가 `PlayerMoveEvent`에서 `isOnGround()`로 착지를 감지하면 "공중"/"사용함" 기록을 지우고 `allowFlight`를 다시 켜서, 다음 점프에서 또 이단 점프를 쓸 수 있게 복구합니다.
- 플레이어가 서버를 나가면 `QuitCleanupListener`가 해당 플레이어의 기록(공중 상태, 사용 여부, 마지막 수평 이동량)을 모두 지워 메모리가 무한정 쌓이지 않게 합니다.

### 동작 흐름(이벤트 리스너)

| 리스너 | 이벤트 | 역할 |
| --- | --- | --- |
| `FlightTriggerListener` | `PlayerJoinEvent` | 접속 시 이단 점프 활성화(`allowFlight = true`, 크리에이티브/관전자 제외) |
| `FlightTriggerListener` | `PlayerToggleFlightEvent` | 조건 확인 후 이단 점프 발동(수직/수평 velocity 부여) 또는 무시, 실제 비행 전환은 항상 취소 |
| `TakeoffListener` | `PlayerJumpEvent`(Paper 확장 이벤트) | 이륙(공중 상태 진입) 기록 |
| `MovementTrackingListener` | `PlayerMoveEvent` | 최근 수평 이동량 캐싱 + 착지 감지 시 상태 초기화 및 `allowFlight` 복구 |
| `QuitCleanupListener` | `PlayerQuitEvent` | 퇴장 플레이어의 기록 정리 |

`DoubleJumpPlugin` 클래스는 이 네 리스너를 `onEnable()`에서 등록하고, 플러그인이 리로드되어도 이미 접속 중인 플레이어에게 바로 적용되도록 온라인 플레이어 전체에 `enableDoubleJumpFor()`를 호출합니다. `onDisable()` 시에는 모든 온라인 플레이어의 `allowFlight`를 원래 게임모드 기준(크리에이티브/관전자만 true)으로 되돌리고 내부 기록을 모두 비웁니다.

### 의존성

Paper API(`io.papermc.paper:paper-api`)만 `compileOnly`로 의존하며, 다른 플러그인에 대한 의존성은 없습니다. `PlayerJumpEvent`는 Paper가 제공하는 확장 이벤트이므로 순정 Spigot이 아닌 Paper(또는 그 포크) 서버가 필요합니다.

## 사용 방법(매뉴얼)

### 명령어 / 권한

이 플러그인은 별도의 명령어와 권한 노드를 등록하지 않습니다(`paper-plugin.yml`에 `commands`/`permissions` 섹션이 없음). 플러그인을 서버에 설치하기만 하면 크리에이티브/관전자 모드가 아닌 모든 플레이어에게 자동으로 적용됩니다. 특정 플레이어나 그룹에 대해 켜고 끄는 기능은 없습니다.

### config.yml

제공되는 설정 파일이 없습니다. 수직 점프 속도(`0.5`)는 `FlightTriggerListener.kt`의 `DOUBLE_JUMP_VERTICAL_VELOCITY` 상수로 코드에 하드코딩되어 있어, 값을 바꾸려면 소스를 수정하고 다시 빌드해야 합니다.

### 빌드 방법

저장소 루트에서 다음 명령을 실행합니다.

```bash
./scripts/build-plugin.sh minecraft-double-jump-plugin
```

빌드된 jar는 `data/plugins/`로 복사되며, 서버에 반영하려면 `./scripts/console.sh reload confirm`을 실행하거나 서버를 재시작하면 됩니다.
