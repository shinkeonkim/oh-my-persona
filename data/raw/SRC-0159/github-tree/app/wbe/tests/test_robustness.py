"""잘못된 입력과 실패에 견디는가.

브라우저와 서버는 하나가 잘못돼도 통째로 멈추면 안 된다.
"""

import socket
import subprocess
import sys
import time
import unittest

from wbe import cli
from wbe.net.url import URL
from wbe.scheduling import Task, TaskRunner
from wbe.server.__main__ import handle_connection
from wbe.tab import Tab


class FakeConnection:
    """서버 핸들러에 먹일 최소한의 소켓 흉내."""

    def __init__(self, request):
        self.request = request
        self.sent = b""
        self.closed = False

    def makefile(self, mode):
        import io
        return io.BytesIO(self.request)

    def send(self, data):
        self.sent += data

    def close(self):
        self.closed = True


class TestServerSurvives(unittest.TestCase):
    def test_empty_request_line(self):
        """포트가 열렸는지만 보고 끊는 연결이 흔하다."""
        conx = FakeConnection(b"")
        handle_connection(conx)
        self.assertTrue(conx.closed)
        self.assertEqual(conx.sent, b"")

    def test_blank_line_only(self):
        conx = FakeConnection(b"\r\n\r\n")
        handle_connection(conx)
        self.assertTrue(conx.closed)

    def test_garbage_request_line(self):
        conx = FakeConnection("쓰레기\r\n\r\n".encode("utf8"))
        handle_connection(conx)
        self.assertTrue(conx.closed)

    def test_normal_request_still_works(self):
        conx = FakeConnection(b"GET / HTTP/1.0\r\n\r\n")
        handle_connection(conx)
        self.assertIn(b"200 OK", conx.sent)


class TestServerStaysUp(unittest.TestCase):
    PORT = 8170

    def setUp(self):
        self.server = subprocess.Popen(
            [sys.executable, "-m", "wbe.server", str(self.PORT)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.assertTrue(cli.wait_for_port(self.PORT))

    def tearDown(self):
        self.server.terminate()
        self.server.wait(timeout=3)

    def test_survives_the_readiness_probe(self):
        """wait_for_port 는 연결만 하고 끊는다. 그것으로 죽으면 안 된다."""
        time.sleep(0.3)
        self.assertIsNone(self.server.poll())

    def test_survives_a_garbage_connection(self):
        with socket.create_connection(("127.0.0.1", self.PORT)) as s:
            s.sendall(b"\r\n\r\n")
        time.sleep(0.3)
        self.assertIsNone(self.server.poll())

    def test_still_serves_afterwards(self):
        with socket.create_connection(("127.0.0.1", self.PORT)) as s:
            s.sendall(b"\r\n\r\n")
        time.sleep(0.2)
        self.assertIn("게시판",
                      URL("http://localhost:%d/" % self.PORT).request())


class TestBrowserSurvives(unittest.TestCase):
    def test_connection_refused_shows_an_error_page(self):
        tab = Tab(None, 500)
        tab.load(URL("http://localhost:9/"))       # 아무도 안 듣는 포트
        words = " ".join(c.text for c in tab.flat_display_list
                         if hasattr(c, "text"))
        self.assertIn("열 수 없습니다", words)

    def test_tab_is_still_usable(self):
        tab = Tab(None, 500)
        tab.load(URL("http://localhost:9/"))
        self.assertIsNotNone(tab.root_frame)
        self.assertIsNotNone(tab.document)
        self.assertEqual(tab.title(), "페이지를 열 수 없습니다")

    def test_can_load_something_else_after_a_failure(self):
        import urllib.parse
        tab = Tab(None, 500)
        tab.load(URL("http://localhost:9/"))
        tab.load(URL("data:text/html,"
                     + urllib.parse.quote("<p>다음 페이지</p>")))
        words = [c.text for c in tab.flat_display_list if hasattr(c, "text")]
        self.assertIn("다음", words)

    def test_unknown_host_is_an_error_page(self):
        tab = Tab(None, 500)
        tab.load(URL("http://이런호스트는없다.invalid/"))
        words = " ".join(c.text for c in tab.flat_display_list
                         if hasattr(c, "text"))
        self.assertIn("열 수 없습니다", words)


class TestTaskRunnerSurvives(unittest.TestCase):
    def test_failing_task_does_not_kill_the_loop(self):
        runner = TaskRunner()
        done = []

        def boom():
            raise RuntimeError("일부러")
        runner.schedule_task(Task(boom, name="터짐"))
        runner.schedule_task(Task(lambda: done.append(1), name="그다음"))
        runner.run_tasks()
        self.assertEqual(done, [1])

    def test_thread_stays_alive(self):
        runner = TaskRunner()
        runner.start_thread()
        try:
            def boom():
                raise RuntimeError("일부러")
            runner.schedule_task(Task(boom, name="터짐"))
            time.sleep(0.2)
            self.assertTrue(runner.thread.is_alive())
        finally:
            runner.set_needs_quit()


class TestRunAllForReal(unittest.TestCase):
    """`wbe` 가 실제로 서버를 띄우고 그 페이지를 읽어 오는가.

    앞선 테스트는 browse 를 가짜로 갈아 끼워서, 서버가 이미 죽어 있어도
    통과했다. 여기서는 진짜로 읽어 본다.
    """

    PORT = 8171

    def test_server_serves_the_page_the_browser_would_open(self):
        loaded = []
        saved = cli.browse

        def fake_browse(url=None, trace=None):
            loaded.append(URL(url).request())
            return 0

        cli.browse = fake_browse
        try:
            code = cli.run_all(port=self.PORT)
        finally:
            cli.browse = saved
        self.assertEqual(code, 0)
        self.assertEqual(len(loaded), 1)
        self.assertIn("게시판", loaded[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
