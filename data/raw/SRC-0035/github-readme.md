# Athena Project

## 프로젝트 개요
Athena는 문제 해결과 학습을 위한 인터랙티브 웹 플랫폼입니다. Django 기반으로 구축되었습니다.

## 주요 기능
- 사용자 인증 및 관리 시스템
- 문제 해결 인터페이스
- 아티클 관리 시스템
- API 엔드포인트 제공
- AI 에이전트 기반 상호작용 시스템
- Celery를 활용한 실시간 태스크 처리

## 기술 스택
- **백엔드**: Django
- **데이터베이스**: PostgreSQL
- **태스크 큐**: Redis + Celery
- **컨테이너화**: Docker
- **모니터링**: Flower (Celery 모니터링)

## 프로젝트 구조 (source_code 하위)
```
webapp/
├── api/          # API 엔드포인트
├── agent/        # 에이전트 관련 기능
├── article/      # 아티클 관리
├── config/       # 프로젝트 설정
├── main/         # 메인 애플리케이션 로직
├── problem/      # 문제 관리 기능
├── static/       # 정적 파일
├── templates/    # HTML 템플릿
└── user/         # 사용자 관리
```

## 시스템 구성
프로젝트는 Docker Compose를 사용하여 다음과 같은 서비스로 구성되어 있습니다:
- `athena_webapp`: 메인 Django 애플리케이션
- `athena_db`: PostgreSQL 데이터베이스
- `athena_test_db`: 테스트용 데이터베이스
- `redis`: 캐싱 및 태스크 큐용 Redis 서버
- `celery-worker`: 백그라운드 태스크 처리
- `celery-beat`: 스케줄된 태스크 관리
- `flower`: Celery 모니터링 인터페이스

## 스크린샷
프로젝트의 주요 화면은 다음과 같습니다:

### 메인 페이지
![메인 페이지](assets/main_page.png)

### 문제 페이지
![문제 페이지](assets/question_page.png)

## 개발 환경 설정

### 필수 요구사항
- Docker
- Docker Compose
- Python 3.x

### 환경 변수
`.env` 파일에 다음 변수들을 설정해야 합니다:
```
PORT=8000
POSTGRES_DB=athena_db
POSTGRES_USER=athena_user
POSTGRES_PASSWORD=your_password
POSTGRES_PORT=5432
TEST_POSTGRES_DB=athena_test_db
TEST_POSTGRES_USER=athena_test_user
TEST_POSTGRES_PASSWORD=your_test_password
TEST_POSTGRES_PORT=5433
```

### 애플리케이션 실행
1. 저장소 클론
2. `.env` 파일 생성 및 설정
3. 다음 명령어 실행:
```bash
docker-compose up
```

애플리케이션은 `http://localhost:8000`에서 접근 가능합니다.

### 모니터링
- Celery Flower 모니터링 인터페이스: `http://localhost:5555`

## 테스트
프로젝트는 테스트 실행을 위한 별도의 테스트 데이터베이스를 포함하고 있습니다. 다음 명령어로 테스트를 실행할 수 있습니다:
```bash
docker-compose exec athena_webapp python manage.py test
```

## 기여 방법
1. 저장소 포크
2. feature/ 브랜치 생성
3. 변경사항 커밋
4. 브랜치 푸시
5. 풀 리퀘스트 생성
