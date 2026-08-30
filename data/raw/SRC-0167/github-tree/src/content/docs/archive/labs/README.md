---
title: "Terraform Associate (004) 실습 가이드"
description: "Legacy study material imported from labs/README.md"
pagefind: false
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📚 개요

실제 Terraform 환경에서 hands-on 실습을 통해 시험에 필요한 기술을 익힙니다. 각 실습은 특정 시험 도메인과 연결되어 있으며, 실무에서도 활용 가능한 시나리오로 구성되어 있습니다.

## 실습 환경 준비

### 필수 사항
- Terraform 1.12 이상
- AWS/Azure/GCP 계정 (무료 티어 가능)
- 텍스트 에디터 (VS Code 권장)
- Git

### Terraform 설치
```bash
# macOS
brew install terraform

# Linux
wget https://releases.hashicorp.com/terraform/1.12.0/terraform_1.12.0_linux_amd64.zip
unzip terraform_1.12.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Windows (Chocolatey)
choco install terraform

# 설치 확인
terraform version
```

### VS Code 확장 프로그램 (권장)
- HashiCorp Terraform
- Terraform Autocomplete

---

## 실습 과정 구조

각 실습은 다음 구조를 따릅니다:

```
lab-XX-topic/
├── README.md          # 실습 가이드
├── instructions/      # 단계별 지시사항
├── solution/          # 완성된 솔루션
├── starter/           # 시작 템플릿 (선택)
└── validation/        # 검증 스크립트 (선택)
```

---

## 실습 목록

### 🟢 Level 1: 기초 (Week 1-3)

#### [Lab 01: 첫 번째 Terraform 프로젝트](/archive/labs/lab-01-first-project/readme/)
**학습 목표:**
- Terraform 설치 및 초기화
- 간단한 리소스 생성
- Core Workflow 이해

**실습 내용:**
- AWS S3 Bucket 생성
- `init → plan → apply → destroy` 워크플로우
- State 파일 이해

**소요 시간:** 30분  
**도메인:** Core Workflow (16%)

---

#### [Lab 02: Variables와 Outputs](/archive/labs/lab-02-variables-outputs/readme/)
**학습 목표:**
- Input Variables 정의 및 사용
- Outputs를 통한 정보 출력
- Variable 타입 이해

**실습 내용:**
- 재사용 가능한 S3 Bucket 구성
- Variables로 환경별 구성 관리
- Outputs로 생성된 리소스 정보 출력

**소요 시간:** 45분  
**도메인:** Terraform Configuration (26%)

---

#### [Lab 03: Data Sources 활용](/archive/labs/lab-03-data-sources/readme/)
**학습 목표:**
- Resource vs Data Source 이해
- 기존 리소스 참조
- Cross-resource references

**실습 내용:**
- Data Source로 최신 AMI 조회
- 기존 VPC 참조
- EC2 인스턴스 생성

**소요 시간:** 45분  
**도메인:** Terraform Configuration (26%)

---

### 🟡 Level 2: 중급 (Week 4-6)

#### [Lab 04: count와 for_each](/archive/labs/lab-04-count-for-each/readme/)
**학습 목표:**
- count 메타-인수 활용
- for_each로 안전한 리소스 관리
- 두 방식의 차이점 이해

**실습 내용:**
- count로 여러 S3 Bucket 생성
- for_each로 인스턴스 생성 (map 사용)
- 리소스 제거 시 동작 비교

**소요 시간:** 60분  
**도메인:** Terraform Configuration (26%)

---

#### [Lab 05: 첫 번째 Module 만들기](/archive/labs/lab-05-first-module/readme/)
**학습 목표:**
- Module 구조 이해
- 재사용 가능한 Module 작성
- Module Input/Output

**실습 내용:**
- VPC Module 생성
- Root Module에서 VPC Module 호출
- Module Output 참조

**소요 시간:** 90분  
**도메인:** Terraform Modules (10%)

---

#### [Lab 06: Remote State 설정](/archive/labs/lab-06-remote-state/readme/)
**학습 목표:**
- Local State → Remote State 마이그레이션
- State Locking 이해
- Backend 구성

**실습 내용:**
- S3 Backend 설정
- DynamoDB를 통한 State Locking
- State 마이그레이션

**소요 시간:** 60분  
**도메인:** State Management (16%)

---

#### [Lab 07: Lifecycle Meta-Arguments](/archive/labs/lab-07-lifecycle/readme/)
**학습 목표:**
- create_before_destroy 활용
- prevent_destroy로 리소스 보호
- ignore_changes로 특정 변경 무시

**실습 내용:**
- 무중단 배포 시뮬레이션
- 중요 리소스 삭제 방지
- 외부 변경 무시 설정

**소요 시간:** 75분  
**도메인:** Terraform Configuration (26%)

---

### 🔴 Level 3: 고급 (Week 7-8)

#### [Lab 08: Custom Conditions (004 신규)](/archive/labs/lab-08-custom-conditions/readme/)
**학습 목표:**
- Variable Validation 작성
- Preconditions/Postconditions 활용
- Check Blocks 사용

**실습 내용:**
- AMI ID 검증
- 인스턴스 상태 확인
- 인프라 Health Check

**소요 시간:** 90분  
**도메인:** Terraform Configuration (26%)

---

#### [Lab 09: Dynamic Blocks](/archive/labs/lab-09-dynamic-blocks/readme/)
**학습 목표:**
- Dynamic Blocks 문법
- 반복 블록 동적 생성
- Complex types 활용

**실습 내용:**
- Security Group 규칙 동적 생성
- 여러 ingress 규칙 관리
- Variable로 규칙 정의

**소요 시간:** 75분  
**도메인:** Terraform Configuration (26%)

---

#### [Lab 10: State 조작 마스터](/archive/labs/lab-10-state-manipulation/readme/)
**학습 목표:**
- terraform import 실습
- terraform state mv/rm 활용
- Drift 감지 및 해결

**실습 내용:**
- 기존 인프라 Import
- 리소스 이름 변경
- 수동 변경 감지

**소요 시간:** 90분  
**도메인:** State Management (16%), Maintain Infrastructure (10%)

---

#### [Lab 11: Module Registry 활용](/archive/labs/lab-11-module-registry/readme/)
**학습 목표:**
- Terraform Registry 탐색
- Public Module 사용
- Module 버전 관리

**실습 내용:**
- AWS VPC Module (terraform-aws-modules/vpc/aws) 사용
- 버전 제약 설정
- Module 소스 다양화

**소요 시간:** 60분  
**도메인:** Terraform Modules (10%)

---

#### [Lab 12: HCP Terraform 워크플로우](/archive/labs/lab-12-hcp-terraform/readme/)
**학습 목표:**
- HCP Terraform 계정 생성
- VCS 연동 Workspace 설정
- Remote Execution

**실습 내용:**
- HCP Terraform 무료 계정 생성
- GitHub 연동
- Variable Sets 구성
- Run Triggers 설정

**소요 시간:** 120분  
**도메인:** HCP Terraform (6%)

---

## 실습 진행 가이드

### 1. 순차적 학습 (권장)
```
Lab 01 → Lab 02 → Lab 03 → ... → Lab 12
```
- 각 실습은 이전 실습의 개념을 기반으로 함
- 기초부터 차근차근 진행

### 2. 도메인별 학습
특정 도메인을 집중 학습하고 싶다면:

**Terraform Configuration (26%):**
- Lab 02, 03, 04, 07, 08, 09

**State Management (16%):**
- Lab 06, 10

**Terraform Modules (10%):**
- Lab 05, 11

**Core Workflow (16%):**
- Lab 01

**HCP Terraform (6%):**
- Lab 12

### 3. 시험 직전 복습
시험 1주일 전:
- Lab 01 (Core Workflow 재확인)
- Lab 02 (Variables/Outputs 재확인)
- Lab 04 (count/for_each 차이)
- Lab 06 (Remote State)
- Lab 10 (State 조작)

---

## 실습 검증 방법

각 실습 후 다음을 확인하세요:

### 1. Plan 검증
```bash
$ terraform plan
# No changes 또는 예상된 변경사항만 표시
```

### 2. Apply 성공
```bash
$ terraform apply
Apply complete! Resources: X added, 0 changed, 0 destroyed.
```

### 3. State 확인
```bash
$ terraform state list
# 생성된 리소스 목록 확인

$ terraform state show <resource>
# 리소스 상세 정보 확인
```

### 4. Outputs 확인
```bash
$ terraform output
# 정의한 outputs 출력 확인
```

### 5. 실제 인프라 확인
- AWS Console에서 리소스 확인
- CLI로 리소스 존재 확인
```bash
aws s3 ls
aws ec2 describe-instances
```

---

## 비용 관리

### 무료 티어 활용
- AWS: S3, t2.micro EC2 (750시간/월)
- Azure: B1S VM, Storage
- GCP: f1-micro, 5GB Cloud Storage

### 실습 후 정리 필수
```bash
# 모든 리소스 삭제
$ terraform destroy

# 확인
$ terraform state list
# (empty)
```

### 비용 추적
```bash
# AWS Cost Explorer 확인
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

---

## 문제 해결 (Troubleshooting)

### 일반적인 오류

#### 1. Provider 다운로드 실패
```bash
Error: Failed to query available provider packages

# 해결:
$ terraform init -upgrade
```

#### 2. State Lock 오류
```bash
Error: Error locking state

# 해결:
$ terraform force-unlock <LOCK_ID>
```

#### 3. 리소스가 이미 존재
```bash
Error: Resource already exists

# 해결:
$ terraform import <resource_type>.<name> <id>
```

#### 4. Permission Denied
```bash
Error: UnauthorizedOperation

# 해결: AWS credentials 확인
$ aws sts get-caller-identity
$ aws configure
```

### 디버깅
```bash
# 상세 로그 활성화
$ export TF_LOG=DEBUG
$ export TF_LOG_PATH=./terraform.log

$ terraform apply
```

---

## 추가 학습 리소스

### HashiCorp Learn
- [Get Started with Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started)
- [Terraform Language](https://developer.hashicorp.com/terraform/language)

### Community
- [HashiCorp Discuss](https://discuss.hashicorp.com/)
- [Terraform GitHub](https://github.com/hashicorp/terraform)
- [r/Terraform](https://www.reddit.com/r/Terraform/)

### 실무 예제
- [Terraform AWS Modules](https://github.com/terraform-aws-modules)
- [Gruntwork Terraform](https://gruntwork.io/repos/)
- [CloudPosse Terraform Modules](https://github.com/cloudposse)

---

## 실습 체크리스트

- [ ] Lab 01: 첫 번째 Terraform 프로젝트
- [ ] Lab 02: Variables와 Outputs
- [ ] Lab 03: Data Sources 활용
- [ ] Lab 04: count와 for_each
- [ ] Lab 05: 첫 번째 Module 만들기
- [ ] Lab 06: Remote State 설정
- [ ] Lab 07: Lifecycle Meta-Arguments
- [ ] Lab 08: Custom Conditions
- [ ] Lab 09: Dynamic Blocks
- [ ] Lab 10: State 조작 마스터
- [ ] Lab 11: Module Registry 활용
- [ ] Lab 12: HCP Terraform 워크플로우

---

**실습을 통해 진정한 Terraform 전문가가 되시길 바랍니다! 🚀**

## 다음 단계
- [Lab 01: 첫 번째 Terraform 프로젝트](/archive/labs/lab-01-first-project/readme/) 시작하기
- [예상 문제 풀이](/archive/practice-exams/readme/)로 이론 점검
