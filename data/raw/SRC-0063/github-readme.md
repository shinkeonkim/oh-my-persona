# 깜빡이 - Django 기반 REST API 백엔드

## 프로젝트 구성

### 디렉토리별 역할

- **`webapp/`**: Django 프로젝트의 메인 디렉토리
  - **`config/`**: Django 설정 및 URL 라우팅
    - `settings/`: 환경별 설정 파일 (base, development, production, alpha, test)
    - `urls.py`: 메인 URL 라우터
    - `celery.py`: Celery 비동기 작업 설정
    - `asgi.py` / `wsgi.py`: 서버 배포 설정

  - **`common/`**: 공통 모듈 (재사용 가능한 컴포넌트)
    - `exceptions/`: 커스텀 예외 처리 (BaseAPIException, 에러 코드 등)
    - `middlewares/`: 커스텀 미들웨어 (CamelCase 변환)
    - `models/`: 기본 모델 (BaseModel - 모든 모델이 상속)
    - `views/`: 기본 뷰 클래스 (BaseAPIView, BaseViewSet)
    - `permissions/`: 커스텀 권한 클래스 (ActiveUserPermission)
    - `pagination/`: 페이지네이션 설정
    - `utils/`: 유틸리티 함수 (datetime 등)
    - `admin/`: 관리자 페이지 유틸리티
    - `responses/`: 표준 응답 포맷
    - `choices/`: 전역 선택지 열거형

  - **`api/`**: REST API 엔드포인트 (버전별)
    - **`v1/`**: API v1 버전
      - `health_check/`: 헬스체크 API
      - `users/`: 사용자 인증 및 관리 API
      - `games/`: 게임 목록 및 세션 관리 API
      - `reports/`: 레포트 생성 및 조회 API

  - **`users/`**: 사용자 모델 및 관리
    - `models/`: User, Child, BotToken 모델
    - `admin/`: 사용자 관리자 페이지 커스터마이징
    - `validators.py`: 사용자 데이터 검증
    - `choices/`: 사용자 관련 선택지

  - **`games/`**: 게임 관리
    - `models/`: Game, GameSession, GameResult, RankingEntry 모델
    - `admin/`: 게임 관리자 페이지
    - `serializers.py`: 게임 데이터 직렬화
    - `views.py`: 게임 뷰 및 랭킹 표시
    - `choices/`: 게임 관련 선택지

  - **`reports/`**: 레포트 생성 및 관리 (가장 복잡한 앱)
    - `models/`: Report, GameReport, GameReportAdvice, ReportPin 모델
    - `services/`: 비즈니스 로직 서비스
      - `report_generation_service.py`: 레포트 생성 오케스트레이션
      - `game_report_generation_service.py`: 게임별 레포트 생성
      - `report_email_service.py`: 이메일 발송 서비스
      - `base_pdf_generator.py`: PDF 생성 베이스 클래스
    - `llm/`: LLM 통합 (AI 기반 조언 생성)
      - `generator.py`: LLM 레포트 생성 로직
      - `prompt.py`: LLM 프롬프트 템플릿
      - `provider.py`: LLM 제공자 인터페이스
    - `tasks/`: Celery 비동기 작업
      - `report_task.py`: 레포트 생성 작업
      - `report_email_task.py`: 이메일 발송 작업
    - `admin/`: 레포트 관리자 페이지
    - `authentication.py`: 레포트 접근 인증
    - `management/commands/`: Django 관리 명령어

  - **`static/`**: 정적 파일 (CSS, JS, 이미지)
  - **`staticfiles/`**: 수집된 정적 파일 (프로덕션용)
  - **`media/`**: 미디어 파일 (생성된 PDF 등)

- **`environments/`**: 환경별 Docker 설정
  - **`development/`**: 개발 환경
    - `commands/`: 개발용 스크립트 (migrate, test, shell 등)
    - `Dockerfile`: 개발용 Docker 이미지
  - **`alpha/`**: 알파 환경
  - **`production/`**: 프로덕션 환경

- **`.github/workflows/`**: GitHub Actions 워크플로우
  - `CI.yml`: 테스트 실행
  - `generate_coverage_report.yml`: 커버리지 레포트 생성
  - `create_swagger_file.yml`: Swagger 문서 생성

### docker / docker-compose 관련 구성

- **`docker-compose.yml`**: 개발 환경용 (기본)

**주요 서비스:**
- **webapp**: Django 애플리케이션 (포트 8000)
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

### 5. Github Actions를 위한 secrets 설정

GitHub 저장소의 Settings > Secrets and variables > Actions에서 다음 시크릿을 설정하세요:

- **`CI_DJANGO_KEY`**: Django SECRET_KEY
- **`CI_POSTGRES_PASSWORD`**: PostgreSQL 비밀번호
- **`GH_TOKEN`**: GitHub 토큰 (커버리지/스웨거 문서 푸시용)

## 주요 기능

- **REST API**: Django REST Framework 기반
- **JWT 인증**: dj-rest-auth + Simple JWT
- **API 문서화**: drf-spectacular (Swagger/OpenAPI)
- **비동기 작업**: Celery + Redis
- **데이터베이스**: PostgreSQL + psqlextra
- **캐싱**: Redis
- **관리자 페이지**: Django Unfold (모던한 UI)
- **코드 품질**: Ruff, MyPy, Bandit
- **테스트**: Coverage 레포트 자동 생성
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

### 문서 및 스키마

- **Swagger UI**: `GET /` - 인터랙티브 API 문서
- **OpenAPI 스키마**: `GET /schema/` - OpenAPI 3.0 스키마 JSON
- **ReDoc**: `GET /redoc/` - 대체 API 문서 (ReDoc 스타일)

### 1. 헬스체크 (Health Check)

**Base Path**: `/api/v1/health-check/`

- `GET /api/v1/health-check/` - 애플리케이션 헬스 상태 확인 (인증 불필요)

### 2. 사용자 (Users)

**Base Path**: `/api/v1/users/`

#### 인증 및 계정 관리 (dj-rest-auth)

- `POST /api/v1/users/login/` - 로그인
- `POST /api/v1/users/logout/` - 로그아웃 (인증 필요)
- `POST /api/v1/users/password/reset/` - 비밀번호 재설정 요청
- `POST /api/v1/users/password/reset/confirm/` - 비밀번호 재설정 확인
- `POST /api/v1/users/password/change/` - 비밀번호 변경 (인증 필요)
- `GET/PUT/PATCH /api/v1/users/user/` - 사용자 정보 조회/수정 (인증 필요)
- `POST /api/v1/users/token/verify/` - JWT 토큰 검증
- `POST /api/v1/users/token/refresh/` - JWT 토큰 갱신

#### 회원가입

- `POST /api/v1/users/registration/` - 회원가입
- `POST /api/v1/users/registration/verify-email/` - 이메일 인증
- `POST /api/v1/users/registration/resend-email/` - 이메일 인증 재발송

#### 커스텀 사용자 엔드포인트

- `GET /api/v1/users/check-username/` - 사용자명 중복 확인 (인증 불필요)
- `PATCH /api/v1/users/email/` - 이메일 변경 (인증 필요)
- `GET /api/v1/users/child/` - 자녀 정보 조회 (인증 필요)
- `POST /api/v1/users/child/` - 자녀 정보 등록/수정 (인증 필요)

### 3. 게임 (Games)

**Base Path**: `/api/v1/games/`

#### 게임 목록

- `GET /api/v1/games/` - 활성 게임 목록 조회

#### 뿅뿅 아기별 (BB Star)

- `POST /api/v1/games/bb-star/start/` - 게임 세션 시작
- `POST /api/v1/games/bb-star/finish/` - 게임 세션 종료 및 결과 저장

#### 꼬마 교통지킴이 (Kids Traffic)

- `POST /api/v1/games/kids-traffic/start/` - 게임 세션 시작
- `POST /api/v1/games/kids-traffic/finish/` - 게임 세션 종료 및 결과 저장

### 4. 레포트 (Reports)

**Base Path**: `/api/v1/reports/`

- `POST /api/v1/reports/` - PIN 인증으로 레포트 상세 조회 (JWT 또는 Bot 인증)
- `POST /api/v1/reports/status/` - 레포트 생성 상태 확인 및 생성 트리거
- `POST /api/v1/reports/email/` - 레포트 PDF 이메일 발송
- `POST /api/v1/reports/set-report-pin/` - 레포트 접근 PIN 설정/변경

### 5. 랭킹 (Ranking)

**Base Path**: `/games/`

- `GET /games/ranking/` - 랭킹 웹 페이지 표시
- `GET /games/api/ranking/` - 랭킹 데이터 JSON API

### 인증 방식

- **JWT (JSON Web Token)**: 대부분의 인증 엔드포인트에 사용
- **Bot Authentication**: 레포트 접근을 위한 커스텀 인증 (ReportBotAuthentication)
- **No Authentication**: 헬스체크, 사용자명 확인, 회원가입은 인증 불필요
