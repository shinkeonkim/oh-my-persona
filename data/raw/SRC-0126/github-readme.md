# minecraft-tablist-plugin

## 간단한 요약

Tab 키를 눌렀을 때 보이는 접속자 목록(탭리스트)의 헤더/푸터에 서버 이름과 접속자 수를 표시하고, AFK 상태인 플레이어의 이름 앞에 `[AFK]` 표시를 붙여주는 Paper 플러그인입니다. 별도의 명령어나 설정 파일 없이, 서버에 접속하는 즉시 자동으로 동작합니다.

## 설명

### 동작 방식

`TabListPlugin`(`src/main/kotlin/com/example/tablist/TabListPlugin.kt`)은 `onEnable()`에서 `server.scheduler.runTaskTimer`로 3초(60틱, `TAB_UPDATE_INTERVAL_TICKS = 20L * 3L`)마다 `refreshAll()`을 반복 실행하는 것이 전부인 단순한 구조입니다. 이벤트 리스너나 명령어는 존재하지 않습니다.

`refreshAll()`이 매 주기마다 하는 일:

1. **헤더/푸터 갱신** — `Player#sendPlayerListHeaderAndFooter(Component, Component)`를 호출해 모든 접속자에게 고정 헤더 `"우리들만의 서버"`와 현재 접속자 수를 담은 푸터 `"접속자: N명"`을 전송합니다.
2. **AFK 접두사 갱신** — 각 플레이어마다 `updatePrefix(player)`를 호출합니다. 이 함수는 플레이어의 스코어보드에서 `"t_" + (UUID의 hashCode를 16진수 문자열로 변환한 값)` 이름의 팀을 찾거나 없으면 새로 등록하고, 플레이어를 팀 엔트리로 추가합니다. 그리고 `afkApi?.isAfk(uuid) == true`이면 팀의 `prefix`를 `"[AFK] "`로, 아니면 빈 컴포넌트로 설정합니다. (docs/plugin-ideas/26-tab-list.md에서 언급한 "Team의 prefix/suffix 트릭"을 그대로 사용)

정렬 순서 커스터마이징 등 기획 문서에 "선택 사항"으로 언급된 기능은 구현되어 있지 않습니다.

### afk-plugin(AfkPlugin)에 대한 소프트 의존

이 플러그인은 AfkPlugin이 설치되어 있으면 AFK 상태를 활용하고, 없어도 헤더/푸터 기능은 정상 동작하도록 설계되어 있습니다. 실제 구현은 다음과 같습니다.

- **의존성 선언** (`src/main/resources/paper-plugin.yml`): `dependencies.server.AfkPlugin`에 `load: BEFORE`, `required: false`, `join-classpath: true`를 지정합니다. 즉 AfkPlugin이 설치돼 있으면 TabListPlugin보다 먼저 로드되고 클래스패스를 공유하지만, 필수 의존성은 아니므로 AfkPlugin이 없어도 TabListPlugin은 로드/활성화됩니다.
- **런타임 조회**: `onEnable()`에서 `server.servicesManager.getRegistration(AfkApi::class.java)?.provider`를 호출해 Bukkit `ServicesManager`에 등록된 `AfkApi` 구현체를 조회하고, 그 결과를 nullable 필드 `afkApi: AfkApi?`에 저장합니다. (참고로 AfkPlugin 쪽은 `AfkPlugin.kt`의 `onEnable()`에서 `server.servicesManager.register(AfkApi::class.java, this, this, ServicePriority.Normal)`로 자신을 서비스에 등록합니다.) AfkPlugin이 없거나 서비스 등록이 안 되어 있으면 `getRegistration(...)`은 `null`을 반환하고 `afkApi`도 `null`이 됩니다.
- **안전한 사용**: `updatePrefix()`에서 `afkApi?.isAfk(uuid) == true` 형태의 안전 호출(safe call)로 AFK 여부를 확인하므로, `afkApi`가 `null`이어도 예외 없이 `false`로 취급되어 `[AFK]` 접두사가 붙지 않을 뿐 나머지 로직(헤더/푸터 갱신, 팀 등록)은 그대로 수행됩니다.
- **컴파일 타임 참조**: `build.gradle.kts`에서 `compileOnly(files("../minecraft-afk-plugin/build/libs/afk-plugin-0.1.0.jar"))`로 AfkApi 인터페이스를 컴파일 시점에만 참조하고 shade(포함)하지 않습니다. 즉 빌드 시 옆의 `minecraft-afk-plugin` 프로젝트가 먼저 빌드되어 있어야 하며, 배포되는 jar 자체에는 AfkPlugin 코드가 포함되지 않습니다.

## 사용 방법(매뉴얼)

### 명령어 / 권한

이 플러그인은 등록된 명령어(`commands/`)나 권한(permission) 노드가 없습니다. 서버에 설치하고 활성화하면 자동으로 모든 플레이어에게 헤더/푸터와 AFK 접두사가 표시되며, 별도의 조작이 필요하지 않습니다.

### config.yml

별도의 `config.yml`은 존재하지 않으며, 설정 가능한 항목이 없습니다. 갱신 주기(3초)나 헤더/푸터 문구(`"우리들만의 서버"`, `"접속자: N명"`)는 현재 `TabListPlugin.kt` 코드에 하드코딩되어 있어 변경하려면 소스 코드를 직접 수정해야 합니다.

### 선택적 연동: AfkPlugin

- AfkPlugin(`minecraft-afk-plugin`)을 함께 설치하면 AFK 상태인 플레이어의 탭리스트 이름 앞에 `[AFK] `가 자동으로 표시됩니다.
- AfkPlugin 없이 이 플러그인만 설치해도 헤더/푸터 표시는 정상적으로 동작하며, 오류가 발생하지 않습니다.

### 빌드 방법

저장소 루트(`minecraft-server`)에서 다음 명령을 실행합니다.

```bash
./scripts/build-plugin.sh minecraft-tablist-plugin
```

AfkPlugin 연동 코드가 컴파일 타임에 `../minecraft-afk-plugin/build/libs/afk-plugin-0.1.0.jar`를 참조하므로, 빌드 전에 `minecraft-afk-plugin`이 먼저 빌드되어 해당 jar가 존재해야 합니다.
