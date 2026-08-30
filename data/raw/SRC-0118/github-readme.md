# Minecraft Mailbox Plugin

### 1. 간단한 요약

접속 중이 아닌 플레이어에게도 메시지를 남길 수 있는 오프라인 우편함 플러그인입니다. `/mail send`로 우편을 보내면 YAML 파일에 저장되고, 수신자가 접속하면 알림을 받은 뒤 `/mail read`로 확인할 수 있습니다.

### 2. 설명

- **우편 전송 (`MailboxPlugin.send`)**: `/mail send <닉네임> <내용>`을 실행하면 `Bukkit.getOfflinePlayer(닉네임)`으로 수신자를 조회하고, 해당 플레이어의 UUID를 키로 하는 우편함 목록(`mailboxes: MutableMap<UUID, MutableList<Mail>>`)에 `Mail(sender, message, sentAtMillis)`을 추가합니다. 수신자가 서버에 한 번도 접속한 적이 없고(`hasPlayedBefore() == false`) 현재 온라인도 아니면 "그런 플레이어를 찾을 수 없습니다" 메시지를 띄우고 전송을 거부합니다. 우편 개수 제한은 걸려 있지 않습니다.
- **접속 시 알림 (`MailJoinListener`)**: `PlayerJoinEvent`가 발생하면 `plugin.unreadCount(uuid)`로 해당 플레이어의 미확인 우편 개수를 확인하고, 1개 이상이면 "읽지 않은 우편이 N개 있습니다. /mail read로 확인하세요." 메시지를 보냅니다.
- **우편 읽기 (`MailboxPlugin.collectAndClear`)**: `/mail read`를 실행하면 해당 플레이어의 우편함 전체를 가져오면서 동시에 맵에서 제거(읽으면 즉시 소비)합니다. 우편이 없으면 "받은 우편이 없습니다."를, 있으면 "=== 우편함 (N개) ==="와 함께 `[발신자] 내용` 형식으로 각 우편을 순서대로 출력합니다.
- **데이터 저장/로딩**: `onEnable()`에서 플러그인 데이터 폴더 아래 `mail.yml` 파일을 로딩하고(`loadData()`), `onDisable()` 시점과 우편 송신/수신(변경이 생길 때마다) 시점에 `saveData()`로 즉시 저장합니다. YAML 구조는 `players.<UUID>.mails.<index>.{sender, message, sentAt}` 형태이며, 인덱스는 정수 문자열 순으로 정렬해 복원합니다. 텍스트 메시지만 저장하며, 아이템(인벤토리 오브젝트) 첨부 기능은 구현되어 있지 않습니다.
- **명령어 처리 방식**: `MailCommand`는 Paper의 `BasicCommand`(Brigadier 기반) 인터페이스를 구현하며, `execute(source, args)`에서 `args[0]`을 보고 `send`/`read` 서브커맨드로 분기합니다. 플레이어가 아닌 콘솔 등에서 실행하면 "플레이어만 사용할 수 있습니다."를 반환합니다.
- **의존 플러그인**: 없습니다. 다만 기획 문서(`docs/plugin-ideas/21-mailbox.md`)는 파티/경제 플러그인 등이 이 플러그인을 통해 오프라인 알림을 재사용하는 것을 염두에 두고 있으나, 현재 코드에는 그런 외부 API(예: `Mailbox.send(uuid, message)` 형태의 공개 API)가 노출되어 있지 않고, `MailboxPlugin.send(recipient: OfflinePlayer, senderName: String, message: String)`가 사실상 유일한 진입점입니다.

### 3. 사용 방법 (매뉴얼)

**명령어**

- `/mail send <닉네임> <내용...>` — 지정한 닉네임의 플레이어(오프라인 포함, 서버 접속 이력이 있어야 함)에게 우편을 보냅니다. `<내용...>`은 마지막 인자부터 끝까지 공백으로 합쳐진 문자열입니다.
- `/mail read` — 자신에게 온 우편을 모두 확인하고, 확인한 우편은 우편함에서 삭제됩니다(다시 조회 불가).
- 인자 없이 `/mail`만 입력하면 사용법 안내 메시지가 출력됩니다.
- 콘솔 등 플레이어가 아닌 발신자가 실행하면 오류 메시지만 출력되고 아무 동작도 하지 않습니다.

**권한 노드**

이 플러그인은 별도의 권한 노드를 정의하거나 등록하지 않습니다(`paper-plugin.yml`에 permissions 섹션 없음, 코드 내 `addPermission` 호출도 없음). 즉 서버에 접속한 모든 플레이어가 `/mail send`, `/mail read`를 제한 없이 사용할 수 있습니다.

**config.yml**

별도의 `config.yml`은 존재하지 않으며, 설정 가능한 옵션도 없습니다. 우편 데이터는 플러그인 데이터 폴더의 `mail.yml`에 자동 저장됩니다.

**빌드 방법**

저장소 루트에서 다음을 실행합니다.

```
./scripts/build-plugin.sh minecraft-mailbox-plugin
```
