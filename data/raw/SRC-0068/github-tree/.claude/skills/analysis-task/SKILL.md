---
name: analysis-task
description: 분석-resume Celery 태스크 - 텍스트 추출, 임베딩, 분석
compatibility: opencode
---

# 분석-resume Celery 태스크

## Tasks

### extract_text
PDF/DOCX에서 텍스트 추출

### embed_resume
임베딩 생성

### analyze_resume
LLM 분석

### reembed_resume
임베딩 재생성

### finalize_resume
최종 처리

### process_resume
전체 파이프라인 실행

## 위치
`app/tasks/{task}.py`
