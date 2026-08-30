---
name: be-api
description: DRF API 엔드포인트 - ViewSet, Serializer, permission_classes
compatibility: opencode
---

# DRF API 생성

## 베이스 클래스

| 용도 | 베이스 | 인증 |
|------|-------|--------|
| CRUD | BaseViewSet | 필수 |
| 커스텀 | BaseGenericViewSet | 필수 |
| 단일 | BaseAPIView | 필수 |

## 파일 위치
- View: `webapp/api/v1/{앱}/views/{view}.py`
- Serializer: `webapp/api/v1/{앱}/serializers/{serializer}.py`

## 템플릿

```python
from common.permissions import IsEmailVerified
from common.views import BaseGenericViewSet

class 모델ViewSet(BaseGenericViewSet):
  permission_classes = [IsEmailVerified]

  def get_serializer_class(self):
    if self.action == "create":
      return Create모델Serializer
    return 모델Serializer
```

## 체크리스트
- [ ] permission_classes 설정
- [ ] @extend_schema 적용
- [ ] get_serializer_class() 분기
- [ ] select_related 최적화