---
name: be-task
description: Celery 비동기 태스크 - BaseTask, BaseScheduledTask, crontab
compatibility: opencode
---

# Celery 태스크 생성

## 유형

| 유형 | 베이스 |
|------|-------|
| 일반 | BaseTask |
| 주기 | BaseScheduledTask |

## 파일 위치
`webapp/{앱}/tasks/{task}.py`

## 템플릿

```python
from common.tasks import BaseTask
from config.celery import app

class XxxTask(BaseTask):
  def run(self, user_id, **kwargs):
    from 앱.services import XxxService
    return XxxService(user_id=user_id).perform()

RegisteredXxxTask = app.register_task(XxxTask())
```

## 체크리스트
- [ ] BaseTask 상속
- [ ] app.register_task() 등록
- [ ] service 호출