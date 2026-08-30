# MeFit Domain Knowledge

## Interview (가상 면접)

### 세션 흐름
1. **Precheck**: 마이크/카메라/네트워크 검사
2. **Setup**: JD 선택, 면접 환경 설정
3. **Session**: 실제 면접 진행 (질문 답변)
4. **Result**: 피드백 및 점수 제공

### 핵심 entities
- `InterviewSession`: 세션 관리
- `InterviewTurn`: 질문/답변 세트
- `InterviewAnalysisReport`: 분석 결과
- `Question`: 질문 관리
- `Answer`: 사용자 답변
- `Transcript`: 실시간 변환 결과

---

## Resume (이력서)

### 파싱 흐름
1. 파일 업로드 (PDF/DOCX)
2. 파싱 진행 (AnalysisProgress)
3. 섹션 추출 (경력, 학력, 스킬)
4. 템플릿 매핑

### 핵심 entities
- `Resume`: 이력서 기본
- `ResumeTextContent`: 파싱된 텍스트
- `ResumeFileContent`: 원본 파일
- `ResumeBasicInfo`, `ResumeExperience`, `ResumeEducation`: 섹션별
- `ResumeSkill`, `ResumeProject`, `ResumeCertification`: 추가 정보
- `ResumeSummary`: 요약
- `ResumeEmbedding`: Vector Search용

---

## Ticket (이용권)

### 티켓 생명주기
1. **Grant**: 발급 (구독, 관리자赠送)
2. **Use**: 사용 (면접 시작 시 차감)
3. **Refund**: 환불 (취소 시 복구)
4. **Expire**: 만료 (기간 경과)

### 핵심 entities
- `UserTicket`: 사용자 보유 티켓
- `TicketLog`: 사용 이력

---

## Achievement (업적)

### 업적 유형
- **Interview**: 면접 횟수 달성
- **Streak**: 연속 학습
- **Profile**: 프로필 완성
- **Custom**: 이벤트 등

### 평가 흐름
1. Trigger 발생 (면접 완료 등)
2. Condition 평가
3. 보상 지급 (티켓 등)

### 어드민 운영 이슈 기록
- 어드민에서 업적 평가/초기화 시, 폼 뷰 및 버튼 노출은 Unfold 기반 커스텀 View + URL 패턴으로 구성
- 리스트 상단 버튼과 액션에서 동일 폼으로 이동하도록 설계

### API 응답 규칙
- API 응답은 middleware에서 camelCase로 변환됨
- 프론트는 camelCase 기준으로 필드를 사용해야 UI 상태가 정상 표시됨
  - 예시: isAchieved, achievedAt, rewardClaimedAt, canClaimReward

---

## Subscription (구독)

### 구독 정책
- **Free**: 기본 이용
- **Premium**: 무제한 면접
- **Tier**: 등급별 차등

### 핵심 entities
- `Subscription`: 사용자 구독
- `SubscriptionPlan`: 구독 플랜
- `SubscriptionPlanTicketPolicy`: 플랜별 티켓 정책

---

## Job Description (채용공고)

### 기능
- 채용공고 수집기 통한 수집
- 기업 채용공고 관리
- 채용공고 분석

### 핵심 entities
- `JobDescription`: 기업 채용공고 (收載된 공고)
- `UserJobDescription`: 사용자 저장 공고

---

## Profile (프로필)

### 기능
- 사용자 프로필 관리
- 직무 카테고리/직무 선택
- 프로필 완성도 추적

### 핵심 entities
- `Profile`: 사용자 프로필
- `JobCategory`: 직무 카테고리
- `Job`: 직무

---

## Streak (연속 학습)

### 기능
- 일일 면접 참여 추적
- 연속 기록 관리
- 보상 정책

### 핵심 entities
- `StreakStatistics`: 연속 통계
- `StreakLog`: 일일 기록
- `DailyInterviewRewardPolicy`: 보상 정책

---

## Terms (약관)

### 기능
- 약관 동의 관리
- 버전 관리

### 핵심 entities
- `TermsDocument`: 약관 문서
- `UserConsent`: 사용자 동의
