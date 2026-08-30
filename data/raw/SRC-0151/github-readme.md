<p align="center">
<img width="304" height="102" alt="Image" src="https://github.com/user-attachments/assets/7c5e0376-56ff-490b-9811-1f8170304b28" />
</p>

> 터미널 스타일 ASCII 명함 생성기 — neofetch 감성의 개발자 명함을 만들어보세요.

![TermCard](https://img.shields.io/badge/TermCard-v1.0.0-brightgreen?style=flat-square&logo=terminal)

<p align="center">
  <img width="2062" height="1280" alt="Image" src="https://github.com/user-attachments/assets/51a23f05-4792-4528-9989-1452d30e5a8c" />
</p>

## ✨ Features

- **4가지 스타일** — `neofetch`, `boxcard`, `dotart`, `biglogo`
- **6가지 컬러 테마** — Matrix, Frost, Amber, Sakura, Ocean, Grape
- **한글 완벽 지원** — CJK 문자 폭 계산으로 테두리 정렬 유지
- **타이핑 애니메이션** — 터미널 느낌의 출력 효과
- **PNG 다운로드** — 생성된 명함을 이미지로 저장
- **텍스트 복사** — 클립보드에 ASCII 텍스트 복사
- **Python CLI** — 터미널에서 직접 명함 생성

## 🖥️ 웹 사용법

[TermCard 웹앱](https://term-card.xn--hy1by51c.kr/)에서 정보를 입력하고 **Generate** 버튼을 클릭하세요.

## 🐍 Python CLI 사용법

### 요구 사항

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

### 실행

```bash
# 다운로드
curl -O https://raw.githubusercontent.com/kokoa-lab/term-card/main/public/termcard.py

# 실행 권한 부여
chmod +x termcard.py

# 실행
./termcard.py --name "홍길동" --title "개발자" --github "gildong" --skills "React,TypeScript"

# 스타일과 테마 선택
./termcard.py --style box --theme cyan --name "Jane" --title "Backend Dev"

# 도움말
./termcard.py --help
```

### CLI 옵션
| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--name` | 이름 (필수) | — |
| `--title` | 직함 | — |
| `--github` | GitHub 사용자명 | — |
| `--email` | 이메일 | — |
| `--website` | 웹사이트 URL | — |
| `--skills` | 기술 스택 (쉼표 구분) | — |
| `--style` | 카드 스타일 (`neofetch`, `box`, `dotart`, `biglogo`) | `neofetch` |
| `--theme` | 컬러 테마 (`green`, `cyan`, `amber`, `rose`, `blue`, `purple`) | `green` |
### 출력 예시
```
   .+------+.      shinkeonkim
   |  ><>   |      -----------
   |   .--. |      Title: Developer
   |   |##| |      GitHub: github.com/shinkeonkim
   |   '--' |      Stack: React, TypeScript
   |  TERM  |
   |  CARD  |      ### ### ### ### ### ### ### ###
   '+------+'
```
## 🛠️ 기술 스택
- **Frontend** — React, TypeScript, Vite
- **Styling** — Tailwind CSS, shadcn/ui
- **Font** — Nanum Gothic Coding (한글/영문 고정폭)
- **CLI** — Python, Typer, Rich
## 📦 로컬 개발
```bash
git clone https://github.com/kokoa-lab/term-card.git
cd term-card
npm install
npm run dev
```

## 👤 Author

**shinkeonkim** — [github.com/shinkeonkim](https://github.com/shinkeonkim)

## 📄 License

MIT
