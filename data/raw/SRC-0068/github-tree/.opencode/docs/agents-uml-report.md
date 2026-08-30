# Agents UML 보고서

## 목적
Agent들의 **이름**, **역할**, **주요 연결 관계**를 한눈에 볼 수 있도록 UML 자료를 작성했습니다.

## 산출물
- UML 원본 파일: `.opencode/docs/agents-uml.puml`

## 구성 기준
- 소스: `.opencode/agents/*.md` (총 47개 파일)
- 표시 요소:
  - Agent 이름
  - 설명 기반 역할 요약
  - `## Linked Agents` 섹션의 대표 관계

## 시각화 요약
- **Cross Project**: ceo, cto, product-lead, hr-manager, qa-engineer, mefittools-manager
- **Backend**: PM/개발/테스트 + 도메인 Agent
- **Frontend**: PM/컴포넌트/API/스토어/테스트 + 도메인 보조 Agent
- **Analysis Resume / Scraping / Voice API / Report / Infra**: 각 PM 중심 실행 구조

## 핵심 관계 패턴
1. **ceo 중심 허브 구조**
   - 각 프로젝트 PM(백엔드/프론트/분석/스크래핑/음성/리포트/인프라)로 전략 지시
2. **PM 중심 실행 구조**
   - 각 PM이 개발 Agent(Dev/API/Service/Task/Tester)를 오케스트레이션
3. **도메인 지식 의존 구조**
   - PM/개발 Agent가 Domain Agent 또는 Knowledge Manager로부터 사양 검증
4. **교차 프로젝트 연결**
   - fe-domain-info-requester ↔ be-api/도메인
   - BE/Analysis/Voice/Scraping 작업이 Infra로 배포 연계

## 참고
- 일부 Linked Agents 대상(예: `BE-Reviewer`, `Infra-Tester` 등)은 현재 agents 폴더의 파일로 직접 확인되지 않아, UML에서는 **문서상 관계 중심**으로 반영했습니다.
