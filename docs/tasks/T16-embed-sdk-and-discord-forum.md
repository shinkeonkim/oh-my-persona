# T16 임베드 SDK와 Discord Forum 상담 연결

상태: `DOING`  
기준일: 2026-08-31

## 목표

`persona.shinkeonkim.com`의 대화를 다른 웹사이트에서 채널톡 형태로 사용할 수 있는
프레임워크 비종속 SDK로 제공한다. 방문자의 대화는 Discord Forum 게시물 하나와 연결하고,
김신건이 Forum 스레드에 남긴 답변은 최근 30일 이내 대화 세션으로 비동기 전달한다.

## 결정

1. SDK는 한 줄의 `<script>`로 설치하며 Shadow DOM으로 호스트 사이트 CSS와 격리한다.
2. 브라우저의 제3자 쿠키 차단을 전제로 한다. SDK는 설치된 사이트의 first-party
   `localStorage`에 `conversation_id`와 서버가 서명한 접근 토큰을 보관한다.
3. `portfolio.shinkeonkim.com`과 `resume.shinkeonkim.com`의 세션은 기본적으로 각각
   독립적이다. 도메인 간 추적을 위한 강제 fingerprinting은 하지 않는다.
4. 방문자 세션마다 Discord Forum 스레드 하나를 만든다. 웹 메시지와 AI 답변은 스레드에
   복제하고, Forum에서 김신건이 직접 쓴 메시지는 `owner` 메시지로 대화에 추가한다.
5. Discord 수신은 공식 Gateway의 `MESSAGE_CREATE` 이벤트를 사용하는 단일 replica worker가
   담당한다. 웹 API replica와 분리해 중복 Gateway 연결을 피한다.
6. Forum 답변 전달은 마지막 활동 시각이 30일 이내인 세션으로 제한한다.
7. 방문자 메시지는 HTTP `POST`, AI·관리자·Discord에서 추가된 메시지는 인증된 fetch 기반
   SSE로 전달한다. 브라우저가 임의 이벤트를 지속적으로 서버에 보낼 필요가 없으므로 WebSocket은
   사용하지 않는다. EventSource는 인증 헤더를 지원하지 않아 접근 토큰이 URL에 남을 수 있으므로
   `fetch()`의 ReadableStream으로 SSE를 해석한다.

## 공식 참고 자료

- Discord Start Thread in Forum or Media Channel:
  https://discord.com/developers/docs/resources/channel#start-thread-in-forum-or-media-channel
- Discord Gateway와 Gateway events:
  https://discord.com/developers/docs/topics/gateway
  https://discord.com/developers/docs/events/gateway-events#message-create
- Discord privileged intents:
  https://discord.com/developers/docs/events/gateway#privileged-intents
- MDN third-party cookies:
  https://developer.mozilla.org/en-US/docs/Web/Privacy/Guides/Third-party_cookies

## 실행 그래프

```text
T16A 현행/공식 문서 조사
 └─ T16B 세션·접근 토큰 API
     ├─ T16C 임베드 SDK ─┬─ T16E portfolio 통합 ─┐
     │                  └─ T16F resume 통합 ─────┤
     └─ T16D Discord REST+Gateway bridge ─────────┤
                                                 └─ T16G 브라우저/E2E/배포
```

## 완료 기준

- [x] 허용된 origin에서 widget session 생성, 재개, 메시지 조회가 가능하다.
- [x] 잘못된 접근 토큰으로 타 세션을 조회하거나 메시지를 추가할 수 없다.
- [x] SDK가 데스크톱과 모바일에서 열리고 닫히며 기존 사이트 레이아웃을 침범하지 않는다.
- [x] portfolio와 resume 빌드에 동일 SDK가 포함된다.
- [ ] 방문자 메시지가 Forum 스레드를 생성/갱신한다.
- [x] 허용된 Discord 사용자의 Forum 메시지가 30일 이내 세션에 `owner`로 저장된다(자동 테스트).
- [x] 30일을 지난 세션과 다른 Forum의 메시지는 무시한다(자동 테스트).
- [ ] Python/프론트엔드/Playwright 테스트와 운영 URL 종단 검증을 통과한다.

## 운영에 필요한 Secret

- `PERSONA_SESSION_SECRET`: 세션 접근 토큰 HMAC 서명 키
- `PERSONA_DISCORD_BOT_TOKEN`: Discord bot token
- `PERSONA_DISCORD_FORUM_CHANNEL_ID`: 상담 Forum channel ID
- `PERSONA_DISCORD_OWNER_IDS`: Forum 답변을 전달할 Discord 사용자 ID 목록

Secret 값은 저장소에 커밋하지 않는다.

Discord Developer Portal에서 bot의 **Message Content Intent**를 활성화한다. 서버 초대 시 대상
Forum에 `View Channel`, `Send Messages`, `Send Messages in Threads`, `Create Public Threads`,
`Read Message History` 권한을 부여한다. `PERSONA_DISCORD_OWNER_IDS`가 비어 있으면 Forum에서
웹 세션으로 전달되는 메시지는 보안을 위해 모두 거부한다.
