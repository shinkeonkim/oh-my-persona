# ChatChannelsPlugin

### 1. 간단한 요약

전체 채팅과 지역(근처) 채팅을 분리해주는 채팅 채널 플러그인이다. 플레이어는 `/channel` 명령어로 기본 채널을 전환하거나, 메시지 앞에 `#global `/`#local ` 접두사를 붙여 그 메시지 한 번만 다른 채널로 보낼 수 있다.

### 2. 설명

- 현재 지원하는 채널은 두 가지다.
  - **전체(GLOBAL)**: 서버에 접속 중인 모든 플레이어에게 전달된다.
  - **지역(LOCAL)**: 메시지를 보낸 플레이어와 같은 월드에 있고, 반경 100블록(`LOCAL_CHAT_RADIUS`) 이내에 있는 플레이어에게만 전달된다.
- 채널별 상태 관리: `ChatChannelsPlugin`이 플레이어별 기본 채널을 `playerChannels: MutableMap<UUID, ChatChannel>`로 메모리에만 들고 있다. 별도 저장소나 파일에 영속화하지 않으므로 서버를 재시작하면 초기화된다(별도 지정이 없으면 기본값은 전체(GLOBAL)).
- 채팅 가로채기: `ChatChannelListener`가 Paper의 `io.papermc.paper.event.player.AsyncChatEvent`를 구독하고, 이벤트를 항상 `isCancelled = true`로 취소한 뒤 직접 메시지를 만들어 전송한다(바닐라 채팅 브로드캐스트는 사용하지 않음).
  - 원본 메시지는 `PlainTextComponentSerializer`로 순수 텍스트로 변환된다.
  - 메시지가 `#local `로 시작하면 그 한 번만 지역 채널로, `#global `로 시작하면 그 한 번만 전체 채널로 보내고, 접두사가 없으면 `/channel`로 설정해둔 플레이어의 기본 채널을 사용한다.
  - 전송 포맷: 지역 채널은 `§7[지역] {플레이어이름}: {내용}`(회색), 전체 채널은 `§f[전체] {플레이어이름}: {내용}`(흰색)이다.
  - 채널과 무관하게 콘솔(`Bukkit.getConsoleSender()`)에는 항상 메시지가 출력된다.
- 다른 플러그인에 대한 의존 관계는 없다(`paper-plugin.yml`에 `depend`/`softdepend` 없음). 소스 코드 내에서도 이 플러그인 자체 외에 다른 플러그인 API를 참조하지 않는다.
- 파티/길드 채널 등은 아직 구현되어 있지 않다(`docs/plugin-ideas/22-chat-channels.md` 기획 문서의 확장 아이디어이며, 현재 코드는 전체/지역 두 채널만 지원한다).

### 3. 사용 방법 (매뉴얼)

#### 명령어

- `/channel <global|local>`
  - `global`을 입력하면 기본 채널이 전체로, `local`을 입력하면 기본 채널이 지역으로 바뀐다.
  - 인자를 생략하거나 `global`/`local` 외의 값을 입력하면 `사용법: /channel <global|local>` 안내 메시지가 표시된다.
  - 탭 자동완성으로 `global`, `local` 두 값이 제안된다.
  - 콘솔 등 플레이어가 아닌 발신자가 실행하면 `플레이어만 사용할 수 있습니다.` 메시지를 받고 아무 동작도 하지 않는다.
  - 이 명령어는 `paper-plugin.yml`의 `commands` 섹션이 아니라 `onEnable()`에서 `registerCommand("channel", ChannelCommand(this))`로 코드 상에서 등록된다(Paper Brigadier `BasicCommand` 방식).

#### 채팅 접두사 (즉시 채널 전환)

- 메시지 맨 앞에 `#local `을 붙이면 그 메시지 하나만 지역 채널로 전송된다. (예: `#local 근처에 좀비 있어요`)
- 메시지 맨 앞에 `#global `을 붙이면 그 메시지 하나만 전체 채널로 전송된다.
- 접두사가 없으면 `/channel`로 설정한 기본 채널을 사용하며, 아무것도 설정하지 않았다면 기본값은 전체(GLOBAL)이다.

#### 권한 노드

- 코드 전체(`ChatChannelsPlugin.kt`, `ChannelCommand.kt`, `ChatChannelListener.kt`, `paper-plugin.yml`)를 확인한 결과, 별도로 등록된 권한 노드는 없다. `/channel` 명령어와 채팅 채널 전환은 서버에 접속한 모든 플레이어가 제한 없이 사용할 수 있다.

#### config.yml

- 별도의 `config.yml`은 존재하지 않는다. 채널 목록(`ChatChannel` enum: `GLOBAL`, `LOCAL`)과 지역 채널 반경(`LOCAL_CHAT_RADIUS = 100.0`블록)은 소스 코드에 상수/enum으로 하드코딩되어 있으며, 외부 설정 파일로 변경할 수 없다.

#### 빌드 방법

저장소 루트에서 다음 명령어를 실행한다.

```bash
./scripts/build-plugin.sh minecraft-chatchannels-plugin
```
