# minecraft-blocklog-plugin

## 간단한 요약

블록 파괴/설치 이력을 SQLite 데이터베이스에 기록하고, 특정 위치 주변의 최근 변경 내역을 조회(`/lookup`)하거나 특정 플레이어가 최근에 한 변경을 되돌리는(`/rollback`) 그리핑 대응용 플러그인입니다.

## 설명

- **기록** (`BlockLogListener`): `BlockBreakEvent`와 `BlockPlaceEvent`를 감지해, 플레이어 UUID/닉네임, 월드, 좌표(x, y, z), 동작 종류(`BREAK`/`PLACE`), 변경 전/후 블록 타입, 타임스탬프를 `BlockLogPlugin.logChangeAsync`로 넘겨 비동기로 SQLite에 `INSERT`합니다. 파괴는 `이전 타입 → AIR`, 설치는 `이전 타입(event.blockReplacedState) → 새 타입`으로 기록됩니다.
- **저장소**: 데이터 폴더의 `blocklog.db` 파일에 SQLite로 저장하며, `onEnable()`에서 `block_log` 테이블을 없으면 생성합니다(id, player_uuid, player_name, world, x, y, z, action, before_type, after_type, timestamp). shadowJar가 Kotlin은 자체 패키지로 relocate하지만 `org.sqlite`는 relocate하지 않는데, sqlite-jdbc의 JNI 네이티브 라이브러리가 원래 패키지 경로로 고정 컴파일되어 있어 옮기면 `UnsatisfiedLinkError`가 나기 때문입니다(코드 주석 기준).
- **조회** (`/lookup`, `LookupCommand` → `BlockLogPlugin.lookupAsync`): 실행한 플레이어의 현재 위치를 기준으로, 지정한 반경(정사각형, x/z 각각 ± radius) 안에서 지정한 분(minutes) 이내에 발생한 변경을 최신순으로 최대 50건 비동기 조회해 채팅으로 보여줍니다. 결과가 없으면 "기록이 없습니다"를 출력합니다.
- **롤백** (`/rollback`, `RollbackCommand` → `BlockLogPlugin.rollbackAsync`): 지정한 플레이어 닉네임이 최근 지정한 분 이내에 남긴 기록을 최신순으로 모두 조회한 뒤, 메인 스레드에서 각 좌표의 블록을 `before_type`(변경 전 블록)으로 되돌립니다. 월드를 찾을 수 없거나 `before_type` 문자열이 유효한 `Material`이 아니면 그 건은 건너뜁니다. 반경 제한은 없고 해당 플레이어의 전체 최근 변경을 대상으로 합니다. 되돌린 뒤에는 몇 건이 적용됐는지 채팅으로 알려줍니다.

다른 플러그인에 대한 의존성은 없습니다.

## 사용 방법 (매뉴얼)

### 명령어

| 명령어 | 설명 |
| --- | --- |
| `/lookup` | 현재 위치 기준 반경 10블록, 최근 60분 이내의 블록 변경 내역을 최신순으로 최대 50건 조회합니다(기본값). |
| `/lookup <반경>` | 반경만 지정하고 분은 기본값(60분)을 사용합니다. |
| `/lookup <반경> <분>` | 반경과 조회 기간(분)을 모두 지정합니다. |
| `/rollback <닉네임> <분>` | 지정한 플레이어가 최근 `<분>`분 이내에 남긴 블록 변경을 모두 변경 전 상태로 되돌립니다. |

`/lookup`은 플레이어만 실행할 수 있습니다(콘솔 사용 불가, 현재 위치가 기준점이기 때문). `/rollback`은 닉네임과 분 인자가 모두 숫자로 파싱되어야 하며, 둘 중 하나라도 없으면 사용법 안내만 출력합니다.

### 권한 노드

- `blocklog.rollback` (기본값: OP) — `/lookup`과 `/rollback` 둘 다 이 권한을 요구합니다(`LookupCommand`, `RollbackCommand` 모두 `permission()`이 `"blocklog.rollback"`을 반환). 조회와 롤백에 별도 권한이 나뉘어 있지 않다는 점에 주의하세요.

### config.yml 설정 항목

이 플러그인에는 `config.yml`이 없습니다. 조회 반경/기간 기본값(반경 10블록, 60분)과 조회 결과 상한(50건)은 `BlockLogPlugin.kt`와 `LookupCommand.kt`에 코드로 고정되어 있으며, 명령어 인자로만 그때그때 조정할 수 있습니다.

### 빌드 방법

저장소 루트에서 다음 명령어를 실행합니다.

```bash
./scripts/build-plugin.sh minecraft-blocklog-plugin
```

빌드된 jar(`build/libs/*-all.jar`)가 `data/plugins/`로 복사됩니다. 서버에 반영하려면 `./scripts/console.sh reload confirm`을 실행하거나 서버를 재시작하세요. 다른 플러그인 의존성이 없으므로 별도 사전 빌드 없이 바로 빌드할 수 있습니다.
