# minecraft-jobs-plugin

## 간단한 요약

농부/광부/낚시꾼/사냥꾼 4개 직업을 갖고 레벨업·전직(승급)·퀘스트·패시브/액티브 능력까지 성장시키는 작은 RPG형 직업 시스템입니다. 직업 행동(수확/채굴/낚시/사냥)마다 경험치와 재화를 지급하며, 재화 지급/차감은 `minecraft-economy-plugin`의 `EconomyApi`에 의존합니다.

## 설명

### 직업과 진행도

- 직업은 `JobType`(FARMER/MINER/FISHERMAN/HUNTER)으로 정의되며, 한 번에 하나만 활성화할 수 있습니다(`JobsPlugin.activeJobs`).
- 직업별 진행도(`PlayerJobRecord`: 레벨, 경험치, 전직 단계 `tier`, 퀘스트 진행도, 누적 획득 재화)는 UUID+직업 키로 계속 보관되어, 직업을 바꿔도 사라지지 않고 나중에 돌아오면 이어서 성장합니다. 다만 패시브/액티브 효과는 항상 "현재 활성 직업" 것만 적용됩니다.
- 처음 직업을 갖는 것은 무료지만, 이미 다른 직업이 있는 상태에서 직업을 바꾸는 것은 "전직"으로 취급되어 `JOB_CHANGE_COST`(200.0)의 재화 비용이 듭니다.

### 행동 감지 (Listener)

각 직업 전용 리스너가 관련 이벤트를 감지해 `JobsPlugin.grantProgress(player, type)`를 호출합니다. 현재 활성 직업과 다르면 아무 일도 일어나지 않습니다.

- `FarmerListener` — 작물 수확
- `MinerListener` — `BlockBreakEvent`에서 광석 종류 블록(코얼~고대 잔해 등)을 캤을 때
- `FishermanListener` — 낚시 성공
- `HunterListener` — 몬스터 처치

### 레벨과 보상

`grantProgress` 호출마다:
- `moneyPerActionFor(level)`(기본 2.0 + 레벨×0.05)만큼 재화를 즉시 지급하고, `bonusChanceFor(tier, level)` 확률로 2배 지급합니다.
- 경험치를 `BASE_EXP_PER_ACTION`(5)만큼 쌓고, `expThresholdForLevel(level)`(레벨×100)을 넘으면 레벨업합니다.
- 전직 단계별 퀘스트(예: 1차는 20회, 2차는 50회, 3차는 100회 행동 누적 — `TIER_QUEST_TARGET`)를 아직 완료하지 않았다면 진행도가 함께 쌓이고, 목표에 도달하면 `TIER_QUEST_REWARD`(1/2/3차 각 100/300/600)를 지급합니다.

### 전직(승급)과 패시브/액티브 능력 — 전직 단계뿐 아니라 레벨로도 계속 강해짐

전직 단계는 최대 `MAX_TIER`(3)까지이며, `/job promote`로 다음 단계 요구 레벨(`TIER_LEVEL_REQUIREMENT`: 2차 레벨 10, 3차 레벨 25)을 만족하고 비용(`TIER_PROMOTION_COST`: 2차 200.0, 3차 500.0)을 지불하면 승급합니다. 전직 단계마다 `JobAbility.kt`의 `JOB_ABILITIES`에 정의된 패시브 포션 효과(예: 광부 2차 HASTE, 3차 HASTE+NIGHT_VISION)와, 최고 단계(3차)부터는 쿨다운 있는 액티브 능력(`/job ability`, 쿨다운 5분)이 해금됩니다.

여기서 그치지 않고, **레벨이 오를 때마다 같은 전직 단계 안에서도 능력이 계속 강해집니다**(`JobConstants.kt`):
- `bonusChanceFor(tier, level)` = 전직 단계 기본 확률(`TIER_BONUS_CHANCE`: 1/2/3차 0%/20%/40%) + `레벨 × 0.004`(레벨 보너스는 최대 0.30까지, 합계는 최대 0.9까지) — 즉 보너스(2배 지급) 확률이 레벨에 비례해 계속 오릅니다.
- `moneyPerActionFor(level)` = 기본 2.0 + `레벨 × 0.05` — 행동 1회당 지급액도 레벨에 비례해 계속 오릅니다.
- `levelAmplifierBonus(level)` = `(레벨 / 15).coerceAtMost(3)` — 15레벨마다 패시브/액티브 포션 효과의 증폭(amplifier) 단계가 1씩 올라가고 최대 +3까지 쌓입니다. `effectivePassives`/`effectiveActiveEffects`가 이 증폭값을 전직 단계의 기본 효과에 더해서 실제 적용값을 계산합니다. 레벨업으로 이 증폭 구간을 막 넘는 순간에는 현재 걸려 있는 패시브도 `refreshAbilities`로 즉시 재계산되어 그 자리에서 더 강해집니다.

패시브 효과는 접속/전직/직업 변경/직업 포기 시점에 `refreshAbilities`로 다시 계산되어 적용되며(포션 효과는 재접속하면 사라지므로 접속할 때도 다시 겁니다), 직업을 포기하면 모두 사라집니다.

### GUI

인자 없이 `/job`만 입력하면 `JobsGui.kt`의 `buildJobsGui`가 만드는 9칸 인벤토리 GUI가 열립니다. 직업별 아이콘(밀/철곡괭이/낚싯대/철검)을 클릭하면 가입/전직이 되고, 경험치·전직 단계·전직 단계별 혜택표·레벨 보너스 적용 현황을 lore로 보여주며, 승급 아이템과 액티브 능력 발동 아이템, 직업 포기(배리어) 아이템도 함께 배치됩니다. `JobsGuiListener`가 클릭을 가로채 `JobsPlugin`의 `joinJob`/`promote`/`leaveJob`/`useActiveAbility`를 그대로 호출하므로, 로직은 전부 `JobsPlugin`에 있고 GUI는 그 위에 얹힌 화면일 뿐입니다.

### economy-plugin 의존

`JobsPlugin.onEnable()`에서 `server.servicesManager.getRegistration(EconomyApi::class.java)`로 `minecraft-economy-plugin`이 등록한 `EconomyApi`를 찾아옵니다. 찾지 못하면(=economy-plugin이 먼저 로드되지 않았으면) 이 플러그인을 즉시 비활성화합니다. `paper-plugin.yml`에도 `EconomyPlugin`을 `load: BEFORE`, `required: true`로 명시해 로드 순서를 강제합니다. 행동 보상 지급(`deposit`), 전직/전직 비용 차감(`withdraw`)에 이 API를 사용합니다.

### 테스트

`src/test`에 MockBukkit 기반 테스트(`JobsPluginTest`)가 있으며, 전직 단계별 패시브 효과가 함께/올바르게 적용·해제되는지, 레벨 증폭 구간을 넘으면 즉시 효과가 강해지는지, 레벨업만으로 보상·보너스 확률이 계속 오르는지 등을 검증합니다.

## 사용 방법 (매뉴얼)

### 명령어

| 명령어 | 설명 |
| --- | --- |
| `/job` | 인자 없이 실행하면 직업 GUI를 엽니다. |
| `/job join <직업>` | 지정한 직업으로 가입(무료) 또는 전직(비용 200.0)합니다. 직업명은 `FARMER`/`MINER`/`FISHERMAN`/`HUNTER` (대소문자 무관). |
| `/job info` | 현재 활성 직업의 레벨/경험치/전직 단계/퀘스트 진행/누적 재화와 현재 적용 중인 혜택을 확인합니다. |
| `/job promote` | 현재 활성 직업을 다음 전직 단계로 승급합니다(레벨/비용 조건 필요). |
| `/job leave` | 현재 직업을 그만둡니다(진행도는 보존되지만 능력은 사라집니다). |
| `/job ability` | 액티브 능력을 발동합니다(3차 전직부터 가능, 쿨다운 5분). |

### 권한 노드

소스 코드(`JobsPlugin`, `JobCommand`, `paper-plugin.yml`) 어디에도 별도의 권한(permission) 등록이 없습니다. `/job`과 그 하위 명령 전부 권한 제한 없이 모든 플레이어가 사용할 수 있습니다.

### config.yml 설정 항목

별도의 `config.yml`은 없습니다. 직업/레벨/전직/퀘스트 관련 수치는 모두 `JobConstants.kt`에 코드로 고정되어 있고(`JOB_CHANGE_COST`, `MAX_TIER`, `TIER_LEVEL_REQUIREMENT`, `TIER_PROMOTION_COST`, `TIER_BONUS_CHANCE`, `TIER_QUEST_TARGET`/`TIER_QUEST_REWARD`, `LEVEL_BONUS_CHANCE_PER_LEVEL` 등), 능력 정의는 `JobAbility.kt`의 `JOB_ABILITIES`에 있습니다. 데이터 폴더에는 진행도가 저장되는 `jobs.yml`이 자동 생성됩니다.

### 빌드 방법

이 플러그인은 컴파일 시점에 `minecraft-economy-plugin`의 plain jar(`../minecraft-economy-plugin/build/libs/economy-plugin-0.1.0.jar`)를 직접 참조합니다. 먼저 economy-plugin 디렉터리에서 plain jar를 만들어두세요.

```bash
cd plugins-dev/minecraft-economy-plugin
./gradlew jar
```

그다음 저장소 루트에서 이 플러그인을 빌드합니다.

```bash
./scripts/build-plugin.sh minecraft-jobs-plugin
```

빌드된 jar(`build/libs/*-all.jar`)가 `data/plugins/`로 복사됩니다. 서버에 반영하려면 `./scripts/console.sh reload confirm`을 실행하거나 서버를 재시작하세요. 서버에는 economy-plugin이 먼저 활성화되어 있어야 합니다(`paper-plugin.yml`의 `load: BEFORE` 의존성).
