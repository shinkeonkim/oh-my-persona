"""브라우저가 들고 있는 스타일시트."""

import os

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "css", "default.css"), encoding="utf8") as f:
    BROWSER_CSS = f.read()

with open(os.path.join(HERE, "css", "chrome.css"), encoding="utf8") as f:
    CHROME_CSS = f.read()
