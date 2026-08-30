---
name: be-test
description: Django 테스트 코드 - django.test.TestCase, Factory Boy, 단위 테스트
compatibility: opencode
---

# Django 테스트 생성

## 위치
`webapp/{앱}/tests/services/test_{service}.py`

## 템플릿

```python
from django.test import TestCase
from 앱.factories import 모델Factory

class Create모델ServiceTests(TestCase):
  def setUp(self):
    self.user = UserFactory()

  def test_정상_생성(self):
    result = Create모델Service(user=self.user, title="테스트").perform()
    self.assertIsNotNone(result.pk)
```

## 체크리스트
- [ ] django.test.TestCase 사용
- [ ] Factory Boy 데이터
- [ ] 한국어 메서드명
- [ ] @patch로 mocking