"""브라우저 — 창, 탭 목록, 스레드, 화면 갱신.

브라우저 스레드는 입력을 받고 프레임을 예약한다. 스타일·배치·자바스크립트는
탭마다의 메인 스레드가, 그리기는 래스터 스레드가 맡는다. 화면에 올리는 일만
주 스레드가 한다 — SDL 이 스레드 안전하지 않기 때문이다.
"""

import threading
import time

import skia

from wbe.a11y import AccessibilityThread, default_speaker
from wbe.chrome import Chrome
from wbe.net.url import URL
from wbe.paint.compositing import composite, draw_list, paint_draw_list
from wbe.paint.geometry import AOI_HEIGHT, HEIGHT, VSTEP, WIDTH
from wbe.scheduling import (MeasureTime, NetworkThread, PRIORITY_INPUT,
                            PRIORITY_RENDER, RasterDrawThread,
                            REFRESH_RATE_SEC, FrameScheduler, Task)
from wbe.tab import HOME_URL, Tab, ZOOM_STEP

TOUCH_SCROLL_SCALE = 4 * HEIGHT


class Browser:
    def __init__(self, headless=False, trace_path=None):
        self.headless = headless
        self.measure = MeasureTime(trace_path)
        self.width, self.height = WIDTH, HEIGHT

        self.tabs = []
        self.active_tab = None
        self.lock = threading.Lock()
        self.scheduler = FrameScheduler()
        self.needs_animation_frame = False
        self.needs_raster_and_draw = False
        self.needs_composite = False
        self.animation_timer = None

        self.active_tab_display_list = []
        self.active_tab_height = 0
        self.active_tab_scroll = 0
        self.composited_layers = []
        self.draw_list = []
        self.aoi_top = 0

        self.network = NetworkThread(None, self.measure)
        self.raster_thread = RasterDrawThread(self.measure)
        self.accessibility = AccessibilityThread(default_speaker())
        self.touch_points = {}
        self.needs_blit = threading.Event()

        self.chrome = Chrome(self)
        self.sdl_window = None
        self.tab_surface = None
        # Skia 서피스는 창이 없어도 만들 수 있다. 창 없이 그려 보는 시험이
        # 그대로 돌게 하려고 headless 에서도 만들어 둔다.
        self.make_surfaces()
        if not headless:
            self.open_window()

    # ------------------------------------------------------------------ #
    # 창
    # ------------------------------------------------------------------ #

    def open_window(self):
        import sdl2
        self.sdl_window = sdl2.SDL_CreateWindow(
            b"wbe-ko", sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED, self.width, self.height,
            sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_RESIZABLE)

    def make_surfaces(self):
        self.root_surface = skia.Surface.MakeRaster(
            skia.ImageInfo.Make(self.width, self.height,
                                ct=skia.kRGBA_8888_ColorType,
                                at=skia.kUnpremul_AlphaType))
        self.chrome_surface = skia.Surface(self.width,
                                           max(1, int(self.chrome.bottom)))
        self.tab_surface = None

    def start_threads(self):
        self.network.start_thread()
        self.raster_thread.start_thread()
        self.accessibility.start_thread()

    # ------------------------------------------------------------------ #
    # 탭
    # ------------------------------------------------------------------ #

    def new_tab(self, url, background=False):
        tab = Tab(self, self.height - self.chrome.bottom,
                  speaker=self.accessibility, network=self.network,
                  measure=self.measure)
        tab.width = self.width
        self.tabs.append(tab)
        if not background or self.active_tab is None:
            self.active_tab = tab
        tab.task_runner.start_thread()
        self.schedule_on(tab, lambda: self.load_and_commit(tab, url),
                         name="load")
        return tab

    def load_and_commit(self, tab, url):
        tab.load(url)
        self.commit(tab, tab.run_animation_frame())

    def load_in_active_tab(self, url):
        tab = self.active_tab
        if tab is not None:
            self.schedule_on(tab, lambda: self.load_and_commit(tab, url),
                             name="load")

    def schedule_on(self, tab, fn, name="input"):
        tab.task_runner.schedule_task(
            Task(fn, priority=PRIORITY_INPUT, measure=self.measure,
                 name=name))

    def on_active_tab(self, fn, name="input"):
        """활성 탭에서 무언가 하고 그 결과를 커밋한다."""
        tab = self.active_tab
        if tab is None:
            return

        def wrapped():
            fn(tab)
            self.commit(tab, tab.run_animation_frame())
        self.schedule_on(tab, wrapped, name)

    # ------------------------------------------------------------------ #
    # 프레임 예약과 커밋
    # ------------------------------------------------------------------ #

    def set_needs_animation_frame(self, tab):
        with self.lock:
            if tab is self.active_tab:
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
                Task(lambda: self.commit(tab, tab.run_animation_frame(
                    self.active_tab_scroll)),
                    priority=PRIORITY_RENDER, measure=self.measure,
                    name="run_animation_frame"))

        self.animation_timer = threading.Timer(delay, callback)
        self.animation_timer.daemon = True
        self.animation_timer.start()
        return delay

    def commit(self, tab, data):
        if data is None:
            return
        with self.lock:
            if tab is not self.active_tab:
                return
            self.active_tab_scroll = data.scroll
            self.active_tab_height = data.height
            self.active_tab_display_list = data.display_list
            self.needs_raster_and_draw = True
            self.needs_composite = True

    def set_needs_raster_and_draw(self):
        with self.lock:
            self.needs_raster_and_draw = True

    # ------------------------------------------------------------------ #
    # 래스터와 그리기
    # ------------------------------------------------------------------ #

    def raster_and_draw(self):
        with self.lock:
            if not self.needs_raster_and_draw:
                return False
            self.needs_raster_and_draw = False
        if self.raster_thread.thread.is_alive():
            self.raster_thread.submit(self.do_raster_and_draw)
        else:
            self.do_raster_and_draw()
        return True

    def needs_new_aoi(self):
        if self.tab_surface is None:
            return True
        view = self.height - self.chrome.bottom
        return self.active_tab_scroll < self.aoi_top \
            or self.active_tab_scroll + view > self.aoi_top + AOI_HEIGHT

    def do_raster_and_draw(self):
        with self.lock:
            display_list = list(self.active_tab_display_list)
            scroll = self.active_tab_scroll
            height = self.active_tab_height
            needs_composite = self.needs_composite
            self.needs_composite = False

        if needs_composite or not self.composited_layers:
            self.measure.time("composite")
            self.composited_layers = composite(display_list)
            self.draw_list = paint_draw_list(self.composited_layers)
            self.measure.stop("composite")

        # 관심 영역 — 화면 둘레만 들고 있는다
        if self.needs_new_aoi():
            view = self.height - self.chrome.bottom
            want = scroll - (AOI_HEIGHT - view) / 2
            limit = max(0, height + 2 * VSTEP - AOI_HEIGHT)
            self.aoi_top = max(0, min(want, limit))
            self.tab_surface = skia.Surface(self.width, AOI_HEIGHT)

        self.measure.time("raster")
        for layer in self.composited_layers:
            layer.raster()
        with self.tab_surface as canvas:
            canvas.clear(skia.ColorWHITE)
            canvas.save()
            canvas.translate(0, -self.aoi_top)
            draw_list(self.draw_list, canvas)
            canvas.restore()
        self.measure.stop("raster")

        self.measure.time("draw")
        with self.chrome_surface as canvas:
            canvas.clear(skia.ColorWHITE)
            self.chrome.raster(canvas)
        with self.root_surface as canvas:
            canvas.clear(skia.ColorWHITE)
            canvas.save()
            canvas.clipRect(skia.Rect.MakeLTRB(0, self.chrome.bottom,
                                               self.width, self.height))
            canvas.drawImage(self.tab_surface.makeImageSnapshot(), 0,
                             self.chrome.bottom - (scroll - self.aoi_top))
            canvas.restore()
            canvas.drawImage(self.chrome_surface.makeImageSnapshot(), 0, 0)
        self.measure.stop("draw")
        self.needs_blit.set()

    def blit_if_ready(self):
        if self.headless or not self.needs_blit.is_set():
            return
        import sdl2
        self.needs_blit.clear()
        pixels = self.root_surface.toarray(
            colorType=skia.kRGBA_8888_ColorType)
        surface = sdl2.SDL_CreateRGBSurfaceFrom(
            pixels.ctypes.data, self.width, self.height, 32, self.width * 4,
            0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000)
        rect = sdl2.SDL_Rect(0, 0, self.width, self.height)
        window_surface = sdl2.SDL_GetWindowSurface(self.sdl_window)
        sdl2.SDL_BlitSurface(surface, rect, window_surface, rect)
        sdl2.SDL_UpdateWindowSurface(self.sdl_window)

    # ------------------------------------------------------------------ #
    # 입력
    # ------------------------------------------------------------------ #

    def handle_click(self, x, y, new_tab=False):
        if y < self.chrome.bottom:
            if self.active_tab is not None:
                self.on_active_tab(lambda tab: tab.click(-1, -1), "blur")
            self.chrome.click(x, y)
            self.set_needs_raster_and_draw()
            return
        self.chrome.blur()
        page_y = y - self.chrome.bottom
        if new_tab:
            # 가운데 클릭 — 링크를 새 탭에서 연다
            tab = self.active_tab
            if tab is None:
                return
            url = self.link_at(tab, x, page_y)
            if url is not None:
                self.new_tab(url, background=True)
            return
        self.on_active_tab(lambda tab: tab.click(x, page_y), "click")

    def link_at(self, tab, x, y):
        from wbe.dom.nodes import Element
        from wbe.net.url import resolve
        node = tab.node_at(x, y)
        frame = tab.frame_at(node) if node is not None else tab.root_frame
        while node is not None:
            if isinstance(node, Element) and node.tag == "a" \
                    and "href" in node.attributes:
                return resolve(frame.url, node.attributes["href"])
            node = node.parent
        return None

    def handle_key(self, char):
        if not (0x20 <= ord(char) < 0x7f):
            return
        if self.chrome.keypress(char):
            self.set_needs_raster_and_draw()
        else:
            self.on_active_tab(lambda tab: tab.keypress(char), "keypress")

    def handle_backspace(self):
        if self.chrome.backspace():
            self.set_needs_raster_and_draw()
        else:
            self.on_active_tab(lambda tab: tab.backspace(), "backspace")

    def handle_enter(self):
        if self.chrome.enter():
            self.set_needs_raster_and_draw()
        else:
            self.on_active_tab(lambda tab: tab.enter(), "enter")

    def handle_tab_key(self):
        self.on_active_tab(lambda tab: tab.advance_tab(), "advance_tab")

    def handle_scroll(self, delta, smooth=True):
        tab = self.active_tab
        if tab is None:
            return
        if not smooth:
            with self.lock:
                view = self.height - self.chrome.bottom
                limit = max(0, self.active_tab_height + 2 * VSTEP - view)
                self.active_tab_scroll = max(
                    0, min(self.active_tab_scroll + delta, limit))
                self.needs_raster_and_draw = True
            return

        def scroll(t):
            t.smooth_scroll_by(delta)
        self.on_active_tab(scroll, "smooth_scroll")
        self.set_needs_animation_frame(tab)

    def handle_hover(self, x, y):
        if y < self.chrome.bottom:
            return
        self.on_active_tab(
            lambda tab: tab.hover(x, y - self.chrome.bottom), "hover")

    def go_back(self):
        self.on_active_tab(lambda tab: tab.go_back(), "go_back")

    def go_forward(self):
        self.on_active_tab(lambda tab: tab.go_forward(), "go_forward")

    def handle_zoom(self, factor):
        self.on_active_tab(lambda tab: tab.zoom_by(factor), "zoom")

    def handle_reset_zoom(self):
        self.on_active_tab(lambda tab: tab.reset_zoom(), "reset_zoom")

    def handle_dark_mode(self):
        self.on_active_tab(lambda tab: tab.toggle_dark_mode(), "dark_mode")

    def handle_forced_colors(self):
        self.on_active_tab(lambda tab: tab.toggle_forced_colors(),
                           "forced_colors")

    def handle_read_next(self):
        self.on_active_tab(lambda tab: tab.advance_accessibility(),
                           "advance_accessibility")

    def handle_resize(self, width, height):
        if width <= 0 or height <= 0:
            return
        self.width, self.height = width, height
        self.chrome.render()
        self.make_surfaces()
        self.on_active_tab(
            lambda tab: tab.resize(width, height - self.chrome.bottom),
            "resize")
        self.set_needs_raster_and_draw()

    # -- 터치 ----------------------------------------------------------- #

    def handle_finger_down(self, finger):
        self.touch_points[finger.fingerId] = (finger.x, finger.y)

    def handle_finger_up(self, finger):
        start = self.touch_points.pop(finger.fingerId, None)
        if start is None or self.touch_points:
            return                       # 두 손가락 이상이면 탭이 아니다
        dx = abs(finger.x - start[0]) * self.width
        dy = abs(finger.y - start[1]) * self.height
        if dx < 10 and dy < 10:          # 거의 안 움직였으면 탭 = 클릭
            self.handle_click(finger.x * self.width, finger.y * self.height)

    def handle_finger_motion(self, finger):
        if len(self.touch_points) < 2:
            return                       # 두 손가락 끌기만 스크롤로 본다
        self.touch_points[finger.fingerId] = (finger.x, finger.y)
        self.handle_scroll(-finger.dy * TOUCH_SCROLL_SCALE, smooth=False)

    def handle_multi_gesture(self, gesture):
        if gesture.numFingers >= 2:
            self.handle_scroll(-gesture.dDist * TOUCH_SCROLL_SCALE,
                               smooth=False)

    # ------------------------------------------------------------------ #
    # 끝내기
    # ------------------------------------------------------------------ #

    def set_title(self):
        if self.headless or self.active_tab is None:
            return
        import sdl2
        sdl2.SDL_SetWindowTitle(
            self.sdl_window, self.active_tab.title().encode("utf8"))

    def handle_quit(self):
        for tab in self.tabs:
            tab.task_runner.set_needs_quit()
        self.network.set_needs_quit()
        self.raster_thread.set_needs_quit()
        self.accessibility.set_needs_quit()
        self.measure.finish()
        if not self.headless:
            import sdl2
            sdl2.SDL_DestroyWindow(self.sdl_window)


# ---------------------------------------------------------------------- #
# 이벤트 고리
# ---------------------------------------------------------------------- #

def run(url_text=None, trace_path=None):
    import ctypes

    import sdl2

    sdl2.SDL_Init(sdl2.SDL_INIT_EVENTS | sdl2.SDL_INIT_VIDEO)
    browser = Browser(trace_path=trace_path)
    browser.start_threads()
    browser.new_tab(URL(url_text or HOME_URL))

    event = sdl2.SDL_Event()
    while True:
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            ctrl = sdl2.SDL_GetModState() & sdl2.KMOD_CTRL
            if event.type == sdl2.SDL_QUIT:
                browser.handle_quit()
                sdl2.SDL_Quit()
                return
            elif event.type == sdl2.SDL_WINDOWEVENT:
                if event.window.event == sdl2.SDL_WINDOWEVENT_RESIZED:
                    browser.handle_resize(event.window.data1,
                                          event.window.data2)
            elif event.type == sdl2.SDL_MOUSEBUTTONUP:
                browser.handle_click(
                    event.button.x, event.button.y,
                    new_tab=(event.button.button == sdl2.SDL_BUTTON_MIDDLE))
            elif event.type == sdl2.SDL_MOUSEMOTION:
                browser.handle_hover(event.motion.x, event.motion.y)
            elif event.type == sdl2.SDL_MOUSEWHEEL:
                browser.handle_scroll(-event.wheel.y * 100, smooth=False)
            elif event.type == sdl2.SDL_KEYDOWN:
                key = event.key.keysym.sym
                if key == sdl2.SDLK_RETURN:
                    browser.handle_enter()
                elif key == sdl2.SDLK_TAB:
                    browser.handle_tab_key()
                elif key == sdl2.SDLK_BACKSPACE:
                    if ctrl:
                        browser.go_back()
                    else:
                        browser.handle_backspace()
                elif key == sdl2.SDLK_DOWN:
                    browser.handle_scroll(100)
                elif key == sdl2.SDLK_UP:
                    browser.handle_scroll(-100)
                elif key == sdl2.SDLK_LEFT:
                    browser.chrome.left()
                    browser.set_needs_raster_and_draw()
                elif key == sdl2.SDLK_RIGHT:
                    browser.chrome.right()
                    browser.set_needs_raster_and_draw()
                elif ctrl and key in (sdl2.SDLK_PLUS, sdl2.SDLK_EQUALS):
                    browser.handle_zoom(ZOOM_STEP)
                elif ctrl and key == sdl2.SDLK_MINUS:
                    browser.handle_zoom(1 / ZOOM_STEP)
                elif ctrl and key == sdl2.SDLK_0:
                    browser.handle_reset_zoom()
                elif ctrl and key == sdl2.SDLK_d:
                    browser.handle_dark_mode()
                elif ctrl and key == sdl2.SDLK_h:
                    browser.handle_forced_colors()
                elif ctrl and key == sdl2.SDLK_a:
                    browser.handle_read_next()
                elif ctrl and key == sdl2.SDLK_t:
                    browser.new_tab(URL(HOME_URL))
            elif event.type == sdl2.SDL_TEXTINPUT:
                if not (sdl2.SDL_GetModState() & sdl2.KMOD_CTRL):
                    browser.handle_key(event.text.text.decode("utf8"))
            elif event.type == sdl2.SDL_FINGERDOWN:
                browser.handle_finger_down(event.tfinger)
            elif event.type == sdl2.SDL_FINGERUP:
                browser.handle_finger_up(event.tfinger)
            elif event.type == sdl2.SDL_FINGERMOTION:
                browser.handle_finger_motion(event.tfinger)
            elif event.type == sdl2.SDL_MULTIGESTURE:
                browser.handle_multi_gesture(event.mgesture)

        browser.raster_and_draw()
        browser.blit_if_ready()
        browser.set_title()
        browser.schedule_animation_frame()
        time.sleep(REFRESH_RATE_SEC / 4)
