# DailyRewardPlugin

## 간단한 요약

플레이어가 하루에 한 번 `/daily` 명령으로 출석 보상을 받을 수 있게 해주는 플러그인입니다. 연속 출석일수를 추적해 오래 연속 출석할수록 더 많은 재화를 지급하며, 지급된 재화는 economy-plugin의 잔액에 바로 적립됩니다.

## 설명

- **명령 기반 지급**: 자동 지급(접속 시 자동 지급) 기능은 구현되어 있지 않고, 플레이어가 직접 `/daily` 명령을 입력해야 보상을 받습니다. `PlayerJoinEvent` 등 별도의 리스너는 없으며(`listeners/` 디렉터리 자체가 존재하지 않음), 오직 `/daily` 명령을 처리하는 `DailyCommand` 하나만 등록되어 있습니다.
- **하루 판정 및 연속 출석 로직**: 플레이어별로 `(마지막 수령일, 연속 출석일수)`를 메모리에 들고 있다가 플러그인 데이터 폴더의 `daily.yml`에 저장합니다.
  - 오늘 날짜에 이미 수령했다면(`마지막 수령일 == 오늘`) 재지급을 거부하고 "오늘 출석 보상은 이미 받았습니다. 내일 다시 오세요." 라는 안내만 보냅니다.
  - 마지막 수령일이 정확히 "어제"라면 연속 출석일수를 1 증가시키고, 그렇지 않다면(하루 이상 건너뛰었거나 최초 수령이면) 연속 출석일수를 1로 초기화합니다.
- **보상 금액 계산**: 기본 보상 50 + (연속 출석 보너스일수 × 10). 보너스일수는 `(연속 출석일수 - 1)`이며 최대 10일치까지만 보너스가 누적됩니다(11일째부터는 보너스가 더 늘지 않고 상한선에서 고정). 즉 최대 지급액은 `50 + 10 × 10 = 150`입니다. 이 값들은 `BASE_REWARD`(50.0), `STREAK_BONUS_PER_DAY`(10.0), `MAX_STREAK_BONUS_DAYS`(10) 상수로 코드에 하드코딩되어 있으며, 별도의 `config.yml` 설정 파일은 존재하지 않습니다.
- **한국 시간대(Asia/Seoul) 기준 판정**: 코드 상단에 `val SERVER_ZONE: ZoneId = ZoneId.of("Asia/Seoul")`로 고정된 타임존이 정의되어 있고, 출석 판정에 사용하는 "오늘 날짜"는 `LocalDate.now(SERVER_ZONE)`으로 항상 한국 시간대의 자정 기준 날짜로 계산됩니다. 즉 서버 OS의 시스템 타임존이 무엇이든 상관없이 이 플러그인 자체가 Asia/Seoul 자정을 기준으로 "하루가 지났는지"를 판정합니다.
- **economy-plugin에 대한 하드 의존**: `src/main/resources/paper-plugin.yml`에 `dependencies.server.EconomyPlugin`이 `load: BEFORE`, `required: true`, `join-classpath: true`로 선언되어 있어 EconomyPlugin이 먼저 로드되고 클래스패스도 공유합니다. 또한 `onEnable()`에서 `server.servicesManager.getRegistration(EconomyApi::class.java)`로 서비스를 조회하는데, 등록된 `EconomyApi`를 찾지 못하면 `logger.severe(...)`로 에러를 남기고 `server.pluginManager.disablePlugin(this)`를 호출해 플러그인 스스로를 즉시 비활성화합니다. 보상 지급은 아이템이 아니라 `economy.deposit(player.uniqueId, reward)` 호출을 통한 재화(잔액) 입금으로만 이루어집니다.
- 데이터 저장 형식: `daily.yml`의 `players.<UUID>.lastClaim`(ISO 날짜 문자열)과 `players.<UUID>.streak`(정수)로 저장되며, 플러그인 비활성화 시(`onDisable`)에도 저장됩니다.

## 사용 방법(매뉴얼)

### 명령어

| 명령 | 설명 |
| --- | --- |
| `/daily` | 오늘의 출석 보상을 수령합니다. 이미 수령했다면 다음 안내만 표시됩니다: "오늘 출석 보상은 이미 받았습니다. 내일 다시 오세요." 플레이어만 사용할 수 있으며, 콘솔 등에서 실행하면 "플레이어만 사용할 수 있습니다." 메시지가 출력됩니다. |

### 권한 노드

코드(`DailyCommand`, `paper-plugin.yml`) 전체를 확인한 결과 별도의 권한(permission) 노드가 정의되어 있지 않습니다. `/daily` 명령은 플레이어이기만 하면 누구나 사용할 수 있습니다.

### config.yml 설정

별도의 `config.yml` 파일이 없습니다. 보상 금액 관련 값(기본 보상, 연속 출석 보너스, 보너스 상한일수)은 모두 `DailyRewardPlugin.kt`에 상수로 하드코딩되어 있습니다:

- `BASE_REWARD = 50.0` (기본 지급액)
- `STREAK_BONUS_PER_DAY = 10.0` (연속 출석 1일당 추가 보너스)
- `MAX_STREAK_BONUS_DAYS = 10` (보너스가 누적되는 최대 일수, 이후엔 상한 고정)

### 필수 선행 조건

이 플러그인은 economy-plugin 없이는 동작하지 않습니다. 서버에 economy-plugin이 먼저 설치·활성화되어 있어야 하며, `EconomyApi` 서비스가 등록되지 않으면 DailyRewardPlugin은 활성화 직후 스스로 비활성화됩니다.

### 빌드 방법

저장소 루트에서 다음 명령을 실행합니다:

```bash
./scripts/build-plugin.sh minecraft-dailyreward-plugin
```
