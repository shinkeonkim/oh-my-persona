# minecraft-scoreboard-plugin

## 간단한 요약

접속 중인 모든 플레이어의 화면 오른쪽에 좌표·잔액·접속자 수를 보여주는 사이드바 스코어보드를 2초마다 자동으로 갱신해서 표시하는 Paper 플러그인입니다. 별도의 명령어 조작 없이 접속과 동시에 표시되며, economy-plugin이 서버에 함께 설치되어 있으면 잔액 줄이 추가로 표시됩니다.

## 설명

- `ScoreboardPlugin` (`src/main/kotlin/com/example/scoreboard/ScoreboardPlugin.kt`)이 유일한 클래스이며, 별도의 `listeners/`, `commands/` 패키지나 `config.yml`은 존재하지 않습니다.
- `onEnable()`에서 `server.scheduler.runTaskTimer`로 반복 작업을 등록하며, 최초 1회(0틱 지연) 실행 후 `SCOREBOARD_UPDATE_INTERVAL_TICKS`(20틱 × 2 = 2초)마다 `refreshAll()`을 호출해 온라인 플레이어 전원의 사이드바를 다시 그립니다.
- `updateSidebar(player)`는 플레이어가 아직 서버 기본 스코어보드(`mainScoreboard`)를 쓰고 있으면 전용 스코어보드를 새로 만들어 지정하고, `"info"`라는 이름의 `dummy` 타입 objective를 `DisplaySlot.SIDEBAR`에 등록합니다(없으면 최초 1회만 생성).
- 매 갱신마다 기존 점수를 전부 `resetScores`로 지운 뒤, `buildLines(player)`가 만든 줄 목록을 점수 역순(위에서부터 큰 점수)으로 다시 등록합니다. 같은 텍스트의 줄이 여러 개 있어도 스코어보드 API가 요구하는 "줄마다 고유한 문자열" 제약을 지키기 위해, 각 줄 끝에 보이지 않는 색상 리셋 코드(`§r`)를 줄 순서만큼 반복해 붙여 고유성을 확보합니다.
- 표시되는 줄 구성(`buildLines`):
  1. `좌표: X, Y, Z` (항상 표시, 블록 좌표 기준)
  2. `잔액: 0.0` 형식 (economy-plugin이 감지된 경우에만 표시)
  3. `접속자: N명` (항상 표시, 현재 온라인 플레이어 수)
- 기획 문서(`docs/plugin-ideas/25-scoreboard-sidebar.md`)에는 `/scoreboard toggle`로 켜고 끄는 기능이 아이디어로 제시되어 있지만, 실제 코드에는 명령어나 권한 노드가 전혀 구현되어 있지 않습니다. 즉 현재 버전은 항상 켜져 있고 플레이어가 개별적으로 끌 수 없습니다.

### economy-plugin에 대한 소프트 의존

- `paper-plugin.yml`의 `dependencies.server.EconomyPlugin`에 `load: BEFORE`, `required: false`, `join-classpath: true`로 선언되어 있습니다. 이 덕분에 EconomyPlugin이 서버에 있으면 스코어보드 플러그인보다 먼저 로드되고 그 클래스패스를 참조할 수 있지만, 없어도 서버 구동이나 활성화에는 전혀 영향을 주지 않습니다.
- 빌드 시에는 economy-plugin의 산출물 jar(`../minecraft-economy-plugin/build/libs/economy-plugin-0.1.0.jar`)를 `compileOnly` 의존성으로만 참조해 `EconomyApi` 인터페이스 타입에 대해 컴파일이 되도록 하고, shadowJar에는 포함(shade)하지 않습니다.
- 런타임 연동은 Bukkit `ServicesManager`를 통해 이루어집니다. `onEnable()`에서 `server.servicesManager.getRegistration(EconomyApi::class.java)?.provider`로 등록된 구현체를 조회해 nullable 필드 `economy: EconomyApi?`에 저장합니다. economy-plugin이 설치되어 있지 않거나 아직 서비스를 등록하지 않았다면 이 값은 `null`이 되고, `buildLines`에서 `economy?.let { ... }`로 안전하게 건너뛰어 잔액 줄만 빠진 채 나머지 기능(좌표, 접속자 수)은 정상 동작합니다.

## 사용 방법(매뉴얼)

- **명령어**: 없습니다. 플러그인이 활성화되면 온라인 플레이어 전원에게 자동으로 사이드바가 표시되며, 별도의 명령어로 켜거나 끌 수 없습니다.
- **권한 노드**: 없습니다. `paper-plugin.yml`에 등록된 permission이 없고, 코드 내에도 권한 체크 로직이 없습니다.
- **config.yml**: 존재하지 않습니다. 갱신 주기(2초)는 코드 상수 `SCOREBOARD_UPDATE_INTERVAL_TICKS`로 고정되어 있으며 설정 파일로 변경할 수 없습니다.
- **선택적 연동**: economy-plugin(`EconomyPlugin`)을 함께 설치하면 사이드바에 잔액 줄이 자동으로 추가됩니다. 별도 설정은 필요 없습니다.
- **빌드 방법**: 저장소 루트에서 다음을 실행합니다.

  ```bash
  ./scripts/build-plugin.sh minecraft-scoreboard-plugin
  ```

  빌드된 jar는 `data/plugins/`로 복사되며, 서버에 반영하려면 `./scripts/console.sh reload confirm`을 실행하거나 서버를 재시작합니다.
