# Job Extractor

Work24 API를 통해 직업 카테고리 및 직업 데이터를 추출하여 CSV 파일로 생성하는 프로젝트입니다.

## 📋 개요

이 프로젝트는 Work24 공공 API를 호출하여 한국의 직업 분류 체계를 가져와 다음 두 가지 CSV 파일을 생성합니다:
- `job_categories.csv`: 직업 카테고리 목록
- `jobs.csv`: 직업 목록

## 🛠 개발환경 설정

### 요구사항
- Python 3.12
- uv (Python 패키지 매니저)

### 설치

1. **리포지토리 클론**
```bash
git clone <repository-url>
cd job_extractor
```

2. **의존성 설치**
```bash
uv sync
```

3. **환경 변수 설정**

`.env` 파일을 생성하고 Work24 API 인증키를 설정합니다:
```bash
WORK24_AUTH_KEY=your_actual_api_key_here
```

## 🚀 사용방법

### 로컬 실행

```bash
uv run extract_jobs.py
```

실행이 완료되면 프로젝트 루트에 다음 파일들이 생성됩니다:
- `job_categories.csv` - 직업 카테고리 데이터 (id, name)
- `jobs.csv` - 직업 데이터 (id, name, job_category_name)

### GitHub Actions 자동화

GitHub Actions를 통해 자동으로 CSV 파일을 업데이트할 수 있습니다.

#### 1. GitHub Secrets 설정

1. GitHub 리포지토리의 **Settings** → **Secrets and variables** → **Actions**로 이동
2. **New repository secret** 클릭
3. Name: `WORK24_AUTH_KEY`
4. Secret: Work24 API 인증키 입력
5. **Add secret** 클릭

#### 2. 워크플로우 실행

1. GitHub 리포지토리의 **Actions** 탭으로 이동
2. 왼쪽 사이드바에서 **"Update Job Categories and Jobs CSV"** 워크플로우 선택
3. 오른쪽 상단의 **"Run workflow"** 버튼 클릭
4. 브랜치 선택 (기본: main)
5. **"Run workflow"** 버튼 클릭하여 실행

#### 3. 결과 확인

- Actions 탭에서 워크플로우 실행 상태 및 로그 확인
- 변경사항이 있는 경우 자동으로 커밋되어 main 브랜치에 푸시됨
- 커밋 메시지: `chore: Update job categories and jobs CSV files`
- 변경사항이 없는 경우 커밋 생략

## 📦 주요 의존성

- `requests` - HTTP API 호출
- `python-dotenv` - 환경 변수 관리

## 📄 출력 파일 형식

### job_categories.csv
```csv
id,name
11,의회의원·고위공무원 및 기업 고위임원
12,행정·경영·금융·보험 관리자
...
```

### jobs.csv
```csv
id,name,job_category_name
1,기업고위임원,의회의원·고위공무원 및 기업 고위임원
2,행정부고위공무원,의회의원·고위공무원 및 기업 고위임원
...
```
