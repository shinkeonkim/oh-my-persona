# minecraft-party-plugin

## 간단한 요약

친구들끼리 파티(그룹)를 만들어 함께 모험하고 파티 전용 채팅으로 대화할 수 있게 해주는 Paper 플러그인입니다. `/party` 명령어 하나로 파티 생성, 초대, 수락, 탈퇴, 해체, 목록 확인까지 처리하며, 메시지 앞에 `!`를 붙이면 파티원에게만 전달됩니다.

## 설명

이 플러그인은 `/party` 명령어 하나(`PartyCommand`)와 두 개의 이벤트 리스너(`PartyChatListener`, `PartyQuitListener`)로 구성됩니다.

- **파티 상태 관리** (`PartyPlugin.kt`, `Party.kt`): 파티는 `Party(id, leaderUuid, members)` 형태의 자체 클래스이며, `PartyPlugin`이 `parties`(파티 ID → 파티), `memberToParty`(플레이어 UUID → 파티 ID), `pendingInvites`(초대받은 플레이어 UUID → 파티 ID) 세 개의 `MutableMap`으로 상태를 메모리에만 보관합니다. 영속 저장소가 없으며, 서버 재시작이나 플러그인 비활성화(`onDisable`) 시 모든 파티 정보가 초기화됩니다.
- **파티 생성/초대/수락** (`PartyCommand.handleCreate/handleInvite/handleAccept`): `/party create`로 자신을 파티장으로 하는 새 파티를 만들고, 파티장만 `/party invite <닉네임>`으로 접속 중인 플레이어를 초대할 수 있습니다(대상이 오프라인이거나 이미 다른 파티에 속해 있으면 거부). 초대는 `pendingInvites`에 기록되며, 대상이 `/party accept`를 실행하면 그 초대가 소비되어 파티에 합류하고 기존 파티원 전원에게 합류 알림이 전송됩니다. 초대에는 만료 시간이나 거절 명령어가 없습니다(수락 전까지 계속 유효).
- **파티 탈퇴/해체** (`PartyCommand.handleLeave/handleDisband`): `/party leave`로 파티를 나갈 수 있으며, 파티장이 나가면 남은 인원 중 임의의 한 명(`members.first()`)에게 파티장이 자동으로 위임됩니다. 마지막 인원이 나가면 파티 자체가 제거됩니다. `/party disband`는 파티장만 실행할 수 있고, 실행 시 파티원 전원의 소속 정보를 지우고 파티를 즉시 없앱니다.
- **파티원 목록 확인** (`PartyCommand.handleList`): `/party list`는 현재 소속된 파티의 멤버 이름 목록과 파티장 이름을 보여줍니다.
- **파티 전용 채팅** (`PartyChatListener`): 일반 채팅 메시지(`AsyncChatEvent`)의 맨 앞이 `!`이면 그 메시지는 서버 전체 채팅으로 전송되지 않고(`event.isCancelled = true`) 파티원에게만 `§d[파티] <이름>: <내용>` 형식으로 전달됩니다. 파티에 속해 있지 않은 플레이어가 `!`로 시작하는 메시지를 보내면 아무 일도 일어나지 않고(이벤트가 취소되지 않아 일반 채팅으로 전송됨) 그대로 넘어갑니다.
- **접속 종료 처리** (`PartyQuitListener`): 파티원이 서버를 나가면(`PlayerQuitEvent`) 자동으로 파티에서 제외되고, 남은 파티원들에게 퇴장 알림이 전송됩니다(파티장 위임 로직은 탈퇴와 동일).
- **다른 플러그인과의 관계**: 이 플러그인은 다른 어떤 플러그인에도 의존하지 않는 완전히 독립된 플러그인입니다. 특히 채팅 채널 기능을 가진 `minecraft-chatchannels-plugin`과도 코드상 아무 연동이 없으며(import·참조 없음), 이 플러그인이 자체적으로 `AsyncChatEvent`를 가로채 파티 채팅을 구현합니다. `build.gradle.kts`에도 Paper API(`compileOnly`) 외의 의존성은 없습니다.

## 사용 방법 (매뉴얼)

### 명령어

| 명령어 | 설명 |
| --- | --- |
| `/party create` | 새 파티를 만들고 자신이 파티장이 됩니다. 이미 파티에 속해 있으면 실패합니다. |
| `/party invite <닉네임>` | 지정한 접속 중인 플레이어를 파티에 초대합니다. 파티장만 사용할 수 있습니다. |
| `/party accept` | 받은 파티 초대를 수락하고 해당 파티에 합류합니다. |
| `/party leave` | 현재 파티에서 나갑니다. 파티장이 나가면 다른 멤버에게 파티장이 위임됩니다. |
| `/party disband` | 파티를 완전히 해체합니다. 파티장만 사용할 수 있습니다. |
| `/party list` | 현재 파티의 멤버 목록과 파티장을 보여줍니다. |

인자를 생략하면 사용법 안내 메시지가 출력되고, 콘솔에서 실행하면 "플레이어만 사용할 수 있습니다" 메시지가 뜹니다. 첫 번째 인자는 `create/invite/accept/leave/disband/list` 중에서, `invite`의 두 번째 인자는 온라인 플레이어 이름으로 탭 자동완성(`suggest`)됩니다.

파티 채팅은 별도 명령어가 아니라, 채팅창에 메시지를 입력할 때 맨 앞에 `!`를 붙이는 방식으로 사용합니다 (예: `!같이 사냥가자`). 파티에 속해 있지 않으면 `!`를 붙여도 일반 채팅으로 그대로 전송됩니다.

### 권한 노드

소스 코드(`PartyPlugin`, `PartyCommand`, `PartyChatListener`, `PartyQuitListener`, `paper-plugin.yml`) 어디에도 권한(permission) 등록이 없습니다. 즉 `/party`의 모든 하위 명령어와 파티 채팅 기능은 권한 제한 없이 서버에 접속한 모든 플레이어가 사용할 수 있습니다.

### config.yml 설정 항목

이 플러그인에는 `config.yml`이 없습니다. 파티 채팅 트리거 문자(`!`)나 메시지 형식(`§d[파티] ...`) 등은 모두 코드에 하드코딩되어 있으며 별도의 설정 파일을 통해 바꿀 수 없습니다.

### 빌드 방법

저장소 루트에서 다음 명령어를 실행합니다.

```bash
./scripts/build-plugin.sh minecraft-party-plugin
```

빌드된 jar(`build/libs/*-all.jar`)가 `data/plugins/`로 복사됩니다. 서버에 반영하려면 `./scripts/console.sh reload confirm`을 실행하거나 서버를 재시작하세요.
