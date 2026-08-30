# 코드

책을 따라 만든 브라우저 전체입니다. 1~16장의 코드가 한 폴더에 모여 있습니다.

## 어느 장의 브라우저를 볼 것인가

`labN.py` 가 **N장까지 따라 만들면 완성되는 브라우저**입니다. 그 장에서 새로
생기거나 바뀐 코드만 담고 나머지는 이전 장 파일에서 import 하므로, 파일 하나로
장과 장 사이에 무엇이 달라졌는지 바로 볼 수 있습니다.

```bash
python3 lab5.py https://browser.engineering/     # 5장 시점의 브라우저
python3 lab10.py http://localhost:8000/          # 10장 시점의 브라우저
```

11장부터는 Skia 와 SDL 을 씁니다.

```bash
python3 lab11.py https://browser.engineering/
```

각 장 시점에 무엇을 할 수 있는지는 그 장 폴더의 `결과물.md` 에 정리해 두었습니다.

## 서버가 필요한 장

8장부터는 폼을 받아 줄 서버가 필요합니다.

```bash
python3 server8.py      # 8~9장   (다른 터미널에서)
python3 server10.py     # 10장부터
```

## 연습문제

본문 연습문제 134개를 모두 구현한 코드가 [`exercises/`](exercises/) 에 있습니다.

```bash
cd exercises
python3 test_ex6.py                              # 6장까지의 연습문제 검증
python3 ex6.py https://browser.engineering/      # 연습문제가 반영된 6장 브라우저
```

`labN.py` 는 손대지 않고 `exN.py` 를 따로 두었습니다. 책 본문이 "연습문제를 풀지
않았다고 가정한다"고 밝히고 있어, 연습문제를 반영하면 이후 장의 코드 조각과
어긋나기 때문입니다. `exN.py` 는 `ex(N-1).py` 를 이어받으므로 **1장부터의 모든
연습문제가 누적된 채로** 발전합니다. 그래서 `labN.py` 와 `exN.py` 를 나란히 놓고
견주어 볼 수 있습니다.

각 장 폴더의 `연습문제.md` 에 그 장 연습문제의 구현 위치와 설계 판단이 있습니다.

## 전체 검증

```bash
cd exercises
for n in $(seq 1 16); do python3 test_ex$n.py; done
```

904개 테스트가 모두 네트워크 없이 돕니다. 11장부터는 Skia 서피스에 직접 그려
확인하므로 창을 띄우지 않습니다.

## 필요한 패키지

| 패키지 | 쓰는 곳 |
|---|---|
| `dukpy` | 9장부터 (JavaScript) |
| `skia-python`, `pysdl2`, `pysdl2-dll` | 11장부터 (그리기·창) |
| `PyOpenGL` | 13장부터 |
| `pyttsx3` | 14장 연습문제 (소리 내어 읽기) |

저장소 루트에서 `uv sync` 로 한 번에 갖춰집니다.

---

코드 출처: [browserengineering/book](https://github.com/browserengineering/book) 의
`src/` — © 2018–2023 Pavel Panchekha & Chris Harrelson, MIT 라이선스.
`labN.py` 와 에셋은 원문 그대로이며 라이선스 전문은 같은 폴더의 `LICENSE` 에
있습니다. `exercises/` 는 이 저장소에서 작성한 연습문제 구현입니다.
