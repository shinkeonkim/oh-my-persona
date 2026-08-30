---
name: be-model
description: Django 모델 생성 - BaseModel 상속, db_table, verbose_name, related_name
compatibility: opencode
---

# Django 모델 생성

## 베이스 클래스 선택

| 용도 | 베이스 |
|------|-------|
| 일반 | BaseModel |
| UUID 필요 | BaseModelWithUUID |
| 논리삭제 | BaseModelWithSoftDelete |
| UUID + 논리삭제 | BaseModelWithUUIDAndSoftDelete |

## 파일 위치
`webapp/{앱}/models/{model}.py`

## 템플릿

```python
from common.models import BaseModelWithUUID
from django.conf import settings
from django.db import models

class 모델(BaseModelWithUUID):
  class Meta(BaseModelWithUUID.Meta):
    db_table = "테이블명_복수형"
    verbose_name = "이름"

  user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    related_name="모델_복수형",
  )
```

## 체크리스트
- [ ] BaseModel 계열 상속
- [ ] db_table 설정
- [ ] verbose_name 설정
- [ ] related_name 설정