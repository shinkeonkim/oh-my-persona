# app — 브라우저 최종본

책 전체를 따라 만든 브라우저를, 장 구분 없이 **하나의 파이썬 패키지**로 다시
쓴 것입니다. `code/` 의 `labN.py` 나 `exN.py` 를 import 하지 않고, 각 부분이
제 자리에 놓인 독립 구현입니다.

- 1~16장 본문 기능 전부
- 연습문제 134개의 구현 전부
- 433개 테스트

## 실행

`app/` 은 `wbe` 라는 이름의 uv 패키지입니다. 저장소 루트에서 한 번만 갖추면 됩니다.

```bash
uv sync
```

그다음 명령 하나로 **서버와 브라우저가 함께** 뜹니다.

```bash
uv run wbe
```

서버(`http://localhost:8000/`)를 띄우고 그 주소를 연 브라우저 창이 열립니다.
창을 닫으면 서버도 함께 내려갑니다. 이미 그 포트에 서버가 있으면 그것을 씁니다.

### 따로 쓰기

| 명령 | 하는 일 |
|---|---|
| `uv run wbe` | 서버 + 브라우저 (기본) |
| `uv run wbe --port 9000` | 다른 포트로 |
| `uv run wbe browse <주소>` | 브라우저만 |
| `uv run wbe <주소>` | 위와 같음 (주소만 줘도 됩니다) |
| `uv run wbe serve [포트]` | 서버만 |
| `uv run wbe test [이름...]` | 테스트 |
| `uv run wbe --trace browser.trace` | 렌더링 트레이스를 남기며 실행 |

```bash
uv run wbe https://browser.engineering/
uv run wbe test test_paint test_layout
```

`uv run python -m wbe ...` 로도 같은 명령을 씁니다.

### 키

| 키 | 하는 일 |
|---|---|
| `Tab` | 다음 포커스 대상 (프레임을 넘나듭니다) |
| `↑` `↓` | 부드러운 스크롤 |
| `Ctrl` + `Backspace` | 뒤로 가기 |
| `Ctrl` + `T` | 새 탭 |
| `Ctrl` + `+` `-` `0` | 확대 / 축소 / 되돌리기 |
| `Ctrl` + `D` | 다크 모드 |
| `Ctrl` + `H` | 고대비 모드 |
| `Ctrl` + `A` | 문서를 한 노드씩 읽기 |

창 크기를 바꿀 수 있고, 마우스 가운데 버튼으로 링크를 새 탭에서 엽니다.
트레이스는 `chrome://tracing` 에서 엽니다.

## 검증

```bash
uv run wbe test
```

433개 테스트가 모두 네트워크와 창 없이 돕니다. Skia 서피스에 직접 그려
확인하고, 말하기는 `RecordingSpeaker` 로 갈아 끼웁니다.

## 구조

```
app/
├─ pyproject.toml   uv 패키지 (이름 wbe)
└─ wbe/
    ├─ cli.py          명령줄 진입점
    ├─ net/            주소와 통신
    │   ├─ url.py          URL 파싱, HTTP 요청, 캐시, 리다이렉트
    │   ├─ cookies.py      쿠키 저장고 (SameSite, HttpOnly, 만료)
    │   └─ security.py     인증서, CSP, X-Frame-Options, CORS
    ├─ dom/            문서 트리
    │   ├─ nodes.py        Text, Element
    │   ├─ parser.py       HTMLParser, SourceParser
    │   └─ serialize.py    innerHTML 을 읽을 때 쓰는 직렬화
    ├─ css/            스타일
    │   ├─ values.py       값 하나하나를 파이썬 값으로
    │   ├─ selectors.py    태그·클래스·id·자손·시퀀스·:has·의사 클래스
    │   ├─ parser.py       선언, @media, @keyframes
    │   ├─ style.py        캐스케이드, 상속, 증분 재계산
    │   ├─ default.css     브라우저 기본 스타일시트
    │   └─ chrome.css      브라우저 크롬용
    ├─ layout/         배치
    │   ├─ fonts.py        Skia 폰트 감싸기
    │   ├─ boxes.py        Document / Block / Line / Text
    │   ├─ embed.py        입력란·버튼·이미지·캔버스·iframe
    │   └─ invalidation.py ProtectedField, FieldStore, 자식 맞추기
    ├─ paint/          그리기
    │   ├─ geometry.py     Rect, 좌표 옮기기, 둥근 모서리 판정
    │   ├─ commands.py     그리기 명령과 시각 효과
    │   ├─ effects.py      효과 씌우기, 디스플레이 리스트 캐시
    │   ├─ compositing.py  페인트 청크, 합성 레이어
    │   └─ hittest.py      좌표를 지역으로 내리며 찾기
    ├─ js/             자바스크립트
    │   ├─ runtime.js      브라우저가 먼저 돌려 두는 스크립트
    │   └─ context.py      DOM API, 이벤트, 타이머, XHR, 캔버스
    ├─ animation.py    이징, 값 보간, 트랜지션, CSS 애니메이션
    ├─ a11y.py         접근성 트리, 포커스 순서, 낭독
    ├─ scheduling.py   작업 큐, 스레드, 프레임 타이밍
    ├─ frame.py        문서 하나 (iframe 안의 문서도 이것)
    ├─ tab.py          프레임 나무와 사용자 동작
    ├─ chrome.py       브라우저 크롬 (HTML+CSS 로 적고 같은 엔진으로 배치)
    ├─ browser.py      창, 탭 목록, 스레드, 화면 갱신
    ├─ server/         시험용 웹 서버 (게시판·로그인·CORS)
    └─ tests/          433개 테스트
```

## `code/` 와 무엇이 다른가

| | `code/` | `app/` |
|---|---|---|
| 나누는 기준 | 장 (`lab5.py`, `ex5.py`) | 관심사 (`css/`, `layout/`) |
| 이어 붙이는 법 | 상속과 이름 바꿔 끼우기 | 곧바로 정의 |
| 읽는 목적 | 장과 장 사이의 **차이** | 다 만들어진 **결과** |

`code/` 의 `exN.py` 는 `ex(N-1).py` 를 상속하고, 장이 바뀔 때마다
`install_backend()` 같은 함수가 앞 장 모듈의 이름을 바꿔 끼웠습니다. 책을
따라가며 "이 장에서 무엇이 달라졌나" 를 보기에는 좋지만, `BlockLayout.layout`
하나가 네 곳에 나뉘어 있어 완성된 코드로 읽기는 어렵습니다.

`app/` 은 그 최종 상태만 담습니다. 상속 사슬도, 바꿔 끼우기도 없습니다.
클래스와 함수 이름은 책과 같게 두어 서로 견주어 볼 수 있습니다.

## 다시 쓰면서 고친 것

**HTTP 캐시가 죽어 있었습니다.** 10장에서 `request()` 를 다시 정의하면서
1장의 캐시 확인이 빠졌습니다. 그 뒤로 어떤 페이지도 캐시되지 않았습니다.
`app/` 에서는 `GET` 요청이 캐시를 지나갑니다 (`POST` 는 서버 상태를 바꾸므로
언제나 다시 보냅니다).

**의사 클래스의 우선순위가 낮았습니다.** `div:hover` 를 `div` 와 같은 무게(1)로
매겼더니, 스타일시트에서 뒤에 나오는 `div` 규칙이 `div:hover` 를 이겼습니다.
실제 CSS 에서 의사 클래스는 클래스와 같은 무게(+10)입니다.

**연결이 하나 잘못되면 서버가 죽었습니다.** 요청 줄이 비어 있으면
`split(" ", 2)` 이 값을 셋 내놓지 못해 터졌습니다. 포트가 열렸는지만 보고
끊는 연결은 아주 흔합니다 — `wbe` 가 서버를 기다릴 때 하는 일이 바로 그것이라,
서버를 띄우자마자 죽었습니다. 이제 모양이 틀린 요청은 조용히 끊고, 연결
처리 전체를 감싸 하나가 잘못돼도 서버는 계속 돕니다.

**페이지를 못 읽으면 탭이 통째로 멈췄습니다.** 인증서 오류만 잡고 나머지는
그대로 올려보내서, 연결 거부 하나가 메인 스레드를 죽였습니다. 이제 오류를
페이지로 보여 주고 계속 갑니다. 작업 고리도 실패한 작업을 삼키고 다음으로
넘어갑니다.

**`about:` 페이지가 순환 참조를 만들었습니다.** `about:bookmarks` 를 만들려면
북마크 목록이 필요한데 그것은 탭이 들고 있습니다. `net/url.py` 에
`register_about(이름, 만드는 함수)` 를 두어, 탭 쪽이 자기를 등록하게 했습니다.

## 필요한 패키지

`dukpy` · `skia-python` · `pysdl2` · `pysdl2-dll` · `PyOpenGL` · `pyttsx3`
(저장소 루트에서 `uv sync`)

---

이 패키지는 책의 내용을 따라 이 저장소에서 새로 작성한 것입니다. 원서의 소스
코드는 `code/` 에 MIT 라이선스로 함께 두었습니다.
