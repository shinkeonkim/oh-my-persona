"""명령줄 진입점.

    wbe                    서버와 브라우저를 한 번에 띄운다
    wbe browse [주소]       브라우저만
    wbe serve [포트]        서버만
    wbe test [이름...]      테스트
"""

import argparse
import os
import socket
import subprocess
import sys
import time
import unittest

DEFAULT_PORT = 8000
DEFAULT_HOME = "https://browser.engineering/"


# ---------------------------------------------------------------------- #
# 하나씩
# ---------------------------------------------------------------------- #

def browse(url=None, trace=None):
    """브라우저 창을 띄운다."""
    from wbe.browser import run
    run(url or DEFAULT_HOME, trace)
    return 0


def serve(port=DEFAULT_PORT):
    """시험용 웹 서버를 띄운다."""
    from wbe.server.__main__ import main as server_main
    server_main([str(port)])
    return 0


def test(names=()):
    """테스트를 돌린다."""
    loader = unittest.TestLoader()
    if names:
        suite = loader.loadTestsFromNames(
            ["wbe.tests." + n if not n.startswith("wbe.") else n
             for n in names])
    else:
        suite = loader.discover(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests"),
            top_level_dir=os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


# ---------------------------------------------------------------------- #
# 한 번에
# ---------------------------------------------------------------------- #

def port_is_open(port, host="127.0.0.1"):
    with socket.socket() as s:
        s.settimeout(0.2)
        return s.connect_ex((host, port)) == 0


def wait_for_port(port, timeout=10.0):
    end = time.time() + timeout
    while time.time() < end:
        if port_is_open(port):
            return True
        time.sleep(0.1)
    return False


def run_all(port=DEFAULT_PORT, url=None, trace=None):
    """서버를 띄우고, 그 서버를 가리키는 브라우저를 연다.

    브라우저를 닫으면 서버도 함께 내린다.
    """
    if port_is_open(port):
        print("포트 %d 에 이미 서버가 있습니다. 그것을 씁니다." % port)
        server = None
    else:
        print("서버를 띄웁니다 (포트 %d)" % port)
        server = subprocess.Popen(
            [sys.executable, "-m", "wbe.server", str(port)],
            stdout=subprocess.DEVNULL)
        if not wait_for_port(port):
            server.terminate()
            print("서버가 뜨지 않았습니다.", file=sys.stderr)
            return 1

    try:
        return browse(url or "http://localhost:%d/" % port, trace)
    finally:
        if server is not None:
            print("서버를 내립니다")
            server.terminate()
            try:
                server.wait(timeout=3)
            except subprocess.TimeoutExpired:
                server.kill()


# ---------------------------------------------------------------------- #
# 명령줄 해석
# ---------------------------------------------------------------------- #

def build_parser():
    parser = argparse.ArgumentParser(
        prog="wbe",
        description="Web Browser Engineering 을 따라 만든 브라우저")
    parser.add_argument("--trace", metavar="파일",
                        help="렌더링 트레이스를 남긴다 (chrome://tracing)")
    sub = parser.add_subparsers(dest="command")

    p_all = sub.add_parser("all", help="서버와 브라우저를 한 번에 (기본)")
    p_all.add_argument("--port", type=int, default=DEFAULT_PORT)
    p_all.add_argument("url", nargs="?")

    p_browse = sub.add_parser("browse", help="브라우저만")
    p_browse.add_argument("url", nargs="?")

    p_serve = sub.add_parser("serve", help="서버만")
    p_serve.add_argument("port", nargs="?", type=int, default=DEFAULT_PORT)

    p_test = sub.add_parser("test", help="테스트")
    p_test.add_argument("names", nargs="*")

    return parser


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    # `wbe https://...` 처럼 주소만 준 경우를 browse 로 받아 준다
    if argv and not argv[0].startswith("-") and \
            argv[0] not in ("all", "browse", "serve", "test"):
        argv.insert(0, "browse")

    args = build_parser().parse_args(argv)
    command = args.command or "all"

    if command == "browse":
        return browse(args.url, args.trace)
    if command == "serve":
        return serve(args.port)
    if command == "test":
        return test(args.names)
    return run_all(getattr(args, "port", DEFAULT_PORT),
                   getattr(args, "url", None), args.trace)


if __name__ == "__main__":
    sys.exit(main())
