"""작업 큐, 스레드, 프레임 타이밍.

스레드는 셋이다.
    메인 스레드    스타일·배치·그리기·자바스크립트
    네트워킹 스레드 요청 보내고 받기
    래스터 스레드   Skia 로 그리기 (화면에 올리는 일은 주 스레드가 한다)
"""

import json
import sys
import threading
import time

REFRESH_RATE_SEC = 0.033

PRIORITY_RENDER = 0
PRIORITY_INPUT = 1
PRIORITY_DEFAULT = 2
PRIORITY_TIMER = 3

# 우선순위가 낮은 작업이 이만큼 밀리면 먼저 태운다
STARVATION_LIMIT = 5


# ---------------------------------------------------------------------- #
# 트레이싱
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
# 작업
# ---------------------------------------------------------------------- #

class Task:
    def __init__(self, task_code, *args, priority=PRIORITY_DEFAULT,
                 measure=None, name=None):
        self.task_code = task_code
        self.args = args
        self.priority = priority
        self.measure = measure
        # 이름은 실행할 함수 이름에서 딴다
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
    """우선순위를 지키되 굶기지는 않는 큐.

    우선순위가 높은 작업이 계속 들어오면 타이머 작업은 영영 못 돈다.
    작업마다 밀린 횟수를 세어 두고 한계를 넘으면 먼저 태운다.
    """

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
        starved = [t for t in self.tasks if t.skipped >= STARVATION_LIMIT]
        pool = starved or self.tasks
        best = min(pool, key=lambda t: (t.priority, self.tasks.index(t)))
        self.tasks.remove(best)
        for t in self.tasks:
            if t.priority > best.priority:
                t.skipped += 1
        return best


class TaskRunner:
    """작업 고리. 스레드 없이 손으로 돌릴 수도 있다."""

    THREAD_NAME = "메인 스레드"

    def __init__(self, tab=None, measure=None):
        self.tab = tab
        self.measure = measure
        self.queue = TaskQueue()
        self.condition = threading.Condition()
        self.needs_quit = False
        self.thread = threading.Thread(target=self.run, name=self.THREAD_NAME)
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
        """작업 하나를 꺼내 돌린다. 없으면 False.

        작업이 실패해도 고리는 계속 돈다. 페이지 하나를 못 읽었다고 탭이
        통째로 멈추면 안 된다.
        """
        with self.condition:
            task = self.queue.next_task()
        if task is None:
            return False
        try:
            task.run()
        except Exception as e:
            print("작업 %s 가 실패했습니다: %s" % (task.name, e),
                  file=sys.stderr)
        return True

    def run_tasks(self):
        """큐가 빌 때까지."""
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


class NetworkThread(TaskRunner):
    THREAD_NAME = "네트워킹 스레드"


def parallel_fetch(items, fetch):
    """동시에 가져오되 결과는 준 순서 그대로 돌려준다.

    스타일시트는 소스 순서대로 적용돼야 하므로, 늦게 도착한 것이 앞선 것을
    이기면 안 된다.
    """
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
# 프레임 타이밍
# ---------------------------------------------------------------------- #

class FrameTimeEstimator:
    """최근 프레임들이 실제로 얼마나 걸렸는지.

    페이지가 무거워 33ms 를 못 지킬 때, 계속 따라잡으려 하면 CPU 만 태우고
    박자는 들쭉날쭉해진다. 평균을 목표로 삼으면 **일관되게** 느려진다.
    """

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
    """프레임 사이 고정 지연이 아니라 절대 마감으로 잡는다.

    프레임이 끝난 뒤 33ms 를 세면 실제 박자는 `작업 시간 + 33ms` 가 되어
    계속 느려진다.
    """

    def __init__(self, estimator=None, target=REFRESH_RATE_SEC):
        self.target = target
        self.estimator = estimator or FrameTimeEstimator(target=target)
        self.next_deadline = None
        self.frame_start = None

    def start(self, now):
        self.next_deadline = now + self.target

    def delay_until_next(self, now):
        """지금 프레임을 잡으려면 얼마나 기다려야 하는가."""
        period = self.estimator.estimate()
        if self.next_deadline is None:
            self.next_deadline = now + period
            return period
        if self.next_deadline <= now:
            # 마감을 놓쳤으면 지난 만큼을 박자 단위로 건너뛴다
            missed = int((now - self.next_deadline) // period) + 1
            self.next_deadline += missed * period
        return max(0.0, self.next_deadline - now)

    def frame_started(self, now):
        self.frame_start = now

    def frame_finished(self, now):
        self.estimator.record(now - (self.frame_start
                                     if self.frame_start is not None else now))
        self.next_deadline = (self.next_deadline or now) + \
            self.estimator.estimate()


# ---------------------------------------------------------------------- #
# 래스터 스레드
# ---------------------------------------------------------------------- #

class RasterDrawThread:
    """브라우저 스레드가 시키고 이 스레드가 그린다.

    SDL 은 스레드 안전하지 않으므로 **화면에 올리는 일**은 여기서 하지 않고,
    그려 낸 결과를 브라우저 스레드가 가져가게 한다.
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


class CommitData:
    """메인 스레드가 브라우저 스레드에 넘기는 한 프레임의 결과."""

    def __init__(self, url, scroll, height, display_list):
        self.url = url
        self.scroll = scroll
        self.height = height
        self.display_list = display_list
