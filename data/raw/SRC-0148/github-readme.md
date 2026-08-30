# 투표 시스템 (Poll System)

실시간 투표 기능을 제공하는 웹 애플리케이션입니다. Django REST Framework와 Vue.js를 사용하여 구현되었으며, 모든 컴포넌트가 Docker로 컨테이너화되어 있습니다.

## 주요 기능

### 투표 기능
- **찬반투표**: 찬성/반대 2개 선택지
- **객관식투표**: 여러 개의 선택지 중 선택
- **사용자당 투표 횟수 제한**: 각 투표마다 최대 투표 횟수 설정 가능
- **중복 선택 제어**: 같은 선택지를 여러 번 선택할 수 있는지 설정 가능

### 실시간 기능
- **WebSocket 기반 실시간 업데이트**: 투표 결과가 실시간으로 업데이트
- **동시성 처리**: Redis를 이용한 분산 락으로 동시 투표 처리
- **Celery 비동기 처리**: 투표 처리를 백그라운드에서 안전하게 수행

### 사용자 인터페이스
- **반응형 웹 디자인**: 모바일과 데스크톱 모두 지원
- **투표 목록**: 진행 중인 투표들을 한눈에 확인
- **투표 상세**: 실시간 결과와 통계 제공
- **투표 기록**: 사용자별 투표 참여 이력

### 관리 기능
- **Django Admin**: 투표 생성 및 관리
- **투표 통계**: 각 선택지별 득표 현황 및 백분율
- **결과 공개 설정**: 실시간 결과 공개 여부 제어

## 기술 스택

### 백엔드
- **Python 3.12** + **Django 5.2**
- **Django REST Framework**: API 서버
- **Django Channels**: WebSocket 지원
- **JWT Authentication**: 토큰 기반 인증
- **PostgreSQL**: 메인 데이터베이스
- **Redis**: 캐시 및 메시지 브로커
- **Celery**: 비동기 작업 처리
- **uv**: Python 패키지 관리

### 프론트엔드
- **Vue.js 3**: UI 프레임워크
- **Vuex**: 상태 관리
- **Vue Router**: 라우팅
- **Axios**: HTTP 클라이언트
- **WebSocket**: 실시간 통신

### 인프라
- **Docker & Docker Compose**: 컨테이너화
- **nginx**: 리버스 프록시 (추후 추가 가능)

## 프로젝트 구조

```
poll-experiment/
├── docker-compose.yml          # Docker 컴포즈 설정
├── build.sh                   # 빌드 스크립트
├── backend/                   # Django 백엔드
│   ├── Dockerfile.base        # 공통 베이스 이미지
│   ├── Dockerfile.backend     # 백엔드 서비스 이미지
│   ├── Dockerfile.celery      # Celery 워커 이미지
│   ├── Dockerfile.celery-beat # Celery Beat 이미지
│   ├── .dockerignore         # Docker 빌드 제외 파일
│   ├── pyproject.toml        # uv 프로젝트 설정
│   └── poll_backend/
│       ├── manage.py
│       ├── poll_server/      # Django 설정
│       └── polls/            # 투표 앱
│           ├── models/       # 데이터 모델 패키지
│           │   ├── __init__.py
│           │   ├── poll.py    # Poll 모델
│           │   ├── choice.py  # Choice 모델
│           │   ├── vote.py    # Vote 모델
│           │   └── vote_session.py # VoteSession 모델
│           ├── views/        # API 뷰 패키지
│           │   ├── __init__.py
│           │   ├── poll_views.py   # 투표 관련 뷰
│           │   ├── vote_views.py   # 투표 참여 뷰
│           │   ├── stats_views.py  # 통계 뷰
│           │   ├── user_views.py   # 사용자 뷰
│           │   └── utils.py        # 유틸리티 함수
│           ├── serializers/  # 시리얼라이저 패키지
│           │   ├── __init__.py
│           │   ├── user_serializers.py    # 사용자 관련
│           │   ├── poll_serializers.py    # 투표 관련
│           │   ├── choice_serializers.py  # 선택지 관련
│           │   ├── vote_serializers.py    # 투표 기록 관련
│           │   └── stats_serializers.py   # 통계 관련
│           ├── tasks/        # Celery 태스크 패키지
│           │   ├── __init__.py
│           │   ├── vote_tasks.py     # 투표 처리 태스크
│           │   ├── cleanup_tasks.py  # 정리 태스크
│           │   └── stats_tasks.py    # 통계 생성 태스크
│           ├── consumers/     # WebSocket 컨슈머 패키지
│           │   ├── __init__.py
│           │   ├── poll_consumer.py      # 투표 실시간 업데이트
│           │   └── poll_list_consumer.py # 투표 목록 실시간 업데이트
│           ├── admin/        # Django Admin 패키지
│           │   ├── __init__.py
│           │   ├── poll_admin.py         # Poll 관리
│           │   ├── choice_admin.py       # Choice 관리
│           │   ├── vote_admin.py         # Vote 관리
│           │   └── vote_session_admin.py # VoteSession 관리
│           ├── tests/        # 테스트 패키지
│           │   ├── __init__.py
│           │   ├── test_models.py
│           │   ├── test_views.py
│           │   ├── test_tasks.py
│           │   └── test_serializers.py
│           ├── signals.py    # Django 시그널
│           ├── routing.py    # WebSocket 라우팅
│           ├── middleware.py # 커스텀 미들웨어
│           └── urls.py       # URL 설정
└── frontend/                 # Vue.js 프론트엔드
    ├── Dockerfile
    ├── package.json
    └── src/
        ├── components/       # Vue 컴포넌트
        ├── views/           # 페이지 컴포넌트
        ├── store/           # Vuex 스토어
        ├── composables/     # Vue 컴포저블
        └── router/          # Vue Router 설정
```

## 설치 및 실행

### 사전 요구사항
- Docker
- Docker Compose

### 실행 방법

1. **저장소 클론**
   ```bash
   git clone <repository-url>
   cd poll-experiment
   ```

2. **환경 변수 설정** (선택사항)
   ```bash
   # .env 파일 생성 (필요한 경우)
   cp .env.example .env
   ```

3. **Docker 이미지 빌드**
   ```bash
   # 방법 1: 빌드 스크립트 사용 (권장)
   ./build.sh

   # 방법 2: 수동 빌드
   docker-compose --profile build-base build backend-base
   docker-compose build
   ```

4. **Docker 컨테이너 실행**
   ```bash
   docker-compose up -d
   ```

5. **데이터베이스 마이그레이션**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

6. **슈퍼유저 생성** (Django Admin 접근용)
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

7. **정적 파일 수집**
   ```bash
   docker-compose exec backend python manage.py collectstatic --noinput
   ```

### 접속 정보

- **프론트엔드**: http://localhost:3000
- **Django Admin**: http://localhost:8000/admin
- **API 문서**: http://localhost:8000/api/ (DRF 브라우저블 API)

## 사용법

### 1. 관리자 계정으로 투표 생성
1. http://localhost:8000/admin 접속
2. 슈퍼유저 계정으로 로그인
3. Polls > Polls에서 새 투표 생성
4. 투표 제목, 설명, 유형, 선택지 등 설정

### 2. 사용자 투표 참여
1. http://localhost:3000 접속
2. 관리자 계정으로 로그인 (또는 새 계정 생성)
3. 투표 목록에서 참여할 투표 선택
4. 선택지 클릭하여 투표 참여

### 3. 실시간 결과 확인
- 투표 상세 페이지에서 실시간으로 업데이트되는 결과 확인
- 여러 브라우저에서 동시에 투표하여 실시간 업데이트 테스트

## API 엔드포인트

### 인증
- `POST /api/auth/token/` - JWT 토큰 발급
- `POST /api/auth/token/refresh/` - 토큰 갱신

### 투표
- `GET /api/polls/` - 투표 목록 조회
- `POST /api/polls/` - 새 투표 생성
- `GET /api/polls/{id}/` - 투표 상세 조회
- `POST /api/polls/{id}/vote/` - 투표 참여
- `GET /api/polls/{id}/statistics/` - 투표 통계 조회
- `GET /api/polls/{id}/user-status/` - 사용자 투표 상태 조회
- `GET /api/polls/user/history/` - 사용자 투표 기록

### WebSocket
- `ws://localhost:8000/ws/poll/{id}/` - 특정 투표 실시간 업데이트
- `ws://localhost:8000/ws/polls/` - 투표 목록 실시간 업데이트

## 개발 모드 실행

### 백엔드 개발
```bash
cd backend
uv sync
cd poll_backend
uv run python manage.py runserver
```

### 프론트엔드 개발
```bash
cd frontend
npm install
npm run serve
```

## 주요 설정

### 투표 설정 옵션
- **최대 투표 횟수**: 사용자당 참여 가능한 투표 횟수
- **중복 선택 허용**: 같은 선택지 여러 번 선택 가능 여부
- **실시간 결과 공개**: 투표 진행 중 결과 공개 여부
- **투표 수 공개**: 각 선택지별 투표 수 표시 여부

### 보안 기능
- JWT 기반 인증
- Redis 분산 락으로 동시성 제어
- CORS 설정으로 크로스 오리진 요청 제어
- SQL 인젝션 방지 (Django ORM)

## 트러블슈팅

### 일반적인 문제

1. **컨테이너 실행 실패**
   ```bash
   docker-compose down
   docker-compose up --build
   ```

2. **데이터베이스 연결 오류**
   ```bash
   docker-compose restart db
   docker-compose exec backend uv run python manage.py migrate
   ```

3. **WebSocket 연결 실패**
   - Redis 컨테이너가 정상 실행 중인지 확인
   - 브라우저의 개발자 도구에서 WebSocket 연결 상태 확인

4. **투표 처리 지연**
   - Celery 워커가 정상 동작하는지 확인
   - Redis 연결 상태 확인

### 로그 확인
```bash
# 전체 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery
```
