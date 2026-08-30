---
name: scraping-pipeline
description: scraping 파이프라인 - 웹 스크래핑, 데이터 추출, 변환, 적재
compatibility: opencode
---

# scraping 파이프라인

## Components

### scraper.py
메인 스크래핑 스크립트

### pipeline.py
데이터 처리 파이프라인

### plugins/
- jobplanet: Jobplanet 스크래핑
- jobkorea: JobKorea 스크래핑
- default: 기본 스크래핑

### utils/
- browser: 브라우저 자동화
- anti_bot: 봇 감지 회피

## Schemas
- job_description.py
- job_posting.py
- extractor.py
- pipeline.py

## 위치
`scraping/`
