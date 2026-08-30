"""12장 연습문제 검증.

    python3 test_ex12.py

스레드와 스케줄링을 다루므로, 시간에 기대는 대신 결정적으로 확인할 수 있게
작업 고리를 손으로 돌린다. SDL 창은 띄우지 않는다.
"""

import threading
import time
import unittest
import urllib.parse

import ex11
import ex12
from ex12 import (Task, TaskQueue, TaskRunner, NetworkThread, MeasureTime,
                  FrameTimeEstimator, FrameScheduler, RasterDrawThread,
                  CommitData, BrowserCore, JSContext, Tab, parallel_fetch,
                  PRIORITY_RENDER, PRIORITY_INPUT, PRIORITY_DEFAULT,
                  PRIORITY_TIMER, STARVATION_LIMIT, REFRESH_RATE_SEC)
from ex10 import URL, Element, tree_to_list


def data_url(html):
    return URL("data:text/html," + urllib.parse.quote(html))


class FakeBrowser(BrowserCore):
    """창 없이 프레임 예약만 세어 본다."""

    def __init__(self):
        super().__init__()
        self.frames_requested = 0

    def set_needs_animation_frame(self, tab):
        self.frames_requested += 1
        super().set_needs_animation_frame(tab)


def make_tab(html, browser=None):
    browser = browser or FakeBrowser()
    tab = Tab(browser, 500)
    browser.tabs.append(tab)
    browser.active_tab = tab
    tab.load(data_url(html))
    tab.force_render()
    return tab


def drain(tab, limit=50):
    """메인 스레드 작업을 손으로 돌린다."""
    for _ in range(limit):
        if not tab.task_runner.run_one():
            return
    raise AssertionError("작업이 끝나지 않습니다")


def wait_for(predicate, timeout=3.0):
    end = time.time() + timeout
    while time.time() < end:
        if predicate():
            return True
        time.sleep(0.01)
    return predicate()


class Exercise121(unittest.TestCase):
    """12-1 setInterval"""

    def make(self, code):
        tab = make_tab("<p>가</p><script>" + code + "</script>")
        return tab

    def test_interval_is_registered(self):
        tab = self.make("window_h = setInterval(function(){}, 10);")
        self.assertEqual(len(tab.js.interval_handles), 1)

    def test_interval_callback_repeats(self):
        tab = self.make("window_n = 0;"
                        "window_h = setInterval(function(){ window_n++ }, 5);")
        handle = next(iter(tab.js.interval_handles))
        for _ in range(3):
            tab.js.dispatch_setinterval(handle, 5)
        self.assertEqual(tab.js.interp.evaljs("window_n"), 3)

    def test_clear_interval_stops_it(self):
        tab = self.make("window_n = 0;"
                        "window_h = setInterval(function(){ window_n++ }, 5);")
        handle = next(iter(tab.js.interval_handles))
        tab.js.dispatch_setinterval(handle, 5)
        tab.js.interp.evaljs("clearInterval(window_h)")
        tab.js.dispatch_setinterval(handle, 5)
        self.assertEqual(tab.js.interp.evaljs("window_n"), 1)

    def test_clearing_from_inside_the_callback_works(self):
        tab = self.make("window_n = 0;"
                        "window_h = setInterval(function(){"
                        "  window_n++; if (window_n == 2) clearInterval(window_h);"
                        "}, 5);")
        handle = next(iter(tab.js.interval_handles))
        for _ in range(5):
            tab.js.dispatch_setinterval(handle, 5)
        self.assertEqual(tab.js.interp.evaljs("window_n"), 2)

    def test_settimeout_runs_only_once(self):
        tab = self.make("window_n = 0;"
                        "setTimeout(function(){ window_n++ }, 5);")
        tab.js.dispatch_settimeout(0)
        tab.js.dispatch_settimeout(0)
        self.assertEqual(tab.js.interp.evaljs("window_n"), 1)

    def test_interval_fires_on_a_real_timer(self):
        tab = self.make("window_n = 0;"
                        "window_h = setInterval(function(){ window_n++ }, 5);")
        wait_for(lambda: len(tab.task_runner.queue) > 0)
        tab.task_runner.run_one()
        self.assertGreaterEqual(tab.js.interp.evaljs("window_n"), 1)
        tab.js.interval_handles.clear()


class Exercise122(unittest.TestCase):
    """12-2 작업 타이밍"""

    def test_task_takes_its_name_from_the_function(self):
        def my_job():
            pass
        self.assertEqual(Task(my_job).name, "my_job")

    def test_running_a_task_records_a_trace_event(self):
        measure = MeasureTime()

        def my_job():
            pass
        Task(my_job, measure=measure).run()
        self.assertIn("Task:my_job", measure.names())

    def test_trace_event_has_a_duration(self):
        measure = MeasureTime()

        def slow():
            time.sleep(0.005)
        Task(slow, measure=measure).run()
        self.assertGreater(measure.durations("Task:slow")[0], 0.001)

    def test_explicit_name_wins(self):
        self.assertEqual(Task(lambda: None, name="직접 지은 이름").name,
                         "직접 지은 이름")

    def test_trace_is_recorded_even_if_the_task_raises(self):
        measure = MeasureTime()

        def boom():
            raise ValueError("일부러")
        with self.assertRaises(ValueError):
            Task(boom, measure=measure).run()
        self.assertIn("Task:boom", measure.names())

    def test_trace_file_is_written(self):
        import json
        import os
        import tempfile
        path = tempfile.mktemp(suffix=".json")
        measure = MeasureTime(path)
        Task(lambda: None, measure=measure, name="x").run()
        measure.finish()
        try:
            with open(path, encoding="utf8") as f:
                self.assertTrue(json.load(f)["traceEvents"])
        finally:
            os.remove(path)


class Exercise123(unittest.TestCase):
    """12-3 시계 기반 프레임 타이밍"""

    def test_first_frame_uses_the_target(self):
        s = FrameScheduler()
        self.assertAlmostEqual(s.delay_until_next(100.0), REFRESH_RATE_SEC,
                               places=4)

    def test_frames_do_not_drift(self):
        """작업이 오래 걸려도 다음 마감은 절대 시각으로 잡힙니다."""
        s = FrameScheduler()
        s.start(0.0)
        # 프레임이 0.020초 걸렸다면 다음까지는 0.013초만 기다리면 된다
        delay = s.delay_until_next(0.020)
        self.assertAlmostEqual(delay, REFRESH_RATE_SEC - 0.020, places=4)

    def test_a_missed_deadline_snaps_to_the_cadence(self):
        s = FrameScheduler()
        s.start(0.0)
        delay = s.delay_until_next(0.100)     # 마감을 세 번 놓쳤다
        self.assertGreater(delay, 0)
        self.assertLessEqual(delay, REFRESH_RATE_SEC + 1e-6)

    def test_delay_is_never_negative(self):
        s = FrameScheduler()
        s.start(0.0)
        self.assertGreaterEqual(s.delay_until_next(10.0), 0)

    def test_fixed_delay_would_drift(self):
        """비교용: 고정 지연이면 프레임마다 작업 시간만큼 밀립니다."""
        fixed, now = [], 0.0
        for _ in range(5):
            now += 0.020 + REFRESH_RATE_SEC     # 작업 20ms + 고정 33ms
            fixed.append(now)
        s = FrameScheduler()
        s.start(0.0)
        clocked, now = [], 0.0
        for _ in range(5):
            now += s.delay_until_next(now)
            clocked.append(now)
            s.next_deadline = now + REFRESH_RATE_SEC
            now += 0.020
        self.assertLess(clocked[-1], fixed[-1], "절대 시각 쪽이 덜 밀립니다")


class Exercise124(unittest.TestCase):
    """12-4 스케줄링"""

    def names(self, queue, count):
        return [queue.next_task().name for _ in range(count)]

    def test_render_goes_first(self):
        q = TaskQueue()
        q.add(Task(lambda: None, priority=PRIORITY_TIMER, name="타이머"))
        q.add(Task(lambda: None, priority=PRIORITY_RENDER, name="렌더"))
        self.assertEqual(q.next_task().name, "렌더")

    def test_input_beats_default(self):
        q = TaskQueue()
        q.add(Task(lambda: None, priority=PRIORITY_DEFAULT, name="보통"))
        q.add(Task(lambda: None, priority=PRIORITY_INPUT, name="입력"))
        self.assertEqual(q.next_task().name, "입력")

    def test_same_priority_keeps_order(self):
        q = TaskQueue()
        for i in range(3):
            q.add(Task(lambda: None, priority=PRIORITY_INPUT, name=str(i)))
        self.assertEqual(self.names(q, 3), ["0", "1", "2"])

    def test_timers_are_not_starved(self):
        q = TaskQueue()
        timer = Task(lambda: None, priority=PRIORITY_TIMER, name="타이머")
        q.add(timer)
        seen = []
        for i in range(STARVATION_LIMIT + 2):
            q.add(Task(lambda: None, priority=PRIORITY_RENDER,
                       name="렌더%d" % i))
            seen.append(q.next_task().name)
        self.assertIn("타이머", seen, "우선순위가 낮아도 언젠가는 돌아야 합니다")

    def test_starved_task_runs_before_its_limit_is_exceeded(self):
        q = TaskQueue()
        q.add(Task(lambda: None, priority=PRIORITY_TIMER, name="타이머"))
        for i in range(STARVATION_LIMIT):
            q.add(Task(lambda: None, priority=PRIORITY_RENDER, name="렌더"))
        for _ in range(STARVATION_LIMIT):
            q.next_task()
        self.assertEqual(q.next_task().name, "타이머")

    def test_empty_queue_is_none(self):
        self.assertIsNone(TaskQueue().next_task())

    def test_runner_drains_in_priority_order(self):
        runner = TaskRunner()
        order = []
        runner.schedule_task(Task(lambda: order.append("타이머"),
                                  priority=PRIORITY_TIMER))
        runner.schedule_task(Task(lambda: order.append("렌더"),
                                  priority=PRIORITY_RENDER))
        runner.run_tasks()
        self.assertEqual(order[0], "렌더")


class Exercise125(unittest.TestCase):
    """12-5 스레드 기반 로딩"""

    def test_results_keep_source_order(self):
        delays = [0.05, 0.01, 0.03]

        def fetch(i):
            time.sleep(delays[i])
            return "결과%d" % i
        out, _ = parallel_fetch([0, 1, 2], fetch)
        self.assertEqual(out, ["결과0", "결과1", "결과2"])

    def test_requests_really_overlap(self):
        def fetch(_):
            time.sleep(0.1)
            return "x"
        start = time.time()
        parallel_fetch(list(range(4)), fetch)
        self.assertLess(time.time() - start, 0.35,
                        "차례로 받으면 0.4초가 걸립니다")

    def test_one_failure_does_not_stop_the_rest(self):
        def fetch(i):
            if i == 1:
                raise RuntimeError("실패")
            return "결과%d" % i
        out, errors = parallel_fetch([0, 1, 2], fetch)
        self.assertEqual(out[0], "결과0")
        self.assertIsNone(out[1])
        self.assertIsNotNone(errors[1])

    def test_empty_list_is_fine(self):
        self.assertEqual(parallel_fetch([], lambda x: x), ([], []))

    def test_stylesheets_apply_in_source_order(self):
        tab = make_tab('<p id="p">글</p>')
        first = Element("link", {"rel": "stylesheet", "href": "a.css"}, None)
        second = Element("link", {"rel": "stylesheet", "href": "b.css"}, None)
        bodies = {"a.css": "p { color: red; }", "b.css": "p { color: blue; }"}

        def sub_request(url):
            time.sleep(0.02 if "a.css" in str(url) else 0.0)
            return bodies["a.css" if "a.css" in str(url) else "b.css"]

        tab.sub_request = sub_request
        tab.url = URL("http://example.com/")
        tab.load_resources([first, second])
        tab.restyle()
        tab.force_render()
        p = next(n for n in tree_to_list(tab.nodes, [])
                 if getattr(n, "tag", None) == "p")
        self.assertEqual(p.style["color"], "blue",
                         "늦게 도착해도 소스 순서가 이깁니다")


class Exercise126(unittest.TestCase):
    """12-6 네트워킹 스레드"""

    def test_network_runner_is_its_own_thread(self):
        net = NetworkThread()
        self.assertEqual(net.thread.name, "네트워킹 스레드")

    def test_tasks_run_on_the_network_thread(self):
        net = NetworkThread()
        net.start_thread()
        seen = []
        net.schedule_task(Task(lambda: seen.append(threading.current_thread().name),
                               name="가져오기"))
        self.assertTrue(wait_for(lambda: seen))
        net.set_needs_quit()
        self.assertEqual(seen[0], "네트워킹 스레드")

    def test_async_xhr_goes_to_the_network_thread(self):
        tab = make_tab("<p>가</p>")
        tab.url = URL("http://example.com/")
        sent = []
        tab.network = type("N", (), {
            "schedule_task": lambda self, task: sent.append(task)})()
        target = URL("http://example.com/x")
        target.request = lambda *a, **k: "응답"
        tab.url.resolve = lambda u: target
        out = tab.js.XMLHttpRequest_send("GET", "/x", "", True, 7)
        self.assertEqual(out, "")
        self.assertEqual(len(sent), 1)

    def test_sync_xhr_does_not_use_the_thread(self):
        tab = make_tab("<p>가</p>")
        tab.url = URL("http://example.com/")
        sent = []
        tab.network = type("N", (), {
            "schedule_task": lambda self, task: sent.append(task)})()
        target = URL("http://example.com/x")
        target.request = lambda *a, **k: "응답"
        tab.url.resolve = lambda u: target
        self.assertEqual(tab.js.XMLHttpRequest_send("GET", "/x", "", False),
                         "응답")
        self.assertEqual(sent, [])

    def test_onload_runs_back_on_the_main_thread(self):
        tab = make_tab('<p>가</p><script>window_got = "";'
                       'var x = new XMLHttpRequest();'
                       'x.onload = function(){ window_got = x.responseText };'
                       "</script>")
        tab.js.interp.evaljs("XHR_REQUESTS[7] = x; x.handle = 7;")
        tab.js.dispatch_xhr_onload("응답 왔다", 7)
        self.assertEqual(tab.js.interp.evaljs("window_got"), "응답 왔다")


class Exercise127(unittest.TestCase):
    """12-7 최적화된 스케줄링"""

    def test_no_samples_means_the_target(self):
        self.assertEqual(FrameTimeEstimator().estimate(), REFRESH_RATE_SEC)

    def test_fast_frames_do_not_go_below_the_target(self):
        est = FrameTimeEstimator()
        for _ in range(5):
            est.record(0.001)
        self.assertEqual(est.estimate(), REFRESH_RATE_SEC)

    def test_slow_frames_raise_the_estimate(self):
        est = FrameTimeEstimator()
        for _ in range(5):
            est.record(0.100)
        self.assertAlmostEqual(est.estimate(), 0.100, places=4)

    def test_window_forgets_old_frames(self):
        est = FrameTimeEstimator(window=3)
        for _ in range(3):
            est.record(0.200)
        for _ in range(3):
            est.record(0.001)
        self.assertEqual(est.estimate(), REFRESH_RATE_SEC)

    def test_scheduler_uses_the_estimate(self):
        est = FrameTimeEstimator()
        for _ in range(5):
            est.record(0.100)
        s = FrameScheduler(est)
        self.assertAlmostEqual(s.delay_until_next(0.0), 0.100, places=4)

    def test_slow_page_is_consistently_slow(self):
        """무작정 따라잡으려 하지 않고 일정한 박자로 느려집니다."""
        est = FrameTimeEstimator()
        s = FrameScheduler(est)
        now, gaps, last = 0.0, [], None
        for _ in range(8):
            now += s.delay_until_next(now)
            if last is not None:
                gaps.append(now - last)
            last = now
            s.frame_started(now)
            now += 0.080                      # 이 페이지는 프레임마다 80ms
            s.frame_finished(now)
        self.assertLess(max(gaps[-3:]) - min(gaps[-3:]), 0.02,
                        "박자가 들쭉날쭉하면 안 됩니다")


class Exercise128(unittest.TestCase):
    """12-8 래스터·그리기 스레드"""

    def test_job_runs_on_the_raster_thread(self):
        rt = RasterDrawThread()
        rt.start_thread()
        seen = []
        rt.submit(lambda: seen.append(threading.current_thread().name))
        self.assertTrue(wait_for(lambda: seen))
        rt.set_needs_quit()
        self.assertEqual(seen[0], "래스터 스레드")

    def test_browser_thread_is_free_while_rastering(self):
        rt = RasterDrawThread()
        rt.start_thread()
        started = threading.Event()
        release = threading.Event()

        def slow_raster():
            started.set()
            release.wait(2)
        rt.submit(slow_raster)
        self.assertTrue(started.wait(2))
        # 래스터가 도는 동안 여기(브라우저 스레드)는 입력을 처리할 수 있다
        handled = []
        handled.append("입력 처리됨")
        self.assertEqual(handled, ["입력 처리됨"])
        release.set()
        rt.wait(2)
        rt.set_needs_quit()

    def test_raster_thread_records_a_trace_event(self):
        measure = MeasureTime()
        rt = RasterDrawThread(measure)
        rt.run_one()                       # 일이 없으면 아무 일도 없다
        rt.submit(lambda: None)
        rt.run_one()
        self.assertIn("RasterAndDraw", measure.names())

    def test_browser_core_uses_the_thread(self):
        rt = RasterDrawThread()
        core = BrowserCore(raster_thread=rt)
        done = []
        core.do_raster_and_draw = lambda: done.append(True)
        core.set_needs_raster_and_draw()
        core.raster_and_draw()
        rt.run_one()
        self.assertEqual(done, [True])

    def test_without_a_thread_it_runs_inline(self):
        core = BrowserCore()
        done = []
        core.do_raster_and_draw = lambda: done.append(True)
        core.set_needs_raster_and_draw()
        core.raster_and_draw()
        self.assertEqual(done, [True])

    def test_nothing_to_draw_is_a_no_op(self):
        core = BrowserCore()
        self.assertFalse(core.raster_and_draw())


class ChapterTwelveBasics(unittest.TestCase):
    """12장 본문 기능 — 커밋, 애니메이션 프레임, 렌더 예약"""

    def test_render_is_skipped_when_nothing_changed(self):
        tab = make_tab("<p>가</p>")
        self.assertFalse(tab.render(), "필요 없으면 다시 그리지 않습니다")

    def test_dom_change_asks_for_a_frame(self):
        browser = FakeBrowser()
        tab = make_tab('<div id="d"></div>', browser)
        before = browser.frames_requested
        tab.js.interp.evaljs("d.innerHTML = '<p>새 글자</p>'")
        self.assertGreater(browser.frames_requested, before)

    def test_animation_frame_produces_commit_data(self):
        tab = make_tab("<p>가</p>")
        data = tab.run_animation_frame(0)
        self.assertIsInstance(data, CommitData)
        self.assertGreater(data.height, 0)

    def test_raf_handlers_run_in_the_frame(self):
        tab = make_tab("<p>가</p><script>window_n = 0;"
                       "requestAnimationFrame(function(){ window_n++ });"
                       "</script>")
        tab.run_animation_frame(0)
        self.assertEqual(tab.js.interp.evaljs("window_n"), 1)

    def test_raf_handlers_run_only_once(self):
        tab = make_tab("<p>가</p><script>window_n = 0;"
                       "requestAnimationFrame(function(){ window_n++ });"
                       "</script>")
        tab.run_animation_frame(0)
        tab.run_animation_frame(0)
        self.assertEqual(tab.js.interp.evaljs("window_n"), 1)

    def test_commit_only_from_the_active_tab(self):
        core = BrowserCore()
        core.active_tab = "탭1"
        core.commit("탭2", CommitData(None, 0, 100, []))
        self.assertEqual(core.active_tab_height, 0)


class CarriedForward(unittest.TestCase):
    """1~11장 연습문제가 그대로 도는지"""

    def test_chapter11_border_radius(self):
        tab = make_tab('<div style="background-color:red;border-radius:10px">'
                       "글</div>")
        self.assertTrue([c for c in tab.flat_display_list
                         if isinstance(c, ex11.DrawRRect)])

    def test_chapter11_blur(self):
        tab = make_tab('<div style="filter:blur(4px)">글</div>')
        self.assertTrue([c for c in tab.flat_display_list
                         if isinstance(c, ex11.Blend) and c.blur > 0])

    def test_chapter10_password(self):
        tab = make_tab('<input name="p" type="password" value="abc">')
        self.assertIn("***", [c.text for c in tab.flat_display_list
                              if hasattr(c, "text")])

    def test_chapter9_dom(self):
        tab = make_tab('<div id="d"><p>가</p>글자<b>나</b></div>')
        self.assertEqual(tab.js.interp.evaljs("d.children.length"), 2)

    def test_chapter5_bullets(self):
        tab = make_tab("<ul><li>하나</li><li>둘</li></ul>")
        black = [c for c in tab.flat_display_list
                 if isinstance(c, ex11.DrawRect) and c.color == "black"]
        self.assertEqual(len(black), 2)

    def test_chapter3_smallcaps(self):
        tab = make_tab("<abbr>abc</abbr>")
        self.assertIn("ABC", "".join(c.text for c in tab.flat_display_list
                                     if hasattr(c, "text")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
