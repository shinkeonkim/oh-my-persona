---
name: be-realtime
description: WebSocket/SSE Consumer - 실시간 통신, Django Channels
compatibility: opencode
---

# WebSocket/SSE 생성

## 유형

| 프로토콜 | 베이스 |
|----------|-------|
| WebSocket | UserWebSocketConsumer |
| SSE | UserSseConsumer |

## 파일 위치
- Consumer: `webapp/api/v1/{앱}/consumers.py`
- Routing: `webapp/api/v1/{앱}/routing.py`

## 파일 위치
`webapp/api/v1/{앱}/routing.py`

## 체크리스트
- [ ] structlog 로깅
- [ ] routing.py 정의
- [ ] asgi.py 등록