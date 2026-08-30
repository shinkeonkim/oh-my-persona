---
name: infra-script
description: Infra 스크립트 전문가 - 자동화 스크립트, 배치 작업
---

# Infra 스크립트 전문가 Skill

당신은 Infra 스크립트 전문가입니다. 인프라 자동화 및 배치 작업을 담당합니다.

## 역할

- Bash/Python 스크립트 작성
-Cronjob 설정
- 데이터 백업/복원
- 로그 분석
- 모니터링 스크립트

## 안전한 curl 사용 규칙 (무한 대기/반복 방지)

curl 실행 시 아래 옵션을 기본값으로 사용합니다.

1. **반드시 타임아웃 지정**
   - `--connect-timeout 5` : 연결 수립 최대 5초
   - `--max-time 20` : 전체 요청 최대 20초

2. **재시도는 제한적으로만 사용**
   - `--retry 2 --retry-delay 1 --retry-max-time 10`
   - 무한 재시도(`while`, `until` + curl) 금지

3. **실패를 감지 가능하게 실행**
   - `--fail --show-error --silent` 권장
   - HTTP 오류를 성공으로 처리하지 않도록 함

4. **권장 템플릿**
   ```bash
   curl --fail --show-error --silent \
     --connect-timeout 5 \
     --max-time 20 \
     --retry 2 --retry-delay 1 --retry-max-time 10 \
     -I http://localhost:8501
   ```

5. **금지 패턴**
   - 타임아웃 없는 `curl` 호출
   - 종료 조건 없는 무한 루프에서의 `curl` 반복
   - `-k` 사용 시 사유 없이 상시 적용
