# minecraft-discordwebhook-plugin

### 1. 간단한 요약

서버에서 일어나는 플레이어 접속/퇴장/사망/채팅 이벤트를 디스코드 웹훅으로 실시간 전송하는 단방향(게임 → 디스코드) 알림 플러그인입니다.

### 2. 설명

`DiscordWebhookPlugin`은 서버가 활성화될 때 `config.yml`에서 `webhook-url` 값을 읽어들이고, `DiscordEventListener`를 통해 다음 4가지 Bukkit/Paper 이벤트를 구독합니다.

- `PlayerJoinEvent` → `**닉네임**님이 접속했습니다.`
- `PlayerQuitEvent` → `**닉네임**님이 퇴장했습니다.`
- `PlayerDeathEvent` → 서버가 생성한 사망 메시지(`deathMessage()`)를 평문으로 변환해 `💀 <사망 메시지>` 형태로 전송
- `AsyncChatEvent` (Paper의 비동기 채팅 이벤트) → `**닉네임**: <채팅 내용>`

각 이벤트가 발생하면 위 형식으로 만들어진 문자열을 `DiscordWebhookPlugin.sendAsync(message: String)`에 넘깁니다. `sendAsync`는 `webhook-url`이 비어 있으면 즉시 아무것도 하지 않고 조용히 종료하며, 값이 있으면 `Bukkit.getScheduler().runTaskAsynchronously`로 메인 스레드가 아닌 별도 스레드에서 HTTP 요청을 보냅니다(네트워크 지연으로 서버가 멈칫거리는 것을 방지).

전송 형식은 외부 라이브러리 없이 Java 표준 `java.net.http.HttpClient`를 사용하며, 메시지 문자열의 `\`, `"`, 줄바꿈만 최소한으로 이스케이프한 뒤 다음과 같은 JSON 본문으로 POST합니다.

```json
{"content": "여기에 위에서 만든 메시지 문자열이 들어감"}
```

이는 [디스코드 웹훅 API](https://discord.com/developers/docs/resources/webhook#execute-webhook)의 `content` 필드만 사용하는 가장 단순한 형태이며, embed나 username/avatar 오버라이드 등은 사용하지 않습니다.

전송 실패(네트워크 오류 등) 시에는 예외를 잡아 서버 로그에 경고만 남기고 서버 동작에는 영향을 주지 않습니다.

이 플러그인은 명령어나 권한 노드를 전혀 제공하지 않으며(관련 `commands/` 디렉터리 자체가 존재하지 않음), 다른 플러그인에 대한 의존성도 없습니다. `paper-plugin.yml`에도 명령어/권한 항목이 정의되어 있지 않습니다.

### 3. 사용 방법 (매뉴얼)

이 플러그인은 인게임 명령어나 권한 노드가 없습니다. 설정은 오직 `config.yml` 파일 하나로 이루어집니다.

#### 디스코드 웹훅 URL 발급 방법

1. 디스코드에서 알림을 받고 싶은 채널로 이동합니다.
2. 채널 설정(톱니바퀴 아이콘) → **연동** → **웹후크** 메뉴로 들어갑니다.
3. **새 웹후크 만들기**를 누르고 이름을 원하는 대로 지정합니다.
4. **웹후크 URL 복사** 버튼을 눌러 URL을 복사합니다.

#### config.yml 설정

플러그인을 처음 실행하면 `plugins/DiscordWebhookPlugin/config.yml`이 아래 기본값으로 생성됩니다.

```yaml
# 디스코드 채널 설정 > 연동 > 웹후크에서 만든 URL을 여기 붙여넣으세요.
# 비워두면 이 플러그인은 아무것도 전송하지 않습니다 (에러 없이 조용히 꺼진 상태로 동작).
webhook-url: ""
```

`webhook-url` 키에 복사해 둔 웹훅 URL을 그대로 붙여넣으면 됩니다.

```yaml
webhook-url: "https://discord.com/api/webhooks/xxxxxxxxxxxxxxxxxxx/yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
```

주의사항:

- `webhook-url`을 비워두면 경고 로그(`config.yml의 webhook-url이 비어 있어 디스코드 전송이 비활성화됩니다.`)만 남기고 전송 기능이 비활성화될 뿐, 서버가 죽거나 에러가 발생하지는 않습니다.
- 웹훅 URL은 사실상 비밀번호와 같으므로 git 저장소에 커밋하거나 외부에 공유하지 마세요. 서버에 배포된 `plugins/DiscordWebhookPlugin/config.yml`에만 실제 값을 넣어야 합니다.
- 설정을 변경한 뒤에는 서버를 재시작하거나 플러그인을 다시 로드해야 반영됩니다.

#### 빌드 방법

저장소 루트에서 다음 명령을 실행합니다.

```bash
./scripts/build-plugin.sh minecraft-discordwebhook-plugin
```

빌드된 jar가 `data/plugins/`로 복사되며, 이후 `./scripts/console.sh reload confirm` 실행 또는 서버 재시작으로 반영할 수 있습니다.
