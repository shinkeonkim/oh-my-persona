---
name: be-service
description: Django 서비스 레이어 - BaseService/BaseQueryService, 비즈니스 로직
compatibility: opencode
---

# Django 서비스 생성

## 유형

| 유형 | 베이스 | 트랜잭션 |
|------|-------|----------|
| 쓰기 | BaseService | 내부 |
| 읽기 | BaseQueryService | 없음 |

## 파일 위치
`webapp/{앱}/services/{service}.py`

## 템플릿

```python
from common.services import BaseService

class Create모델Service(BaseService):
  required_value_kwargs = ["title"]

  def validate(self):
    # 비즈니스 규칙
    pass

  def execute(self):
    return 모델.objects.create(
      user=self.user,
      title=self.kwargs["title"],
    )
```

## 체크리스트
- [ ] BaseService/BaseQueryService 상속
- [ ] required_kwargs 설정
- [ ] validate() 구현
- [ ] execute() 구현