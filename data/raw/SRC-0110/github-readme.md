# minecraft-elevator-plugin

## 요약
철 블록(기본값) 위에 서서 점프하거나 웅크리면, 같은 X/Z 좌표의 세로선상에서 가장 가까운 다음 철 블록으로 순간이동시켜주는 엘리베이터 플러그인입니다.

## 설명
- `ElevatorPlugin`이 활성화되면 `ElevatorListener`를 이벤트 리스너로 등록합니다.
- `onJump` — Paper 전용 이벤트인 `PlayerJumpEvent`를 구독합니다. 플레이어가 엘리베이터 블록(기본값 `IRON_BLOCK`) 위에 서 있는 상태에서 점프하면, 위쪽(+Y) 방향으로 다음 엘리베이터 블록을 찾아 그 위로 이동시킵니다.
- `onToggleSneak` — `PlayerToggleSneakEvent`를 구독합니다. 웅크리기를 "시작"하는 순간(`event.isSneaking == true`)에만 반응하며, 엘리베이터 블록 위에 서 있으면 아래쪽(-Y) 방향으로 다음 엘리베이터 블록을 찾아 그 위로 이동시킵니다. 웅크리기를 푸는 순간은 무시합니다.
- 탐색은 플레이어가 밟고 있는 블록의 바로 위 또는 아래 칸부터 시작해 같은 X, Z 좌표를 따라 Y축으로만 진행하며, 현재 밟고 있는 엘리베이터 블록 자체는 건너뜁니다. 최대 `MAX_SCAN_RANGE`(64칸)까지만 탐색하고, 그 범위 안에서 다음 엘리베이터 블록을 찾지 못하면 "이 방향에 다른 엘리베이터 블록이 없습니다." 메시지를 플레이어에게 보냅니다.
- 목적지를 찾으면 찾은 블록의 바로 위 좌표로 `Player#teleportAsync`를 사용해 비동기 순간이동합니다. (X/Z, 시야각(yaw/pitch)은 그대로 유지)
- 엘리베이터로 취급하는 블록 종류(`TRIGGER_MATERIAL`, 기본값 `Material.IRON_BLOCK`)와 최대 탐색 범위(`MAX_SCAN_RANGE`, 기본값 64)는 현재 코드에 상수로 고정되어 있으며, 설정 파일(config.yml)은 존재하지 않습니다.
- 명령어와 권한 노드는 등록되어 있지 않습니다 — 전적으로 이벤트 기반으로 자동 동작합니다.
- 다른 플러그인에 대한 직접적인 의존성은 없습니다. 다만 이 서버의 `double-jump-plugin`과 함께 설치할 경우를 염두에 두고, `PlayerToggleFlightEvent`가 아니라 `PlayerJumpEvent`(점프)와 `PlayerToggleSneakEvent`(웅크리기)를 사용해 이벤트 충돌 가능성을 줄였습니다.

## 사용 방법
1. 이동하고 싶은 층마다 같은 X, Z 좌표에 철 블록(`IRON_BLOCK`)을 하나씩 놓습니다.
2. 철 블록 위에 서서 점프하면 위층의 다음 철 블록으로, 웅크리면 아래층의 다음 철 블록으로 이동합니다.
3. 별도의 명령어, 권한 설정, config.yml 설정은 필요하지 않습니다.

### 빌드 방법
저장소 루트에서 다음 명령어를 실행합니다.

```bash
./scripts/build-plugin.sh minecraft-elevator-plugin
```
