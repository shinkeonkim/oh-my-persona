#!/usr/bin/env python3

"""
스마트네트워크서비스 AD 프로젝트 메인 실행 파일
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import SmartNetworkApp


def main():
    print("=" * 60)
    print("스마트네트워크서비스 AD 프로젝트")
    print("=" * 60)
    print()
    print("GUI 애플리케이션을 시작합니다...")
    print()

    app = SmartNetworkApp()
    app.mainloop()


if __name__ == "__main__":
    main()
