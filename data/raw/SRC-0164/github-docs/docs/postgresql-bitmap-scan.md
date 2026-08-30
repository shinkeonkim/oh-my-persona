# PostgreSQL Bitmap Scan 동작 원리 — 왜 여러 인덱스를 동시에 활용할 수 있는가

## 개요

PostgreSQL은 하나의 쿼리에서 **여러 개의 서로 다른 인덱스를 동시에 사용**하여 결과를 합칠 수 있습니다.
이것이 가능한 핵심 메커니즘이 **Bitmap Scan**입니다.

MySQL을 포함한 다른 DBMS에서 "서로 다른 컬럼에 대한 OR 조건은 인덱스를 못 탄다"는
제약이 PostgreSQL에서는 존재하지 않는 이유가 바로 이 구조에 있습니다.

---

## 1. 스캔 유형 비교: Index Scan vs Bitmap Scan

### Index Scan (전통적 방식)

```
인덱스 → TID 하나 꺼냄 → 테이블 페이지 방문 → 다음 TID → 또 방문 → ...
```

- 인덱스에서 TID(Tuple ID = 페이지번호 + 오프셋)를 하나씩 꺼내서
- 즉시 해당 테이블 페이지를 방문
- **문제**: 결과가 여러 페이지에 흩어져 있으면 random I/O가 많아짐

### Bitmap Scan (PG 고유)

```
1단계: 인덱스 → 조건에 맞는 TID 전부 수집 → 메모리에 "비트맵" 생성
2단계: 비트맵을 페이지 순서로 정렬
3단계: 테이블을 페이지 순서대로 방문 (sequential-like)
```

- 먼저 인덱스를 완전히 스캔하여 **어떤 페이지를 방문해야 하는지** 목록을 만듦
- 그 후 물리적 페이지 순서대로 테이블을 읽음
- **장점**: random I/O를 sequential I/O로 변환

---

## 2. BitmapOr — 여러 인덱스를 합치는 핵심

Bitmap Scan의 진짜 강점은 **여러 인덱스의 비트맵을 합칠 수 있다**는 점입니다.

### 동작 흐름

```
쿼리:
  WHERE (date_1='2024-03-15' AND bool_1=TRUE)     ← idx_pair_1 사용
     OR (date_5='2024-07-01' AND bool_5=TRUE)     ← idx_pair_5 사용
     OR (date_12='2024-11-20' AND bool_12=TRUE)   ← idx_pair_12 사용
```

```
실행 계획:

BitmapHeapScan on bench_target
  → BitmapOr
      → BitmapIndexScan on idx_pair_1   → 비트맵 A 생성
      → BitmapIndexScan on idx_pair_5   → 비트맵 B 생성
      → BitmapIndexScan on idx_pair_12  → 비트맵 C 생성

      비트맵 A OR 비트맵 B OR 비트맵 C = 최종 비트맵

  → 최종 비트맵의 페이지만 순서대로 방문하여 행 반환
```

### 단계별 상세

#### 1단계: 각 BitmapIndexScan

각 조건에 해당하는 인덱스를 스캔합니다.
인덱스는 B-tree이므로 조건에 맞는 리프 노드만 빠르게 탐색합니다.

결과는 "이 조건에 해당하는 행이 테이블의 어떤 페이지에 있는가"를 **비트맵**으로 표현합니다.

```
비트맵 A (idx_pair_1에서 date_1='2024-03-15' AND bool_1=TRUE):
  페이지 42: [행 3, 행 7]
  페이지 156: [행 1]
  페이지 891: [행 12, 행 15]
```

#### 2단계: BitmapOr — 비트맵 합치기

여러 비트맵을 OR 연산으로 합칩니다.
"A 또는 B 또는 C에 해당하는 페이지" 목록이 됩니다.

```
비트맵 A:  페이지 {42, 156, 891}
비트맵 B:  페이지 {12, 42, 500}
비트맵 C:  페이지 {200, 891}

최종 OR:   페이지 {12, 42, 156, 200, 500, 891}  ← 6개 페이지만 방문
```

이 OR 연산은 순수 메모리 내 비트 연산이므로 매우 빠릅니다.

#### 3단계: BitmapHeapScan — 테이블 읽기

최종 비트맵에 표시된 페이지만, **물리적 순서대로** 방문합니다.
각 페이지를 읽을 때 원래 조건을 recheck하여 실제 매칭 행만 반환합니다.

```
페이지 12 방문 → 조건 recheck → 매칭 행 반환
페이지 42 방문 → 조건 recheck → 매칭 행 반환
페이지 156 방문 → ...
...
```

---

## 3. 비트맵의 내부 구조 (TID Bitmap)

PostgreSQL의 비트맵은 `src/backend/nodes/tidbitmap.c`에 구현되어 있습니다.

### 두 가지 해상도

| 모드 | 저장 단위 | 정밀도 | 메모리 사용 |
|------|-----------|--------|-------------|
| **Exact** | 페이지 내 개별 행(offset) | 정확한 행 위치 | 높음 |
| **Lossy** | 페이지 단위 (전체 표시) | "이 페이지 어딘가" | 낮음 |

- 처음에는 **Exact 모드**: 페이지 번호 + 해당 페이지 내 행 오프셋을 비트로 기록
- 메모리가 부족하면 **Lossy 모드로 전환**: 페이지만 기록하고 행 오프셋은 버림

### Lossy 전환 메커니즘

```c
// tidbitmap.c (간략화)
if (tbm->nentries > tbm->maxentries) {
    tbm_lossify(tbm);  // 일부 페이지를 lossy로 전환하여 메모리 절약
}
```

- `work_mem` 설정이 비트맵 크기의 상한을 결정
- 비트맵이 `work_mem`을 초과하면 가장 많은 행을 가진 페이지부터 lossy로 전환
- Lossy 페이지는 방문 시 페이지 전체를 읽고 조건을 recheck (약간의 낭비)

### 메모리 효율

- 8KB 페이지 기준, **64GB 테이블 전체를 약 1MB의 비트맵**으로 표현 가능 (lossy 모드)
- 대부분의 실무 쿼리에서 비트맵은 수십~수백 KB 수준

---

## 4. 왜 MySQL은 이것을 못하는가

### MySQL의 Index Merge Union

MySQL도 "여러 인덱스를 합치는" 기능이 있습니다: **Index Merge Union**.

```sql
-- MySQL에서 Index Merge가 동작하는 경우:
WHERE col_a = 1 OR col_b = 2
-- → idx_a와 idx_b를 각각 스캔 후 결과를 merge
```

그러나 핵심 제약이 있습니다:

### MySQL Index Merge의 제약

1. **각 OR 브랜치가 하나의 인덱스로 완전히 해결 가능해야 함**
2. 복합 조건 `(date_1='X' AND bool_1=TRUE)` OR `(date_5='Y' AND bool_5=TRUE)`에서:
   - 첫 브랜치는 `idx_pair_1`로 해결 가능 ✓
   - 두 번째 브랜치는 `idx_pair_5`로 해결 가능 ✓
   - **그러나 MySQL 옵티마이저는 이 구조를 Index Merge 후보로 인식하지 못함** ✗

3. MySQL은 "WHERE 절 전체를 하나의 인덱스로 해결할 수 있는가?"를 먼저 판단합니다.
   서로 다른 컬럼에 대한 OR이면 어떤 단일 인덱스도 전체를 커버하지 못하므로,
   **옵티마이저가 포기하고 Full Table Scan을 선택**합니다.

### 근본적 차이

| | PostgreSQL | MySQL |
|--|-----------|-------|
| 비트맵 중간 구조 | 있음 (TID Bitmap) | 없음 |
| 여러 인덱스 결과 합치기 | BitmapOr/BitmapAnd (범용) | Index Merge (제한적) |
| OR이 다른 컬럼에 걸칠 때 | 각 인덱스 스캔 → 비트맵 합치기 | Full Table Scan |
| 메모리 사용 | work_mem으로 제한, lossy 전환 | N/A |
| 실행 순서 | 비트맵 생성 → 페이지 순서 방문 | 인덱스별 즉시 row fetch |

---

## 5. BitmapOr의 비용 모델

PostgreSQL 플래너는 Bitmap Scan의 비용을 다음과 같이 추정합니다:

### 비용 구성요소

```
총 비용 = Σ(각 인덱스 스캔 비용) + 비트맵 OR 비용 + 테이블 페이지 읽기 비용
```

- **인덱스 스캔 비용**: B-tree 탐색 비용 (로그 비례)
- **비트맵 OR 비용**: CPU 비용 (메모리 내 비트 연산, 거의 무시 가능)
- **테이블 읽기 비용**: 방문할 페이지 수 × `random_page_cost` (또는 `seq_page_cost`)
  - Bitmap Scan은 페이지를 순서대로 방문하므로 `seq_page_cost`에 가까워짐

### Sequential I/O 효과

일반 Index Scan이 random I/O인 반면, Bitmap Scan은:

```
페이지 방문 순서:  12 → 42 → 156 → 200 → 500 → 891
                  (물리적 순서, OS read-ahead 활용 가능)
```

디스크가 HDD라면 이 차이가 극적이고, SSD에서도 sequential prefetch 효과가 있습니다.

---

## 6. 플래너의 Bitmap Scan 선택 기준

PostgreSQL 플래너는 다음 상황에서 Bitmap Scan을 선택합니다:

| 조건 | Index Scan 선호 | Bitmap Scan 선호 |
|------|----------------|-----------------|
| 결과 행 수 | 소수 (< 수십 행) | 중간 (수십~수만 행) |
| 결과 분포 | 한 곳에 집중 | 여러 페이지에 분산 |
| OR 조건 | 없거나 같은 인덱스 | 다른 인덱스에 걸침 |
| 메모리 | 충분 | `work_mem` 범위 내 |

Seq Scan을 선택하는 경우:
- 결과가 테이블의 대부분(>10~20%)일 때
- 테이블이 매우 작을 때

---

## 7. 실제 EXPLAIN 출력 해석

우리 벤치마크에서의 실제 Plan:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, payload FROM bench_target
WHERE (date_1 = '2024-03-15' AND bool_1 = TRUE)
   OR (date_5 = '2024-07-01' AND bool_5 = TRUE)
   OR (date_12 = '2024-11-20' AND bool_12 = TRUE);
```

```
Bitmap Heap Scan on bench_target
  Recheck Cond: (((date_1 = '2024-03-15') AND (bool_1 = true))
             OR ((date_5 = '2024-07-01') AND (bool_5 = true))
             OR ((date_12 = '2024-11-20') AND (bool_12 = true)))
  Heap Blocks: exact=6
  Buffers: shared hit=22
  →  BitmapOr
       →  Bitmap Index Scan on idx_pair_1
            Index Cond: ((date_1 = '2024-03-15') AND (bool_1 = true))
       →  Bitmap Index Scan on idx_pair_5
            Index Cond: ((date_5 = '2024-07-01') AND (bool_5 = true))
       →  Bitmap Index Scan on idx_pair_12
            Index Cond: ((date_12 = '2024-11-20') AND (bool_12 = true))
```

해석:
- `Bitmap Index Scan` × 3: 각 인덱스에서 조건에 맞는 TID 수집
- `BitmapOr`: 세 비트맵을 OR로 합침
- `Bitmap Heap Scan`: 합쳐진 비트맵의 페이지만 방문
- `Heap Blocks: exact=6`: 총 6개 페이지만 방문 (10만 행 중)
- `Buffers: shared hit=22`: 총 22 블록 I/O (인덱스 + 힙)
- `Recheck Cond`: 페이지에서 행을 읽을 때 조건을 다시 확인 (lossy 대비)

---

## 8. UNION ALL과의 비교

UNION ALL도 동등한 성능을 보이는 이유:

```
Append
  →  Index Scan on idx_pair_1   (date_1 = '...' AND bool_1 = true)
  →  Index Scan on idx_pair_5   (date_5 = '...' AND bool_5 = true)
  →  Index Scan on idx_pair_12  (date_12 = '...' AND bool_12 = true)
```

- 각 SELECT가 독립적으로 인덱스를 사용
- 결과를 단순히 이어붙임 (Append)
- Bitmap 생성/합치기 오버헤드가 없는 대신, 페이지 방문이 순서대로가 아닐 수 있음

**결과적으로 BitmapOr과 Append + IndexScan은 거의 동등한 성능**을 보입니다.
PG 플래너는 비용 추정에 따라 둘 중 하나를 선택합니다.

---

## 9. 요약

| 개념 | 설명 |
|------|------|
| TID Bitmap | 테이블 행의 물리적 위치를 비트로 표현한 메모리 내 자료구조 |
| BitmapIndexScan | 인덱스를 스캔하여 TID Bitmap을 생성 |
| BitmapOr | 여러 비트맵을 OR 연산으로 합침 (마찬가지로 BitmapAnd는 AND) |
| BitmapHeapScan | 합쳐진 비트맵에 표시된 페이지만 순서대로 방문 |
| Lossy 모드 | 메모리 부족 시 행 단위→페이지 단위로 해상도를 낮춤 |
| work_mem | 비트맵 최대 크기를 결정하는 설정 |

**PostgreSQL이 "여러 인덱스를 합칠 수 있는" 근본적인 이유:**
B-tree 인덱스의 결과를 **즉시 행을 가져오는 대신**, 중간에 **비트맵이라는 추상 계층**을
두어서, 여러 인덱스의 결과를 비트 연산으로 합치고, 그 후에 한 번에 테이블을 읽기 때문입니다.

---

## 참고 자료

- [PostgreSQL 공식 문서 — Combining Multiple Indexes](https://www.postgresql.org/docs/current/indexes-bitmap-scans.html)
- [PostgreSQL 소스 — tidbitmap.c](https://doxygen.postgresql.org/tidbitmap_8c_source.html) (TID Bitmap 구현)
- [PostgreSQL 소스 — nodeBitmapOr.c](https://doxygen.postgresql.org/nodeBitmapOr_8c_source.html) (BitmapOr 실행 노드)
- [PostgreSQL 소스 — nodeBitmapIndexscan.c](https://doxygen.postgresql.org/nodeBitmapIndexscan_8c_source.html)
- [MySQL Index Merge Optimization](https://dev.mysql.com/doc/refman/8.0/en/index-merge-optimization.html) (비교용)
