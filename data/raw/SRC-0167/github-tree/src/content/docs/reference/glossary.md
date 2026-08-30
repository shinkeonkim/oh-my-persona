---
title: 한영 용어집 / Korean-English Glossary
description: Canonical English Terraform terms paired with concise Korean explanations.
---

| English term | 한국어 설명 | 시험에서 구분할 것 |
|---|---|---|
| configuration | 구성 | `.tf` 파일 전체와 실제 인프라는 다름 |
| desired state | 목표 상태 | Terraform configuration이 선언하는 상태 |
| real-world object | 실제 객체 | cloud API가 관리하는 resource instance |
| provider | 프로바이더 | Terraform Core와 원격 API 사이 plugin |
| resource | 관리 리소스 | 생성·변경·삭제의 대상 |
| data source | 데이터 소스 | 외부 또는 기존 정보를 읽는 대상 |
| state | 상태 | 주소와 실제 객체 binding 및 metadata |
| backend | 백엔드 | state 저장과 관련 동작의 구현 |
| state locking | 상태 잠금 | 동시 쓰기로 인한 손상 방지 |
| drift | 드리프트 | 구성 밖에서 실제 객체가 변경된 차이 |
| plan | 실행 계획 | 현재 상태에서 목표 상태로 가는 제안 변경 |
| apply | 적용 | 계획된 변경을 실행하고 state 갱신 |
| root module | 루트 모듈 | 명령을 실행하는 최상위 구성 |
| child module | 자식 모듈 | 다른 module block이 호출한 모듈 |
| input variable | 입력 변수 | module의 명시적 입력 계약 |
| output value | 출력 값 | module이 호출자에게 노출하는 값 |
| implicit dependency | 암시적 의존성 | expression의 참조로 생기는 graph edge |
| explicit dependency | 명시적 의존성 | `depends_on`으로 추가하는 숨은 의존성 |
| unknown value | 미확정 값 | plan 시점에 apply 후 결정되는 값 |
| sensitive value | 민감 값 | 출력이 가려지지만 저장 자체를 막지 않을 수 있음 |
| ephemeral value | 일시 값 | 지원 문맥에서 state/plan 저장을 피하는 값 |
| workspace | 워크스페이스 | 문맥에 따라 CLI state instance 또는 HCP 실행 단위 |
| project | 프로젝트 | HCP Terraform workspace 조직화·권한 경계 |
