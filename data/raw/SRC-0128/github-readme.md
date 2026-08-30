# minecraft-tpa-plugin

## 간단한 요약

플레이어 간에 동의 기반으로 텔레포트를 주고받는 Paper 플러그인입니다. `/tpa`, `/tpahere`로 요청을 보내고 `/tpaccept`, `/tpdeny`로 응답하며, 요청은 일정 시간 뒤 자동 만료되고 수락 후에도 움직이면 이동이 취소됩니다.

## 설명

이 플러그인은 네 가지 명령어와 하나의 이벤트 리스너로 구성됩니다.

- **텔레포트 요청 전송** (`RequestCommands.kt`의 `TpaCommand`, `TpaHereCommand`): `/tpa <닉네임>`은 "요청을 보낸 사람이 상대방에게" 이동하는 요청이고, `/tpahere <닉네임>`은 "상대방을 요청을 보낸 사람에게" 불러오는 요청입니다. 대상이 접속 중이 아니거나 자기 자신을 지정하면 거부됩니다. 같은 대상에게 이미 대기 중인 요청이 있다면 새 요청이 기존 요청을 덮어씁니다 (`TpaPlugin.cancelExistingRequest`).
- **요청 수락/거절** (`ResponseCommands.kt`의 `TpAcceptCommand`, `TpDenyCommand`): `/tpaccept`는 자신에게 온 가장 최근 요청을 수락해 텔레포트 대기(워밍업)를 시작시키고, `/tpdeny`는 요청을 거절만 하고 아무 이동도 일으키지 않습니다. 대기 중인 요청이 없으면 각각 안내 메시지만 보냅니다.
- **요청 만료**: 요청은 `PendingRequest.expireTask`라는 예약 작업(`REQUEST_EXPIRY_TICKS` = 30초, `TpaPlugin.kt`)으로 관리되며, 응답 없이 시간이 지나면 요청이 자동으로 사라지고 양쪽 모두에게 만료 메시지가 전송됩니다.
- **텔레포트 워밍업/이동 취소** (`TpaPlugin.beginTeleportWarmup`, `TeleportWarmupListener`): 요청이 수락되면 실제로 이동할 플레이어(`/tpa`면 요청을 보낸 사람, `/tpahere`면 요청을 받은 사람)의 현재 위치를 기록해두고 `TELEPORT_WARMUP_TICKS`(3초) 뒤 `Player#teleportAsync`로 이동시킵니다. 그 사이 `PlayerMoveEvent`가 발생해 시작 위치에서 다른 월드로 가거나 0.3블록 이상 움직이면(`MOVE_CANCEL_THRESHOLD`) 이동이 취소됩니다. 시야만 돌리는 것은 무시됩니다.
- 상태(대기 중인 요청, 워밍업 정보)는 전부 메모리(`MutableMap`)에만 보관하며 영속 저장소가 없습니다. 서버가 재시작되거나 플러그인이 비활성화되면(`onDisable`) 모든 대기/예약 작업이 취소되고 초기화됩니다.
- 별도의 권한 노드나 쿨다운 기능은 구현되어 있지 않습니다. 다른 플러그인에 대한 의존성도 없으며, 컴파일 시점에만 필요한 Paper API(`compileOnly`)만 사용합니다.

## 사용 방법 (매뉴얼)

### 명령어

| 명령어 | 설명 |
| --- | --- |
| `/tpa <닉네임>` | 지정한 플레이어에게 "나를 그쪽으로 보내달라"는 텔레포트 요청을 보냅니다. |
| `/tpahere <닉네임>` | 지정한 플레이어에게 "당신을 내 위치로 불러오겠다"는 텔레포트 요청을 보냅니다. |
| `/tpaccept` | 자신에게 와 있는 대기 중인 요청을 수락합니다. 인자 없음. |
| `/tpdeny` | 자신에게 와 있는 대기 중인 요청을 거절합니다. 인자 없음. |

`/tpa`, `/tpahere`는 플레이어만 실행할 수 있고 (콘솔 실행 시 안내 메시지만 출력), 인자를 생략하면 사용법 메시지를 보여줍니다. 첫 번째 인자에 대해 온라인 플레이어 이름으로 탭 자동완성(`suggest`)을 지원합니다.

### 권한 노드

소스 코드(`TpaPlugin`, `RequestCommands.kt`, `ResponseCommands.kt`, `paper-plugin.yml`) 어디에도 권한(permission) 등록이 없습니다. 즉 네 명령어 모두 권한 제한 없이 서버에 접속한 모든 플레이어가 사용할 수 있습니다.

### config.yml 설정 항목

이 플러그인에는 `config.yml`이 없습니다. 요청 만료 시간(30초)과 워밍업 대기 시간(3초), 이동 취소 판정 거리(0.3블록)는 `TpaPlugin.kt`와 `TeleportWarmupListener.kt`에 상수로 하드코딩되어 있으며 별도의 설정 파일을 통해 바꿀 수 없습니다.

### 빌드 방법

저장소 루트에서 다음 명령어를 실행합니다.

```bash
./scripts/build-plugin.sh minecraft-tpa-plugin
```

빌드된 jar(`build/libs/*-all.jar`)가 `data/plugins/`로 복사됩니다. 서버에 반영하려면 `./scripts/console.sh reload confirm`을 실행하거나 서버를 재시작하세요.
