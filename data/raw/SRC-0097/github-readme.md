# AfkPlugin

### 1. 간단한 요약

플레이어의 움직임·채팅·명령어 입력을 감시해서 일정 시간 이상 아무 활동이 없으면 AFK(자리 비움) 상태로 표시하고, 다른 플러그인이 이 상태를 조회할 수 있도록 API를 제공하는 Paper 플러그인입니다.

### 2. 설명

`AfkPlugin`(`com.example.afk.AfkPlugin`)은 활성화(`onEnable`) 시 다음 세 가지를 등록합니다.

- `ActivityListener`를 이벤트 리스너로 등록
- `AfkApi` 서비스를 `ServicesManager`에 `ServicePriority.Normal`로 등록 (다른 플러그인이 조회 가능)
- `checkAfk()`를 주기적으로 실행하는 반복 작업(스케줄러 태스크) 등록

**활동 감지**

`ActivityListener`는 아래 이벤트를 "활동"으로 간주하여 발생 시 해당 플레이어의 마지막 활동 시각을 현재 시각으로 갱신합니다.

- `PlayerJoinEvent` — 접속 시 활동으로 기록
- `PlayerMoveEvent` — 단, `from`과 `to`의 x/y/z 좌표가 완전히 동일하면(즉 시선만 돌린 경우) 활동으로 치지 않음
- `AsyncChatEvent` — 채팅
- `PlayerCommandPreprocessEvent` — 명령어 입력
- `PlayerQuitEvent` — 활동 갱신이 아니라 퇴장한 플레이어의 기록(`lastActivity`, `afkPlayers`)을 정리(제거)

**AFK 판정 로직**

- `AFK_THRESHOLD_MILLIS` = 5분(300,000ms) 동안 활동이 없으면 AFK로 간주합니다.
- `AFK_CHECK_INTERVAL_TICKS` = 400틱(20초)마다 접속 중인 모든 플레이어를 순회하며 마지막 활동 시각과 현재 시각의 차이를 확인합니다.
- 임계값을 넘어 새로 AFK 상태가 된 플레이어는 `afkPlayers` 집합에 추가되고, 서버 전체에 `"{플레이어명}님이 자리를 비웠습니다 (AFK)."` 메시지가 브로드캐스트됩니다.
- AFK 상태였던 플레이어가 다시 활동(이동/채팅/명령어 등)하면 `afkPlayers`에서 제거되고, `"{플레이어명}님이 활동을 재개했습니다."` 메시지가 브로드캐스트됩니다.
- 현재 구현에는 AFK 상태가 오래 지속돼도 자동으로 추방(kick)하는 기능은 없습니다.

**다른 플러그인과의 연동 (AfkApi)**

이 플러그인은 `tablist-plugin` 같은 다른 플러그인이 AFK 여부를 조회할 수 있도록 `AfkApi` 인터페이스를 Bukkit `ServicesManager`를 통해 공개합니다. `AfkPlugin` 자신이 이 인터페이스를 구현합니다.

```kotlin
interface AfkApi {
    fun isAfk(uuid: UUID): Boolean
}
```

다른 플러그인은 다음과 같이 서비스를 조회해서 사용할 수 있습니다.

```kotlin
val afkApi = Bukkit.getServicesManager().load(AfkApi::class.java)
val isAfk = afkApi?.isAfk(player.uniqueId) ?: false
```

### 3. 사용 방법 (매뉴얼)

- **명령어**: 없습니다. 이 플러그인은 별도의 명령어(`commands/`)를 등록하지 않습니다.
- **권한 노드**: 없습니다. 소스 코드에 `addPermission` 등 권한 등록 로직이 없고, `paper-plugin.yml`에도 권한/명령어 정의가 없습니다.
- **config.yml**: 없습니다. 설정 파일 없이 코드 내 상수(`AFK_THRESHOLD_MILLIS` = 5분, `AFK_CHECK_INTERVAL_TICKS` = 20초)로 동작하며, 값을 바꾸려면 소스 코드를 수정해야 합니다.
- **plugin 정보** (`paper-plugin.yml` 기준)
  - 이름: `AfkPlugin`
  - 메인 클래스: `com.example.afk.AfkPlugin`
  - `api-version`: `1.20`

**빌드 방법**

저장소 루트에서 다음 명령을 실행합니다.

```bash
./scripts/build-plugin.sh minecraft-afk-plugin
```
