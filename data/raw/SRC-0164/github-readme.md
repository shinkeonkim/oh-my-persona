# db-union-query-benchmark

서로 다른 컬럼 쌍에 걸친 조건을 조회할 때, **IN / OR / UNION ALL** 중 어떤 SQL 형태가
복합 인덱스를 가장 잘 활용하는지 실측하는 벤치마크 프로젝트입니다.

## 문제 상황

```sql
-- 50개의 (date_N, bool_N) 컬럼 쌍, 각 쌍에 복합 인덱스 존재
-- 여러 쌍에 걸쳐 조회해야 할 때, 어떤 방식이 최적인가?

-- 방법 1: OR
WHERE (date_1='2024-03-15' AND bool_1=TRUE)
   OR (date_5='2024-07-01' AND bool_5=TRUE)

-- 방법 2: UNION ALL
SELECT ... WHERE date_1='2024-03-15' AND bool_1=TRUE
UNION ALL
SELECT ... WHERE date_5='2024-07-01' AND bool_5=TRUE

-- 방법 3: Tuple IN (쌍별)
WHERE (date_1, bool_1) IN (('2024-03-15', TRUE))
   OR (date_5, bool_5) IN (('2024-07-01', TRUE))
```

## 결론 요약

| DB | OR 조건 | UNION ALL | Tuple IN |
|----|---------|-----------|----------|
| **PostgreSQL** 13/15/17 | ✅ 인덱스 사용 | ✅ 인덱스 사용 | ✅ 인덱스 사용 |
| **MySQL** 5.7/8.0/8.4 | ❌ Full Scan | ✅ 인덱스 사용 | ❌ Full Scan |

- **PostgreSQL**: BitmapOr로 여러 인덱스를 합쳐서 처리 → 어떤 방식이든 무관
- **MySQL**: 서로 다른 컬럼에 걸친 OR을 index merge로 처리 못함 → **UNION ALL 필수**

> 상세 분석: [`docs/CONCLUSIONS.md`](docs/CONCLUSIONS.md)
> PostgreSQL BitmapOr 동작 원리: [`docs/postgresql-bitmap-scan.md`](docs/postgresql-bitmap-scan.md)

## Quick Start

```bash
# 전체 초기화 + 벤치마크 실행
./run_benchmark.sh --clean

# 또는 단계별로:
docker compose up -d --build
./run_benchmark.sh

# 대시보드 확인
open http://localhost:8000/static/dashboard.html
```

### 옵션

```bash
./run_benchmark.sh              # 시드(있으면 skip) + 벤치마크 실행
./run_benchmark.sh --clean      # 전체 초기화 후 실행
./run_benchmark.sh --clean-only # 초기화만 (벤치마크 안 함)
./run_benchmark.sh --status     # 현재 결과 수 확인

# 환경 변수로 설정 조절
SCALE=500000 MEASURE_RUNS=30 ./run_benchmark.sh --clean
```

## 테이블 구조

```
bench_target (
    id BIGSERIAL PRIMARY KEY,
    date_1 DATE, bool_1 BOOLEAN,   -- 쌍 1 + 복합 인덱스 (date_1, bool_1)
    date_2 DATE, bool_2 BOOLEAN,   -- 쌍 2 + 복합 인덱스 (date_2, bool_2)
    ...
    date_50 DATE, bool_50 BOOLEAN, -- 쌍 50 + 복합 인덱스 (date_50, bool_50)
    payload TEXT
)
```

- 각 행에는 **하나의 쌍에만 값이 있고** 나머지는 NULL (sparse column 패턴)
- 각 쌍에 `(date_N, bool_N)` 복합 인덱스 존재
- 쿼리는 항상 `bool_N = TRUE`로 조회

## 측정 항목

| 항목 | 설명 |
|------|------|
| 실행 시간 (p50/p95/p99) | EXPLAIN ANALYZE 서버사이드 시간 |
| I/O 블록 수 | 버퍼 히트 + 디스크 읽기 |
| 실행 Plan | access type, 사용 인덱스, 노드 구조 |
| Planning time | 쿼리 최적화 소요 시간 (PG) |

## 아키텍처

```
┌─────────────────────────────────────────────────────┐
│ FastAPI (runner + dashboard)                         │
│  POST /run     → seed + benchmark 일괄 실행         │
│  POST /explain → EXPLAIN ANALYZE 수집               │
│  GET  /results → 결과 조회                          │
│  GET  /static/dashboard.html → 분석 리포트          │
└──────────────────────┬──────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
   PG 13/15/17    MySQL 5.7/8.0/8.4   (각 버전별 컨테이너)
   Docker Compose, CPU/mem limit 고정
```

## 프로젝트 구조

```
├── run_benchmark.sh         # 실행 스크립트 (--clean, --status)
├── docker-compose.yml       # PG 3버전 + MySQL 3버전 + FastAPI
├── configs/
│   ├── postgres/postgresql.conf
│   └── mysql/my.cnf, my57.cnf
├── db/schema/               # DDL (50쌍 컬럼 + 50개 복합 인덱스)
├── app/
│   ├── routes/run_all.py    # seed + benchmark 통합 엔드포인트
│   ├── adapters/            # PG/MySQL EXPLAIN 수집 + 정규화
│   ├── scenarios/           # 시나리오 생성 + 쿼리 빌더
│   └── measure/             # 측정 프로토콜 (warmup/반복/통계)
├── web/dashboard.html       # 분석 리포트 대시보드
├── results/                 # SQLite 결과 저장
└── docs/
    ├── CONCLUSIONS.md       # 벤치마크 결론
    └── postgresql-bitmap-scan.md  # PG BitmapOr 동작 원리 문서
```

## 측정 조건

- 데이터: 10만~50만 행, 50개 컬럼 쌍, 각 행에 1개 쌍만 값 존재
- 인덱스: 각 쌍에 `(date_N, bool_N)` 복합 인덱스
- 측정: warm cache, warmup 3회 → 측정 10회, p50/p95/p99 + σ
- 쿼리: 1~50개 쌍에 걸쳐 `date_N = 특정날짜 AND bool_N = TRUE` 조회
- 비교: IN (쌍별) / OR / UNION ALL — 동일 결과셋 보장

## License

MIT

## Author

[@shinkeonkim](https://github.com/shinkeonkim)
