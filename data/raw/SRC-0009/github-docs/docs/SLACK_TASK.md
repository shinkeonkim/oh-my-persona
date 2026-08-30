# Slack Bot 연동 및 토큰 발급/설정 가이드

Twin AI의 Slack Bot을 실제로 사용하기 위한 절차를 정리합니다.

---

## 1. Slack 앱 생성
1. [Slack API: Your Apps](https://api.slack.com/apps)로 이동
2. **Create New App** 클릭 → "From scratch" 선택
3. 앱 이름과 사용할 워크스페이스 선택 → **Create App**

---

## 2. Bot Token (SLACK_BOT_TOKEN) 발급
1. **OAuth & Permissions** 메뉴로 이동
2. **Scopes**에서 아래 권한 추가:
   - `app_mentions:read`
   - `chat:write`
   - `channels:history`
   - `groups:history`
   - `im:history`
   - `mpim:history`
   - (필요시 추가 권한)
3. **Install App to Workspace** 클릭 → 권한 허용
4. **Bot User OAuth Token**(xoxb-로 시작)을 복사 → `.env`의 `SLACK_BOT_TOKEN`에 입력

---

## 3. App Token (SLACK_APP_TOKEN) 발급
1. **Basic Information** → **App-Level Tokens**로 이동
2. **Generate Token and Scopes** 클릭
3. 이름 입력, **Scope**에 `connections:write` 추가
4. **Generate** 클릭 → xapp-로 시작하는 토큰 복사 → `.env`의 `SLACK_APP_TOKEN`에 입력

---

## 4. 이벤트 구독 및 봇 추가
1. **Event Subscriptions**에서 **Enable Events** ON
2. **Subscribe to bot events**에 `message.channels`, `message.im` 등 필요한 이벤트 추가
3. **Interactivity & Shortcuts**에서 Request URL에 API 서버 주소 입력(필요시)
4. **워크스페이스에 봇 초대**
   - Slack에서 `/invite @봇이름` 명령어로 채널에 초대

---

## 5. Socket Mode 설정

1. 현재 코드(SocketModeHandler)는 Socket Mode를 사용합니다.
2. Slack 앱 설정 > Socket Mode가 Enabled로 설정

---

## 6. .env 파일 예시
```env
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
GEMINI_API_KEY=...
OPENAI_API_KEY=...
```

---

## 7. 실행
```bash
docker-compose up --build
```
또는
```bash
poetry run python src/slackbot/bot.py
```
(로컬 테스트도 가능)
