"""12장 연습문제 구현 (12-1 ~ 12-8).

lab12.py 는 그대로 두고, 1~11장 연습문제를 이어받아 그 위에 12장 기능을 얹는다.
자바스크립트 쪽은 runtime12ex.js, 창과 이벤트 고리는 ex12_sdl.py 에 있다.

    python3 ex12_sdl.py http://localhost:8000/

12장 본문 기능(작업 큐, 메인 스레드와 브라우저 스레드, 커밋, setTimeout,
비동기 XMLHttpRequest, requestAnimationFrame, 트레이싱)에 더해

    12-1 setInterval        되풀이 타이머와 취소
    12-2 작업 타이밍         작업마다 이름 붙은 트레이스 이벤트
    12-3 시계 기반 프레임 타이밍  고정 지연이 아니라 절대 시각으로
    12-4 스케줄링            우선순위 + 굶기지 않기
    12-5 스레드 기반 로딩      병렬로 받되 소스 순서로 처리
    12-6 네트워킹 스레드       네트워크 작업은 따로
    12-7 최적화된 스케줄링     실제 박자를 재서 목표를 조정
    12-8 래스터·그리기 스레드   그리는 동안에도 입력을 받는다
"""

import json
import os
import sys
import threading
import time

import dukpy

import ex10
import ex11
from ex4 import Text, Element
from ex6 import tree_to_list, CSSParser
from ex11 import (Tab as Tab11, DocumentLayout, paint_tree, flatten,
                  WIDTH, HEIGHT, VSTEP, SCROLL_STEP)

HERE = os.path.dirname(os.path.abspath(__file__))
RUNTIME_JS = open(os.path.join(HERE, "runtime12ex.js"), encoding="utf8").read()

REFRESH_RATE_SEC = 0.033

SETTIMEOUT_JS = "__runSetTimeout(dukpy.handle)"
SETINTERVAL_JS = "__runSetInterval(dukpy.handle)"
XHR_ONLOAD_JS = "__runXHROnload(dukpy.out, dukpy.handle)"
RAF_JS = "__runRAFHandlers()"


# ---------------------------------------------------------------------- #
# 트레이싱 (연습문제 12-2)
# ---------------------------------------------------------------------- #

class MeasureTime:
    """Chrome 트레이스 포맷으로 시간을 적어 둔다."""

    def __init__(self, path=None):
        self.path = path
        self.lock = threading.Lock()
        self.events = []            # (이름, 시작, 끝, 스레드)
        self.open = {}

    def time(self, name):
        with self.lock:
            self.open.setdefault(
                (name, threading.get_ident()), []).append(time.time())

    def stop(self, name):
        end = time.time()
        with self.lock:
            key = (name, threading.get_ident())
            stack = self.open.get(key)
            if not stack:
                return None
            start = stack.pop()
            self.events.append((name, start, end, key[1]))
            return end - start

    def names(self):
        with self.lock:
            return [e[0] for e in self.events]

    def durations(self, name):
        with self.lock:
            return [e[2] - e[1] for e in self.events if e[0] == name]

    def finish(self):
        if not self.path:
            return
        with self.lock:
            out = [{"name": name, "ph": "X", "pid": 1, "tid": tid,
                    "ts": start * 1e6, "dur": (end - start) * 1e6}
                   for name, start, end, tid in self.events]
        with open(self.path, "w", encoding="utf8") as f:
            json.dump({"traceEvents": out}, f)


# ---------------------------------------------------------------------- #
# 작업과 작업 큐
# ---------------------------------------------------------------------- #

PRIORITY_RENDER = 0
PRIORITY_INPUT = 1
PRIORITY_DEFAULT = 2
PRIORITY_TIMER = 3
STARVATION_LIMIT = 5          # 연습문제 12-4: 이만큼 밀리면 먼저 태운다


class Task:
    def __init__(self, task_code, *args, priority=PRIORITY_DEFAULT,
                 measure=None, name=None):
        self.task_code = task_code
        self.args = args
        self.priority = priority
        self.measure = measure
        # 연습문제 12-2: 이름은 실행할 함수 이름에서 딴다
        self.name = name or getattr(task_code, "__name__", "task")
        self.skipped = 0

    def run(self):
        label = "Task:" + self.name
        if self.measure:
            self.measure.time(label)
        try:
            return self.task_code(*self.args)
        finally:
            if self.measure:
                self.measure.stop(label)
            self.task_code = None
            self.args = None

    def __repr__(self):
        return "Task(%s, p=%d)" % (self.name, self.priority)


class TaskQueue:
    """연습문제 12-4: 우선순위를 지키되 굶기지는 않는 큐."""

    def __init__(self):
        self.tasks = []

    def __len__(self):
        return len(self.tasks)

    def add(self, task):
        self.tasks.append(task)

    def clear(self):
        self.tasks = []

    def next_task(self):
        if not self.tasks:
            return None
        # 너무 오래 밀린 작업이 있으면 그것부터
        starved = [t for t in self.tasks if t.skipped >= STARVATION_LIMIT]
        pool = starved or self.tasks
        best = min(pool, key=lambda t: (t.priority, self.tasks.index(t)))
        self.tasks.remove(best)
        for t in self.tasks:
            if t.priority > best.priority:
                t.skipped += 1
        return best


class TaskRunner:
    """메인 스레드의 작업 고리. 스레드 없이도 돌릴 수 있다."""

    def __init__(self, tab=None, measure=None, threaded=True):
        self.tab = tab
        self.measure = measure
        self.threaded = threaded
        self.queue = TaskQueue()
        self.condition = threading.Condition()
        self.needs_quit = False
        self.thread = threading.Thread(target=self.run, name="메인 스레드")
        self.thread.daemon = True

    def schedule_task(self, task):
        with self.condition:
            self.queue.add(task)
            self.condition.notify_all()

    def clear_pending_tasks(self):
        with self.condition:
            self.queue.clear()

    def set_needs_quit(self):
        with self.condition:
            self.needs_quit = True
            self.condition.notify_all()

    def start_thread(self):
        self.thread.start()

    def run_one(self):
        """작업 하나를 꺼내 돌린다. 없으면 False."""
        with self.condition:
            task = self.queue.next_task()
        if task is None:
            return False
        task.run()
        return True

    def run_tasks(self):
        """큐가 빌 때까지 (시험용)."""
        count = 0
        while self.run_one():
            count += 1
        return count

    def run(self):
        while True:
            with self.condition:
                if self.needs_quit:
                    return
            if not self.run_one():
                with self.condition:
                    if self.needs_quit:
                        return
                    if len(self.queue) == 0:
                        self.condition.wait(0.01)


# ---------------------------------------------------------------------- #
# 연습문제 12-6: 네트워킹 스레드
# ---------------------------------------------------------------------- #

class NetworkThread(TaskRunner):
    def __init__(self, measure=None):
        super().__init__(None, measure)
        self.thread = threading.Thread(target=self.run, name="네트워킹 스레드")
        self.thread.daemon = True


# ---------------------------------------------------------------------- #
# 연습문제 12-5: 병렬로 받되 소스 순서로 처리
# ---------------------------------------------------------------------- #

def parallel_fetch(items, fetch):
    """items 를 동시에 가져오되, 결과는 준 순서 그대로 돌려준다."""
    results = [None] * len(items)
    errors = [None] * len(items)

    def work(i, item):
        try:
            results[i] = fetch(item)
        except Exception as e:          # 하나가 실패해도 나머지는 계속
            errors[i] = e

    threads = [threading.Thread(target=work, args=(i, item))
               for i, item in enumerate(items)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results, errors


# ---------------------------------------------------------------------- #
# 연습문제 12-3 / 12-7: 프레임 타이밍
# ---------------------------------------------------------------------- #

class FrameTimeEstimator:
    """연습문제 12-7: 최근 프레임들이 실제로 얼마나 걸렸는지."""

    def __init__(self, window=10, target=REFRESH_RATE_SEC):
        self.window = window
        self.target = target
        self.samples = []

    def record(self, duration):
        self.samples.append(duration)
        if len(self.samples) > self.window:
            self.samples.pop(0)

    def estimate(self):
        if not self.samples:
            return self.target
        return max(self.target, sum(self.samples) / len(self.samples))

    def reset(self):
        self.samples = []


class FrameScheduler:
    """연습문제 12-3: 프레임 사이 고정 지연이 아니라 절대 시각으로 잡는다."""

    def __init__(self, estimator=None, target=REFRESH_RATE_SEC):
        self.target = target
        self.estimator = estimator or FrameTimeEstimator(target=target)
        self.next_deadline = None

    def start(self, now):
        self.next_deadline = now + self.target

    def delay_until_next(self, now):
        """지금 프레임을 잡으려면 얼마나 기다려야 하는가."""
        period = self.estimator.estimate()          # 12-7
        if self.next_deadline is None:
            self.next_deadline = now + period
            return period
        # 이미 지난 마감은 박자에 맞춰 앞으로 당긴다 (밀리지 않게)
        if self.next_deadline <= now:
            missed = int((now - self.next_deadline) // period) + 1
            self.next_deadline += missed * period
        delay = self.next_deadline - now
        return max(0.0, delay)

    def frame_started(self, now):
        self.frame_start = now

    def frame_finished(self, now):
        self.estimator.record(now - getattr(self, "frame_start", now))
        self.next_deadline = (self.next_deadline or now) + \
            self.estimator.estimate()


# ---------------------------------------------------------------------- #
# 연습문제 12-8: 래스터·그리기 스레드
# ---------------------------------------------------------------------- #

class RasterDrawThread:
    """브라우저 스레드가 시키고, 이 스레드가 그린다.

    SDL 은 스레드 안전하지 않으므로 **화면에 올리는 일**(blit)은 여기서 하지
    않고, 그려 낸 결과를 브라우저 스레드가 가져가게 한다.
    """

    def __init__(self, measure=None):
        self.measure = measure
        self.condition = threading.Condition()
        self.job = None
        self.needs_quit = False
        self.busy = False
        self.done = threading.Event()
        self.done.set()
        self.thread = threading.Thread(target=self.run, name="래스터 스레드")
        self.thread.daemon = True

    def start_thread(self):
        self.thread.start()

    def submit(self, job):
        with self.condition:
            self.job = job
            self.done.clear()
            self.condition.notify_all()

    def set_needs_quit(self):
        with self.condition:
            self.needs_quit = True
            self.condition.notify_all()

    def run_one(self):
        with self.condition:
            job, self.job = self.job, None
        if job is None:
            return False
        self.busy = True
        if self.measure:
            self.measure.time("RasterAndDraw")
        try:
            job()
        finally:
            if self.measure:
                self.measure.stop("RasterAndDraw")
            self.busy = False
            self.done.set()
        return True

    def run(self):
        while True:
            with self.condition:
                if self.needs_quit:
                    return
                if self.job is None:
                    self.condition.wait(0.01)
            self.run_one()

    def wait(self, timeout=None):
        return self.done.wait(timeout)


# ---------------------------------------------------------------------- #
# 커밋
# ---------------------------------------------------------------------- #

class CommitData:
    def __init__(self, url, scroll, height, display_list):
        self.url = url
        self.scroll = scroll
        self.height = height
        self.display_list = display_list


# ---------------------------------------------------------------------- #
# 자바스크립트
# ---------------------------------------------------------------------- #

class JSContext(ex10.JSContext):
    def __init__(self, tab):
        self.tab = tab
        self.node_to_handle = {}
        self.handle_to_node = {}
        self.id_globals = {}
        self.discarded = False
        self.interval_handles = set()          # 연습문제 12-1

        self.interp = dukpy.JSInterpreter()
        for name in ("log", "querySelectorAll", "getAttribute", "setAttribute",
                     "innerHTML_get", "innerHTML_set", "outerHTML_get",
                     "getChildren", "getParent", "ancestors",
                     "createElement", "createTextNode",
                     "appendChild", "insertBefore", "removeChild",
                     "cookie_get", "cookie_set",
                     "setTimeout", "clearTimeout",
                     "setInterval", "clearInterval",
                     "XMLHttpRequest_send", "requestAnimationFrame"):
            self.interp.export_function(name, getattr(self, name))
        self.interp.evaljs(RUNTIME_JS + "\n0;")

    # -- 타이머 --------------------------------------------------------- #

    def dispatch_settimeout(self, handle):
        if self.discarded:
            return
        self.interp.evaljs(SETTIMEOUT_JS, handle=handle)

    def setTimeout(self, handle, delay):
        def run_callback():
            task = Task(self.dispatch_settimeout, handle,
                        priority=PRIORITY_TIMER, measure=self.tab.measure,
                        name="setTimeout")
            self.tab.task_runner.schedule_task(task)
        threading.Timer(delay / 1000.0, run_callback).start()
        return handle

    def clearTimeout(self, handle):
        return handle

    # -- 연습문제 12-1 -------------------------------------------------- #

    def dispatch_setinterval(self, handle, delay):
        if self.discarded or handle not in self.interval_handles:
            return
        again = self.interp.evaljs(SETINTERVAL_JS, handle=handle)
        if again and handle in self.interval_handles:
            self.arm_interval(handle, delay)

    def arm_interval(self, handle, delay):
        def run_callback():
            if handle not in self.interval_handles:
                return
            task = Task(self.dispatch_setinterval, handle, delay,
                        priority=PRIORITY_TIMER, measure=self.tab.measure,
                        name="setInterval")
            self.tab.task_runner.schedule_task(task)
        timer = threading.Timer(delay / 1000.0, run_callback)
        timer.daemon = True
        timer.start()

    def setInterval(self, handle, delay):
        self.interval_handles.add(handle)
        self.arm_interval(handle, delay)
        return handle

    def clearInterval(self, handle):
        self.interval_handles.discard(handle)
        return handle

    # -- 비동기 요청 ---------------------------------------------------- #

    def dispatch_xhr_onload(self, out, handle):
        if self.discarded:
            return
        self.interp.evaljs(XHR_ONLOAD_JS, out=out, handle=handle)

    def XMLHttpRequest_send(self, method, url, body, is_async=False,
                            handle=None):
        full_url = self.tab.url.resolve(url)
        cross_origin = full_url.origin() != self.tab.url.origin()
        if not self.tab.allowed_request(full_url):
            raise Exception("콘텐츠 보안 정책이 %s 를 막았습니다" % full_url)

        def do_request():
            out = full_url.request(
                referrer=self.tab.url,
                payload=body if method.upper() == "POST" else None,
                origin=self.tab.url.origin() if cross_origin else None,
                referrer_policy=self.tab.referrer_policy,
                top_level=not cross_origin)
            if cross_origin:
                allow = full_url.response_headers.get(
                    "access-control-allow-origin", "")
                if allow not in ("*", self.tab.url.origin()):
                    raise Exception("교차 출처 요청이 허용되지 않았습니다")
            return out

        if not is_async:
            return do_request()

        # 연습문제 12-6: 네트워크는 네트워킹 스레드에서
        def run_load():
            out = do_request()
            self.tab.task_runner.schedule_task(
                Task(self.dispatch_xhr_onload, out, handle,
                     priority=PRIORITY_DEFAULT, measure=self.tab.measure,
                     name="XHR onload"))
        self.tab.network.schedule_task(
            Task(run_load, priority=PRIORITY_DEFAULT,
                 measure=self.tab.measure, name="XHR send"))
        return ""

    # -- 애니메이션 프레임 ---------------------------------------------- #

    def requestAnimationFrame(self):
        self.tab.browser.set_needs_animation_frame(self.tab)


def install_runtime():
    """앞 장의 Tab.load 가 만드는 JSContext 를 12장 것으로 바꿔 끼운다.

    11장에서 그리기 바탕을 갈아 끼운 것과 같은 방법이다.
    """
    ex10.JSContext = JSContext


install_runtime()


# ---------------------------------------------------------------------- #
# 탭
# ---------------------------------------------------------------------- #

class Tab(Tab11):
    def __init__(self, browser, tab_height, task_runner=None, network=None,
                 measure=None):
        super().__init__(tab_height)
        self.browser = browser
        self.measure = measure or MeasureTime()
        self.task_runner = task_runner or TaskRunner(self, self.measure)
        self.network = network or NetworkThread(self.measure)
        self.needs_render = False
        self.js = None

    # -- 렌더 예약 ----------------------------------------------------- #

    def set_needs_render(self):
        self.needs_render = True
        if self.browser is not None:
            self.browser.set_needs_animation_frame(self)

    def restyle(self):
        for node in tree_to_list(self.nodes, []):
            if isinstance(node, Element) and not hasattr(node, "is_focused"):
                node.is_focused = False
        ex10.style(self.nodes, self.all_rules())
        self.set_needs_render()

    def render(self):
        if not self.needs_render:
            return False
        self.measure.time("render")
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)
        self.flat_display_list = flatten(self.display_list)
        self.needs_render = False
        self.measure.stop("render")
        return True

    def force_render(self):
        self.needs_render = True
        self.render()

    def run_animation_frame(self, scroll):
        if scroll is not None:
            self.scroll = scroll
        if self.js is not None:
            self.measure.time("runRAFHandlers")
            self.js.interp.evaljs(RAF_JS)
            self.measure.stop("runRAFHandlers")
        self.render()
        return CommitData(self.url, self.scroll, self.document.height,
                          self.display_list)

    # -- 연습문제 12-5: 자원을 병렬로 받는다 ---------------------------- #

    def load_resources(self, nodes):
        """스타일시트와 스크립트를 한꺼번에 받되, 처리 순서는 소스 순서."""
        links, scripts = [], []
        for node in nodes:
            if not isinstance(node, Element):
                continue
            if node.tag == "link" and "href" in node.attributes \
                    and node.attributes.get("rel") == "stylesheet":
                links.append(node)
            elif node.tag == "script" and "src" in node.attributes:
                scripts.append(node)

        def fetch(node):
            attr = "href" if node.tag == "link" else "src"
            return self.sub_request(self.url.resolve(node.attributes[attr]))

        bodies, _ = parallel_fetch(links + scripts, fetch)
        for node, body in zip(links, bodies[:len(links)]):
            if body is not None:
                self.link_rules[node] = CSSParser(body).parse()
        return dict(zip(scripts, bodies[len(links):]))

    def load(self, url, payload=None, record=True):
        super().load(url, payload, record)
        self.needs_render = True


# ---------------------------------------------------------------------- #
# 브라우저 (창 없는 알맹이)
# ---------------------------------------------------------------------- #

class BrowserCore:
    """스레드와 프레임 예약만 담당한다. 창은 ex12_sdl.py 가 붙인다."""

    def __init__(self, measure=None, raster_thread=None):
        self.measure = measure or MeasureTime()
        self.tabs = []
        self.active_tab = None
        self.lock = threading.Lock()
        self.needs_animation_frame = False
        self.needs_raster_and_draw = False
        self.animation_timer = None
        self.scheduler = FrameScheduler()          # 12-3, 12-7
        self.raster_thread = raster_thread         # 12-8
        self.active_tab_display_list = []
        self.active_tab_height = 0
        self.active_tab_scroll = 0

    # -- 연습문제 12-3 / 12-7 ------------------------------------------ #

    def set_needs_animation_frame(self, tab):
        with self.lock:
            if tab is not self.active_tab:
                return
            self.needs_animation_frame = True

    def schedule_animation_frame(self, now=None):
        now = time.time() if now is None else now
        delay = self.scheduler.delay_until_next(now)

        def callback():
            with self.lock:
                if not self.needs_animation_frame:
                    return
                self.needs_animation_frame = False
                tab = self.active_tab
            if tab is None:
                return
            tab.task_runner.schedule_task(
                Task(tab.run_animation_frame, self.active_tab_scroll,
                     priority=PRIORITY_RENDER, measure=self.measure,
                     name="run_animation_frame"))

        self.animation_timer = threading.Timer(delay, callback)
        self.animation_timer.daemon = True
        self.animation_timer.start()
        return delay

    def commit(self, tab, data):
        with self.lock:
            if tab is not self.active_tab:
                return
            self.active_tab_scroll = data.scroll
            self.active_tab_height = data.height
            self.active_tab_display_list = data.display_list
            self.needs_raster_and_draw = True

    def set_needs_raster_and_draw(self):
        with self.lock:
            self.needs_raster_and_draw = True

    # -- 연습문제 12-8 -------------------------------------------------- #

    def raster_and_draw(self):
        with self.lock:
            if not self.needs_raster_and_draw:
                return False
            self.needs_raster_and_draw = False
        if self.raster_thread is not None:
            self.raster_thread.submit(self.do_raster_and_draw)
        else:
            self.do_raster_and_draw()
        return True

    def do_raster_and_draw(self):
        pass          # 창이 있는 브라우저가 채운다


def main(argv):
    from ex12_sdl import run
    run(argv[0] if argv else ex11.HOME_URL)


if __name__ == "__main__":
    main(sys.argv[1:])
