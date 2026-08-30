# 기획 문서: 사용자 알림 시스템 Backend 구현

> 작성일: 2026-04-17
> 최종 수정: 2026-04-17 — notifiable GenericForeignKey 추가
> 상태: 기획 완료, 구현 대기

---

## 1. 배경 및 목표

### 현황

Frontend에 알림 기능이 일부 구현되어 있으나, Backend에서 지원하는 API가 없어 실제 동작 불가.

| 항목 | 상태 |
|------|------|
| Frontend WS 연결 코드 | 구현됨 |
| Frontend 알림 목록 UI | 구현됨 |
| Backend WS 라우팅 (`ws/notifications/`) | **미구현** |
| Backend Notification 모델 | **미구현** |
| Backend 알림 발송 서비스 | **미구현** |
| Backend REST API | **미구현** |

### 목표

사용자가 다음 이벤트 발생 시 실시간 알림을 받을 수 있도록 Backend를 구현한다:

- 이력서 분석 완료
- 면접 리포트 생성 완료
- JD(채용공고) 스크래핑 완료

---

## 2. 사용자 시나리오

```
1. 사용자가 로그인 후 앱에 진입한다.
2. Frontend가 /api/v1/realtime/ws-ticket/ 에서 WS 티켓을 발급받는다.
3. wss://{host}/ws/notifications/?ticket=<ticket> 으로 WS 연결한다.
4. 사용자가 분석/면접/스크래핑 작업을 요청한다.
5. 해당 작업이 완료되면 Backend가 알림을 생성하고 WS로 push한다.
6. Frontend 알림 UI에 실시간으로 알림이 표시된다.
```

---

## 3. Frontend가 기대하는 인터페이스

### WS 연결

```
wss://{host}/ws/notifications/?ticket=<ticket>
```

### WS push 메시지 형식 (서버 → 클라이언트)

```json
{
  "id": 1,
  "message": "이력서 분석이 완료되었습니다.",
  "category": "resume",
  "createdAt": "2026-04-17T12:00:00Z",
  "notifiableType": "resumes.resume",
  "notifiableId": "550e8400-e29b-41d4-a716-446655440000"
}
```

`category` 값:
- `"interview"` — 면접 관련
- `"resume"` — 이력서 분석 관련
- `"jd"` — 채용공고 스크래핑 관련
- `"system"` — 시스템 알림

`notifiableType` / `notifiableId`:
- 알림과 연관된 객체의 ContentType 레이블 및 PK
- 시스템 알림 등 연관 객체가 없는 경우 `null`
- Frontend에서 바로 가기 링크 생성에 활용 (예: `notifiableType === "resumes.resume"` → `/resumes/{notifiableId}`)

### REST API (영속성 지원 — 선택)

```
GET    /api/v1/notifications/            # 알림 목록 (최신순)
PATCH  /api/v1/notifications/{id}/read/  # 읽음 처리
DELETE /api/v1/notifications/{id}/       # 단건 삭제
DELETE /api/v1/notifications/            # 전체 삭제
```

---

## 4. 구현 범위 및 우선순위

### Phase 1 — WS 연결 활성화 (필수, 최우선)

- [ ] `notifications` Django 앱 생성
- [ ] `NotificationConsumer` 구현 (`UserWebSocketConsumer` 상속)
- [ ] `ws/notifications/` ASGI 라우팅 등록
- [ ] `REALTIME_DOCS_CONSUMERS`에 consumer 등록

### Phase 2 — 알림 모델 및 발송 서비스

- [ ] `Notification` 모델 구현
- [ ] `CreateNotificationService` 구현 (알림 생성 + WS push)
- [ ] 기존 Celery 태스크에서 `CreateNotificationService` 호출
  - 이력서 분석 완료 태스크
  - 면접 리포트 완료 태스크
  - JD 스크래핑 완료 태스크

### Phase 3 — REST API (선택, 알림 영속성 지원)

- [ ] `GET /api/v1/notifications/` 목록 조회
- [ ] `PATCH /api/v1/notifications/{id}/read/` 읽음 처리
- [ ] `DELETE /api/v1/notifications/{id}/` 단건 삭제
- [ ] `DELETE /api/v1/notifications/` 전체 삭제

---

## 5. 데이터 모델 설계

참고: `llm_trackers/models/token_usage.py`의 `TokenUsage` 모델과 동일한 패턴으로 `GenericForeignKey`를 사용한다.
UUID/정수 PK 모두 수용하기 위해 `notifiable_id`는 `CharField`로 선언한다.

```python
# notifications/models.py

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Notification(BaseModel):
    class Category(models.TextChoices):
        INTERVIEW = "interview", "면접"
        RESUME = "resume", "이력서"
        JD = "jd", "채용공고"
        SYSTEM = "system", "시스템"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="사용자",
    )
    message = models.TextField(verbose_name="메시지")
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        verbose_name="카테고리",
    )
    is_read = models.BooleanField(default=False, verbose_name="읽음 여부")

    # Polymorphic FK — 어떤 객체(이력서, 면접세션 등)와 연관된 알림인지 저장
    # UUID/정수 PK 모두 수용하기 위해 CharField 사용 (TokenUsage 패턴과 동일)
    notifiable_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="관련 모델 타입",
    )
    notifiable_id = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name="관련 객체 PK",
    )
    notifiable = GenericForeignKey("notifiable_type", "notifiable_id")

    class Meta:
        db_table = "notifications"
        verbose_name = "알림"
        verbose_name_plural = "알림 목록"
        ordering = ["-created_at"]
```

**notifiable 사용 예시:**

| 알림 이벤트 | notifiable 객체 | notifiableType |
|------------|----------------|----------------|
| 이력서 분석 완료 | `Resume` 인스턴스 | `"resumes.resume"` |
| 면접 리포트 완료 | `InterviewSession` 인스턴스 | `"interviews.interviewsession"` |
| JD 스크래핑 완료 | `UserJobDescription` 인스턴스 | `"job_descriptions.userjobdescription"` |
| 시스템 알림 | (없음) | `null` |

---

## 6. WS Consumer 설계

```python
# notifications/consumers.py

from common.consumers.websocket import UserWebSocketConsumer

class NotificationConsumer(UserWebSocketConsumer):
    async def connect(self):
        await super().connect()
        # 연결 시 추가 로직 필요 시 여기에

    async def notification_message(self, event):
        """
        Channel Layer에서 'notification.message' 타입 메시지 수신 시 WS로 전송.
        """
        await self.send_json(event["data"])
```

---

## 7. 알림 발송 서비스 설계

```python
# notifications/services.py

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

class CreateNotificationService:
    def __init__(self, user, message: str, category: str, notifiable=None):
        self.user = user
        self.message = message
        self.category = category
        self.notifiable = notifiable  # Django 모델 인스턴스 또는 None

    def perform(self) -> Notification:
        kwargs = dict(
            user=self.user,
            message=self.message,
            category=self.category,
        )
        if self.notifiable is not None:
            kwargs["notifiable_type"] = ContentType.objects.get_for_model(self.notifiable)
            kwargs["notifiable_id"] = str(self.notifiable.pk)

        notification = Notification.objects.create(**kwargs)
        self._push_to_ws(notification)
        return notification

    def _push_to_ws(self, notification: Notification):
        channel_layer = get_channel_layer()
        group_name = f"user_{self.user.pk}"

        data = {
            "id": notification.pk,
            "message": notification.message,
            "category": notification.category,
            "createdAt": notification.created_at.isoformat(),
            "notifiableType": (
                notification.notifiable_type.app_label + "." + notification.notifiable_type.model
                if notification.notifiable_type
                else None
            ),
            "notifiableId": notification.notifiable_id,
        }

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "notification.message",
                "data": data,
            },
        )
```

---

## 8. Celery 태스크 연동 지점

| 태스크 | 파일 경로 | 연동 위치 |
|--------|-----------|-----------|
| 이력서 분석 완료 | `resumes/tasks/` | 분석 결과 저장 후 |
| 면접 리포트 완료 | `interviews/tasks/` | 리포트 생성 후 |
| JD 스크래핑 완료 | `job_descriptions/tasks/` | 스크래핑 완료 후 |

연동 패턴:
```python
# 각 태스크 완료 시점에 추가
from notifications.services import CreateNotificationService

# notifiable에 관련 객체를 전달 → Frontend에서 바로 가기 링크 생성 가능
CreateNotificationService(
    user=user,
    message="이력서 분석이 완료되었습니다.",
    category="resume",
    notifiable=resume,          # Resume 인스턴스
).perform()

# 연관 객체가 없는 시스템 알림의 경우 notifiable 생략
CreateNotificationService(
    user=user,
    message="시스템 점검이 완료되었습니다.",
    category="system",
).perform()
```

---

## 9. 태스크 설계

### Task 1. `notifications` 앱 기반 구축

**담당**: BE
**예상 소요**: 1~2시간
**산출물**:
- `notifications/` 앱 디렉토리 (apps.py, __init__.py)
- `NotificationConsumer` (consumers.py)
- ASGI routing 등록
- INSTALLED_APPS 등록

**완료 조건**:
- `ws/notifications/?ticket=<valid_ticket>` 연결 성공
- 연결 후 서버에서 test message 수신 가능

---

### Task 2. Notification 모델 및 마이그레이션

**담당**: BE
**예상 소요**: 1시간
**산출물**:
- `Notification` 모델 (models.py)
- `0001_initial` 마이그레이션

**완료 조건**:
- `python manage.py migrate` 성공
- Django Admin에서 Notification 확인 가능

---

### Task 3. CreateNotificationService 구현

**담당**: BE
**예상 소요**: 2시간
**산출물**:
- `CreateNotificationService` (services.py)
- 단위 테스트 (tests/)

**완료 조건**:
- service.perform() 호출 시 DB 저장 + WS push 동작
- 단위 테스트 통과

---

### Task 4. Celery 태스크 연동

**담당**: BE
**예상 소요**: 1~2시간
**전제 조건**: Task 3 완료
**산출물**:
- 이력서/면접/JD 태스크에 알림 발송 코드 추가

**완료 조건**:
- 각 작업 완료 시 WS 알림 수신 E2E 동작

---

### Task 5. REST API 구현 (선택)

**담당**: BE
**예상 소요**: 2~3시간
**전제 조건**: Task 2 완료
**산출물**:
- `NotificationViewSet` (views.py)
- URL 등록
- Serializer

**완료 조건**:
- GET /api/v1/notifications/ 200 응답
- PATCH read 처리, DELETE 동작

---

## 10. 관련 파일 경로 참조

```
backend/
├── config/
│   ├── asgi.py              # WS routing 등록 위치
│   └── settings/
├── common/
│   └── consumers/
│       └── websocket.py     # UserWebSocketConsumer (상속 베이스)
├── api/v1/realtime/
│   └── views.py             # WsTicketAPIView (티켓 발급)
└── notifications/           # 신규 생성 필요
    ├── apps.py
    ├── models.py
    ├── consumers.py
    ├── services.py
    ├── views.py             # (Phase 3)
    ├── serializers.py       # (Phase 3)
    ├── urls.py              # (Phase 3)
    └── tests/

frontend/src/
├── features/notifications/
│   ├── model/store.ts       # Zustand store (WS 연결, 상태 관리)
│   └── index.ts
├── pages/notifications/ui/
│   └── NotificationsPage.tsx
└── shared/api/
    └── realtimeApi.ts       # WS 연결 클라이언트
```
