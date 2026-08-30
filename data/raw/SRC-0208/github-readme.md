# Hackathon Django Template

Django 템플릿 프로젝트입니다.
REST API, JWT 인증, Celery, PostgreSQL, Redis 등을 포함한 완전한 백엔드 개발 환경을 제공합니다.

## 프로젝트 구성

### 디렉토리별 역할

- **`webapp/`**: Django 프로젝트의 메인 디렉토리
  - **`api/`**: REST API 엔드포인트 (v1 버전)
    - `health_check/`: 헬스체크 API
    - `users/`: 사용자 관련 API
  - **`common/`**: 공통 모듈
    - `exceptions/`: 커스텀 예외 처리
    - `middlewares/`: 커스텀 미들웨어 (CamelCase 변환 등)
    - `models/`: 기본 모델 (이를 상속하여 사용합니다.)
    - `pagination/`: 페이지네이션 설정
    - `views/`: 기본 뷰 클래스 (이를 상속하여 사용합니다.)
  - **`config/`**: Django 설정
    - `settings/`: 환경별 설정 파일 (base, development, production, alpha)
  - **`users/`**: 사용자 모델 및 관리

- **`environments/`**: 환경별 Docker 설정
  - **`development/`**: 개발 환경
    - `commands/`: 개발용 스크립트 (migrate, test, shell 등)
    - `Dockerfile`: 개발용 Docker 이미지
    - `nginx/`: Nginx 설정
  - **`alpha/`**: 알파 환경
  - **`production/`**: 프로덕션 환경

- **`.github/workflows/`**: GitHub Actions 워크플로우
  - `CI.yml`: 테스트 실행
  - `generate_coverage_report.yml`: 커버리지 리포트 생성
  - `create_swagger_file.yml`: Swagger 문서 생성

### docker / docker-compose 관련 구성

- **`docker-compose.yml`**: 개발 환경용 (기본)
- **`docker-compose.alpha.yml`**: 알파 환경용
- **`docker-compose.production.yml`**: 프로덕션 환경용

**주요 서비스:**
- **webapp**: Django 애플리케이션 (포트 8080)
- **nginx**: 리버스 프록시 (포트 8000 또는 80으로 개발환경에 맞게 설정)
- **postgres**: PostgreSQL 데이터베이스 (포트 5432)
- **redis**: Redis 캐시/브로커 (포트 6379)
- **celery-worker**: Celery 워커
- **celery-beat**: Celery 스케줄러
- **flower**: Celery 모니터링 (포트 5555)

## 세팅 방법

### 1. uv sync

```bash
# uv 설치 (macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 의존성 설치
uv sync
```

### 2. pre-commit install

```bash
# pre-commit 설치 및 설정
uv run pre-commit install
```

### 3. ./tool.sh 활용

```bash
# 개발 도구 스크립트 실행
./tool.sh
```

**사용 가능한 명령어:**
- **슈퍼유저 생성**: Django 관리자 계정 생성
- **마이그레이션 생성**: 모델 변경사항을 마이그레이션 파일로 생성
- **마이그레이션 적용**: 데이터베이스에 마이그레이션 적용
- **Django Shell 접속**: Django 쉘에서 모델 조작
- **테스트 실행**: 단위 테스트 실행
- **로그 스트리밍**: 실시간 로그 확인
- **Docker 명령어**: 컨테이너 빌드/시작/중지

### 4. .env 설정

프로젝트 루트에 `.env.sample` 파일을 복사하여 아름을 .env로 변경한 후 환경변수를 설정하세요

### 5. base.py 내의 SERVICE_NAME 변경

`webapp/config/settings/base.py` 파일에서 다음 부분을 수정하세요:

```python
SERVICE_NAME = "YOUR_SERVICE_NAME"  # TEMPLATE_SERVICE에서 변경
```

### 6. Github Actions를 위한 secrets 설정

GitHub 저장소의 Settings > Secrets and variables > Actions에서 다음 시크릿을 설정하세요:

- **`CI_DJANGO_KEY`**: Django SECRET_KEY
- **`CI_POSTGRES_PASSWORD`**: PostgreSQL 비밀번호
- **`GH_TOKEN`**: GitHub 토큰 (커버리지/스웨거 문서 푸시용)

## 주요 기능

- **REST API**: Django REST Framework 기반
- **JWT 인증**: dj-rest-auth + Simple JWT
- **소셜 로그인**: Kakao 로그인 지원
- **API 문서화**: drf-spectacular (Swagger/OpenAPI)
- **비동기 작업**: Celery + Redis
- **데이터베이스**: PostgreSQL + psqlextra
- **캐싱**: Redis
- **관리자 페이지**: Django Unfold (모던한 UI)
- **코드 품질**: Ruff, MyPy, Bandit
- **테스트**: Coverage 리포트 자동 생성
- **CamelCase 변환**: 자동 JSON 필드명 변환

## 개발 시작하기

```bash
# 1. 의존성 설치
uv sync

# 2. 환경변수 설정
cp .env.sample .env  # .env 파일 생성 후 수정

# 3. Docker 컨테이너 시작
./tool.sh  # 선택: 7) docker-compose up -d --build

# 4. 마이그레이션 적용
./tool.sh  # 선택: 3) 마이그레이션 적용

# 5. 슈퍼유저 생성
./tool.sh  # 선택: 1) 슈퍼유저 생성

# 6. 애플리케이션 접속
# http://localhost:8000 - API
# http://localhost:8000/admin - 관리자 페이지
# http://localhost:5555 - Celery 모니터링
```

## API 엔드포인트

- **헬스체크**: `GET /api/v1/health/`
- **사용자 API**: `GET /api/v1/users/`
- **API 문서**: `GET /`
