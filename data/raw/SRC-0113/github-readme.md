# minecraft-hello-plugin

## 간단한 요약

Paper 플러그인 개발을 처음 익히기 위한 최소 예제 플러그인입니다. 플레이어가 접속하면 초록색 이름과 함께 환영 메시지를 보여주고, `/hello` 명령어로 인사말을 출력합니다.

## 설명

이 플러그인은 두 가지 기능만 가지고 있습니다.

- **접속 환영 메시지** (`JoinListener`): 플레이어가 서버에 접속(`PlayerJoinEvent`)하면, 기본 접속 메시지 대신 `<플레이어 이름 (초록색)> 님이 서버에 접속했습니다. 환영합니다!` 형태의 메시지를 전체 서버에 표시합니다. 메시지는 문자열이 아니라 Adventure `Component`로 구성됩니다.
- **인사 명령어** (`HelloCommand`): `/hello` 명령어를 실행하면 `Hello, <world 또는 첫 번째 인자>!` 메시지를 실행한 사람에게 보냅니다.

`HelloPlugin.onEnable()`에서 `JoinListener`를 이벤트 리스너로 등록하고, `registerCommand("hello", HelloCommand())`로 `/hello` 명령어를 등록합니다. Paper 플러그인은 Bukkit/Spigot 시절과 달리 `paper-plugin.yml`의 `commands:` 섹션으로 명령어를 등록하지 않으며, 이렇게 코드에서 `BasicCommand` 구현체를 직접 등록합니다.

다른 플러그인에 대한 의존성은 없습니다. 서버가 기본 제공하는 Paper API(컴파일 시점에만 필요, `compileOnly`)만 사용합니다.

## 사용 방법 (매뉴얼)

### 명령어

| 명령어 | 설명 |
| --- | --- |
| `/hello` | 실행한 사람에게 `Hello, world!` 메시지를 보냅니다. |
| `/hello <이름>` | 첫 번째 인자를 그대로 사용해 `Hello, <이름>!` 메시지를 보냅니다. |

`HelloCommand`는 인자를 하나만 확인하며(`args.firstOrNull()`), 인자가 없으면 `world`를 기본값으로 사용합니다. 두 번째 이후 인자는 무시됩니다.

### 권한 노드

소스 코드(`HelloPlugin`, `HelloCommand`, `paper-plugin.yml`) 어디에도 별도의 권한(permission) 등록이 없습니다. 즉 `/hello` 명령어에는 권한 제한이 걸려 있지 않으며, 서버에 접속한 모든 플레이어가 사용할 수 있습니다.

### config.yml 설정 항목

이 플러그인에는 `config.yml`이 없습니다. 별도의 설정 항목도 없습니다.

### 빌드 방법

저장소 루트에서 다음 명령어를 실행합니다.

```bash
./scripts/build-plugin.sh minecraft-hello-plugin
```

빌드된 jar(`build/libs/*-all.jar`)가 `data/plugins/`로 복사됩니다. 서버에 반영하려면 `./scripts/console.sh reload confirm`을 실행하거나 서버를 재시작하세요.
