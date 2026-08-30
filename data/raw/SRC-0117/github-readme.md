# Leaderboard Plugin

## 간단한 요약

플레이어들의 바닐라 통계(플레이타임, 몹 처치 수, 사망 횟수 등)를 순위표로 조회할 수 있는 Paper 플러그인입니다. `/top <항목>` 명령어 하나로 서버 전체(오프라인 플레이어 포함) 상위 10명을 보여줍니다.

## 설명

- 마인크래프트 바닐라가 이미 추적하고 있는 `org.bukkit.Statistic` 값을 그대로 조회해서 순위를 매기는 "조회/표시 계층"입니다. 플러그인이 직접 이벤트를 리스닝해서 카운터를 쌓지 않습니다.
- 현재 지원하는 항목과 매핑된 바닐라 Statistic은 다음과 같습니다 (`LeaderboardPlugin.kt`의 `LEADERBOARD_STATS`).

  | 항목 키 | 바닐라 Statistic | 설명 |
  | --- | --- | --- |
  | `playtime` | `Statistic.PLAY_ONE_MINUTE` | 누적 플레이타임 (분 단위로 환산해 표시) |
  | `kills` | `Statistic.MOB_KILLS` | 몹 처치 수 |
  | `deaths` | `Statistic.DEATHS` | 사망 횟수 |
  | `jumps` | `Statistic.JUMP` | 점프 횟수 |
  | `damage` | `Statistic.DAMAGE_DEALT` | 가한 피해량 |

- 순위 계산 로직(`TopCommand`):
  1. `Bukkit.getOfflinePlayers()`로 서버에 한 번이라도 접속한 적 있는(`hasPlayedBefore()`) 모든 플레이어(온라인/오프라인 무관)를 대상으로 합니다.
  2. 각 플레이어의 `OfflinePlayer#getStatistic(statistic)` 값을 조회합니다.
  3. 값이 0보다 큰 플레이어만 남기고, 값 기준 내림차순 정렬 후 상위 10명만 표시합니다.
  4. `playtime` 항목은 원시 tick 값을 분 단위(`value / 20 / 60`)로 환산해서 보여주고, 나머지 항목은 원시 값을 그대로 표시합니다.
  5. 명령어가 호출될 때마다 즉시(실시간) 계산합니다 — 별도의 주기적 캐시나 백그라운드 재계산 로직은 없습니다.
- 기획 문서(`docs/plugin-ideas/24-leaderboard.md`)는 "5분마다 재계산하는 캐시" 방식을 제안하지만, 실제 구현에는 캐시가 없고 매 요청마다 전체 오프라인 플레이어 목록을 순회해 계산합니다.

## 사용 방법 (매뉴얼)

### 명령어

| 명령어 | 설명 |
| --- | --- |
| `/top <항목>` | 지정한 항목의 상위 10명 순위를 보여줍니다. `<항목>`은 `playtime`, `kills`, `deaths`, `jumps`, `damage` 중 하나이며, 입력 시 자동완성(Tab)으로 후보가 제안됩니다. |

- `<항목>`을 생략하거나 지원하지 않는 값을 입력하면 `사용법: /top <playtime|kills|deaths|jumps|damage>` 형태의 안내 메시지가 출력됩니다.
- 아직 아무도 해당 통계 값을 기록하지 않았다면 `아직 기록이 없습니다.` 메시지가 출력됩니다.
- 명령어는 Paper의 Brigadier 기반 `BasicCommand`로 구현되어 있으며, `plugin.yml`(`commands:` 섹션)이 아니라 `LeaderboardPlugin.onEnable()`에서 `registerCommand("top", TopCommand())`로 코드 등록됩니다.

### 권한 노드

`TopCommand`는 `permission()`을 별도로 오버라이드하지 않습니다. 즉 **권한 노드가 지정되어 있지 않으며, 콘솔을 포함해 누구나 `/top` 명령어를 사용할 수 있습니다.**

### config.yml

이 플러그인에는 `config.yml`이 없습니다. 별도의 설정 파일 없이 동작합니다.

### 빌드 방법

저장소 루트에서 다음 명령을 실행합니다.

```bash
./scripts/build-plugin.sh minecraft-leaderboard-plugin
```
