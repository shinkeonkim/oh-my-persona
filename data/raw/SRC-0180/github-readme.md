# Address Extractor (주소 추출기)

[도로명 주소](https://business.juso.go.kr/addrlink/attrbDBDwld/attrbDBDwldList.do?cPath=99MD&menu=%EC%A3%BC%EC%86%8CDB#this)를 통해 얻을 수 있는 전체 목록에서 시도명/시군구명을 추출합니다.

## 📋 개요

한국의 도로명 주소 전체 데이터베이스에서 시/도와 구/시 정보를 추출하여 CSV 파일로 생성합니다.

**출력 파일**: `addresses.csv` (id, region, city)

## 🛠 개발환경 설정

### 요구사항
- Python 3.12
- uv (Python 패키지 매니저)

### 설치

```bash
# 의존성 설치
uv sync
```

## 🚀 사용방법

### 로컬 실행

#### 1. 주소 데이터 다운로드 및 추출
```bash
uv run main.py --reload
```
- 도로명 주소 압축 파일을 자동으로 다운로드
- 데이터를 추출하여 `addresses.csv` 생성

#### 2. 기존 데이터로 추출
```bash
uv run main.py
```
- 이미 다운로드된 `address_txt_files` 디렉토리의 파일 사용
- `addresses.csv` 생성

### GitHub Actions 자동화

GitHub Actions를 통해 자동으로 최신 주소 데이터를 가져와 CSV 파일을 업데이트할 수 있습니다.

#### 워크플로우 실행

1. GitHub 리포지토리의 **Actions** 탭으로 이동
2. 왼쪽 사이드바에서 **"Update Addresses CSV"** 워크플로우 선택
3. 오른쪽 상단의 **"Run workflow"** 버튼 클릭
4. 브랜치 선택 (기본: main)
5. **"Run workflow"** 버튼 클릭하여 실행

#### 자동화 프로세스

- 최신 도로명 주소 데이터 다운로드
- 시/도 및 구/시 정보 추출
- `addresses.csv` 생성
- 변경사항이 있으면 자동 커밋 및 푸시
- 커밋 메시지: `chore: Update addresses CSV file`

## 📄 출력 파일 형식

### addresses.csv
```csv
id,region,city
1,강원특별자치도,강릉시
2,강원특별자치도,고성군
3,강원특별자치도,동해시
...
```

## 📦 주요 의존성

- `requests` - HTTP 다운로드용
