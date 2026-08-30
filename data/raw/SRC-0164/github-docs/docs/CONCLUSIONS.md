# 벤치마크 종합 결론

> 측정 조건: 1M 행, composite index `(col_a, col_b)`, warm cache, 7회 측정 / 3회 warmup
> 대상: PG 13/15/17, MySQL 5.7/8.0/8.4
> 변형: tuple_in (V1), dnf_or (V2), values_join (V3), any_array (V4, PG only)

---

## 1. 핵심 발견: 가장 빠른 변형은 무엇인가?

### PostgreSQL (13/15/17 공통)

| 순위 | 변형 | Plan | n=100 p50 | n=500 p50 | n=1000 p50 | I/O (n=500) |
|------|------|------|-----------|-----------|------------|-------------|
| 🥇 1 | **values_join** | Nested Loop + Index Scan | 0.054~0.066ms | 0.25~0.30ms | 0.49~0.59ms | 1,500 blk |
| 🥈 2 | tuple_in | Bitmap Heap Scan | 0.11~0.13ms | 1.18~1.76ms | 5.9~6.4ms | 1,500 blk |
| 🥈 2 | dnf_or | Bitmap Heap Scan | 0.11~0.13ms | 1.36~1.73ms | 5.1~5.7ms | 1,500 blk |
| ❌ 4 | any_array | Seq Scan (!) | 70~80ms | 69~77ms | 72~77ms | **9,346 blk** |

**핵심 인사이트:**
- `VALUES JOIN`이 PG에서 **모든 튜플 수에서 최적**. Nested Loop + Index Scan이 bitmap보다 효율적.
- tuple_in과 dnf_or은 **동일 plan (BitmapOr)**, 성능도 거의 동일 — 옵티마이저가 내부적으로 동등하게 처리.
- **`= ANY(ARRAY[ROW(...)])`는 절대 사용 금지** — PG가 인덱스를 전혀 활용하지 못하고 seq scan으로 퇴화.

### MySQL (5.7/8.0/8.4)

| 순위 | 변형 | Plan | n=100 p50 (8.4) | n=500 p50 (8.4) | I/O (n=500) |
|------|------|------|-----------------|-----------------|-------------|
| 🥇 1 | **tuple_in** | Range (idx_ab) | 0.045ms | 0.224ms | 7,009 |
| 🥇 1 | **dnf_or** | Range (idx_ab) | 0.045ms | 0.242ms | 7,009 |
| ❌ 3 | values_join | **ALL (Full Scan!)** | 0.079ms | 0.407ms | **14,023** |

**핵심 인사이트:**
- MySQL에서 tuple_in과 dnf_or은 동등 최적 (range scan on idx_ab).
- **MySQL에서 VALUES JOIN (derived table JOIN)은 인덱스를 못 탐** — Full Table Scan으로 I/O 2배 소모.
- MySQL 8.0/8.4는 5.7 대비 10~15배 빠름 (같은 plan이지만 내부 실행 효율 차이).

---

## 2. 옵티마이저의 Cost Estimation은 정확한가?

| DB | 실제 최적 | 옵티마이저가 고른 최저 cost | 일치? |
|----|-----------|---------------------------|-------|
| PG (모든 버전) | values_join | tuple_in/dnf_or (cost=155) | ❌ **불일치** |
| MySQL 8.0/8.4 | tuple_in/dnf_or | values_join (cost=49) | ❌ **불일치** |
| MySQL 5.7 | values_join (낮은 n) | values_join (cost=166) | ✅ 일치 |

**발견:**
- PG에서 values_join은 cost가 더 높게 계산됨(265 vs 155)에도 불구하고 실제로는 2~10배 빠름.
  → Nested Loop의 per-loop startup cost를 과대평가하는 경향.
- MySQL에서는 values_join의 cost가 가장 낮지만 실제로는 Full Scan이라 느림.
  → derived table에 대한 cost 추정이 부정확.

**결론: Cost estimate만으로 최적 변형을 판단할 수 없다. 실측이 필수.**

---

## 3. I/O 리소스 소모 비교

### PG — 동일 I/O, 다른 실행 시간

| 변형 | I/O Blocks (n=500) | p50 ms | 해석 |
|------|-------------------|--------|------|
| values_join | 1,500 | 0.25ms | Index Scan → 정확한 블록만 접근 |
| tuple_in | 1,500 | 1.58ms | Bitmap → 블록은 같지만 bitmap merge 오버헤드 |
| dnf_or | 1,500 | 1.73ms | 동일 bitmap, OR 분해 오버헤드 |
| any_array | **9,356** | 69ms | Seq Scan → 전체 테이블 읽기 |

**같은 I/O 블록 수임에도 values_join이 6배 빠른 이유:**
- Nested Loop + Index Scan은 각 튜플에 대해 직접 인덱스 탐색 (O(n × log(N)))
- Bitmap scan은 먼저 모든 조건의 bitmap을 생성한 후 OR merge 후 heap fetch — merge 단계에서 CPU 오버헤드 발생

### MySQL — values_join의 I/O 폭증

| 변형 | I/O Blocks (n=500) | Plan |
|------|-------------------|------|
| tuple_in/dnf_or | 7,009 | range (인덱스) |
| values_join | **14,023** | ALL (풀스캔) |

MySQL에서 derived table JOIN은 옵티마이저가 인덱스를 활용하지 못해 I/O가 2배로 폭증.

---

## 4. 스케일링 특성 (n 증가에 따른 성능 퇴화)

| DB | 변형 | n=10→1000 증가율 | 특성 |
|----|------|-----------------|------|
| PG17 | values_join | ×62 | **선형** (가장 안정) |
| PG17 | tuple_in | ×457 | **초선형** (bitmap merge cost 증가) |
| PG17 | dnf_or | ×523 | **초선형** (OR 분해→bitmap merge) |
| PG17 | any_array | ×2 | 이미 느려서 증가율 낮음 (always seq scan) |
| MySQL 8.4 | tuple_in | ×89 | **선형** |
| MySQL 8.4 | dnf_or | ×99 | **선형** |
| MySQL 8.4 | values_join | ×87 | **선형** (full scan이라 비례) |

**PG에서 tuple_in/dnf_or의 초선형 증가:**
- BitmapOr 노드가 N개의 BitmapIndexScan을 merge하는 비용이 O(N²)에 가까워짐
- values_join의 Nested Loop는 각 루프가 독립적이라 순수 O(N)

---

## 5. 실무 권고 (최종)

### PostgreSQL

1. **IN 조건이 많을 때 (n > 50): `VALUES JOIN`을 사용하라**
   ```sql
   -- 최적
   SELECT t.* FROM target t
   JOIN (VALUES (1::bigint, 2::bigint), (3, 4), ...) AS v(a, b)
   ON t.col_a = v.a AND t.col_b = v.b
   ```

2. **IN 조건이 적을 때 (n ≤ 50): tuple_in이나 dnf_or 모두 무관**
   - 성능 차이 무시 가능 (0.05ms 이하)

3. **절대 `= ANY(ARRAY[ROW(...)])`를 사용하지 마라**
   - PG가 row comparison에 인덱스를 활용 못함 → Seq Scan

### MySQL

1. **`(A, B) IN (...)` 또는 `OR` 사용 — 둘 다 최적**
   ```sql
   -- 둘 다 range scan on idx_ab — 동등 최적
   WHERE (col_a, col_b) IN ((1,2), (3,4))
   WHERE (col_a=1 AND col_b=2) OR (col_a=3 AND col_b=4)
   ```

2. **VALUES JOIN (derived table JOIN) 사용 금지**
   - MySQL 옵티마이저가 derived table에 대해 인덱스를 활용하지 못함
   - Full Table Scan + I/O 2배

### 공통

- 옵티마이저의 cost estimate를 맹신하지 마라 — EXPLAIN ANALYZE 실측 필수
- 복합 인덱스 컬럼 순서: 고카디널리티 컬럼을 선행에 배치
- n ≤ 1000 범위에서는 plan 퇴화(seq scan으로 전환) 없음 (1M 행 기준)

---

## 6. DB별 Plan 메커니즘 요약

| | PostgreSQL | MySQL |
|--|-----------|-------|
| tuple_in plan | BitmapOr(BitmapIndexScan × N) → BitmapHeapScan | Range scan (index range union) |
| dnf_or plan | 동일 (옵티마이저가 tuple_in으로 변환) | 동일 Range scan |
| values_join plan | **Nested Loop + Index Scan** (최적!) | **ALL (Full Scan!)** (비최적) |
| any_array plan | **Seq Scan** (비최적!) | N/A |
| 최적 변형 | **values_join** | **tuple_in / dnf_or** |

---

## 7. 한계 및 후속 연구

- 데이터 규모 1M 행 (10M 행에서 재검증 필요 — plan 전환점이 다를 수 있음)
- Cold cache 미측정 (warm only)
- MySQL 5.7은 ARM 에뮬레이션이라 절대 시간은 참고용
- Prepared statement 환경에서의 차이 미검증
- PG `enable_bitmapscan=off` 상태에서의 강제 Nested Loop 비교 미수행
