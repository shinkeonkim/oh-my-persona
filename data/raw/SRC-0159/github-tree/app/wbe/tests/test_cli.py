"""명령줄 — 인자 해석과 한 번에 실행."""

import time
import unittest

from wbe import cli


class TestParsing(unittest.TestCase):
    def parse(self, argv):
        return cli.build_parser().parse_args(argv)

    def test_default_is_all(self):
        self.assertIsNone(self.parse([]).command)

    def test_browse_takes_a_url(self):
        args = self.parse(["browse", "https://example.com/"])
        self.assertEqual((args.command, args.url),
                         ("browse", "https://example.com/"))

    def test_serve_takes_a_port(self):
        self.assertEqual(self.parse(["serve", "9000"]).port, 9000)

    def test_serve_has_a_default_port(self):
        self.assertEqual(self.parse(["serve"]).port, cli.DEFAULT_PORT)

    def test_test_takes_names(self):
        self.assertEqual(self.parse(["test", "test_net"]).names, ["test_net"])

    def test_trace_flag(self):
        self.assertEqual(self.parse(["--trace", "x.trace", "browse"]).trace,
                         "x.trace")


class TestDispatch(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.saved = (cli.browse, cli.serve, cli.test, cli.run_all)
        cli.browse = lambda url=None, trace=None: \
            (self.calls.append(("browse", url, trace)), 0)[1]
        cli.serve = lambda port=cli.DEFAULT_PORT: \
            (self.calls.append(("serve", port)), 0)[1]
        cli.test = lambda names=(): (self.calls.append(("test", names)), 0)[1]
        cli.run_all = lambda port=cli.DEFAULT_PORT, url=None, trace=None: \
            (self.calls.append(("all", port, url)), 0)[1]

    def tearDown(self):
        cli.browse, cli.serve, cli.test, cli.run_all = self.saved

    def test_no_args_runs_everything(self):
        cli.main([])
        self.assertEqual(self.calls[0][0], "all")

    def test_bare_url_becomes_browse(self):
        """`wbe https://...` 처럼 주소만 줘도 받아 준다."""
        cli.main(["https://example.com/"])
        self.assertEqual(self.calls[0][:2],
                         ("browse", "https://example.com/"))

    def test_browse_subcommand(self):
        cli.main(["browse", "http://localhost:8000/"])
        self.assertEqual(self.calls[0][0], "browse")

    def test_serve_subcommand(self):
        cli.main(["serve", "9001"])
        self.assertEqual(self.calls[0], ("serve", 9001))

    def test_test_subcommand(self):
        cli.main(["test", "test_dom"])
        self.assertEqual(self.calls[0], ("test", ["test_dom"]))

    def test_trace_reaches_browse(self):
        cli.main(["--trace", "x.trace", "browse"])
        self.assertEqual(self.calls[0][2], "x.trace")


class TestRunAll(unittest.TestCase):
    PORT = 8151

    def test_starts_the_server_and_points_the_browser_at_it(self):
        opened = []
        saved = cli.browse
        cli.browse = lambda url=None, trace=None: \
            (opened.append(url), 0)[1]
        try:
            code = cli.run_all(port=self.PORT)
        finally:
            cli.browse = saved
        self.assertEqual(code, 0)
        self.assertEqual(opened, ["http://localhost:%d/" % self.PORT])

    def test_server_is_shut_down_afterwards(self):
        saved = cli.browse
        cli.browse = lambda url=None, trace=None: 0
        try:
            cli.run_all(port=self.PORT + 1)
        finally:
            cli.browse = saved
        deadline = time.time() + 3
        while time.time() < deadline and cli.port_is_open(self.PORT + 1):
            time.sleep(0.05)
        self.assertFalse(cli.port_is_open(self.PORT + 1))

    def test_reuses_a_server_that_is_already_up(self):
        import subprocess
        import sys
        port = self.PORT + 2
        server = subprocess.Popen(
            [sys.executable, "-m", "wbe.server", str(port)],
            stdout=subprocess.DEVNULL)
        try:
            self.assertTrue(cli.wait_for_port(port))
            saved = cli.browse
            cli.browse = lambda url=None, trace=None: 0
            try:
                cli.run_all(port=port)
            finally:
                cli.browse = saved
            # 우리가 띄우지 않았으므로 내리지도 않는다
            self.assertTrue(cli.port_is_open(port))
        finally:
            server.terminate()
            server.wait(timeout=3)

    def test_port_helpers(self):
        self.assertFalse(cli.port_is_open(1))
        self.assertFalse(cli.wait_for_port(1, timeout=0.3))


if __name__ == "__main__":
    unittest.main(verbosity=2)
