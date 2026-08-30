"""12장 브라우저 셸 — SDL 창, 브라우저 스레드, 래스터·그리기 스레드.

    python3 ex12_sdl.py http://localhost:8000/
"""

import ctypes
import sys
import threading
import time

import sdl2
import skia

import ex10
import ex11
import ex12
from ex11 import WIDTH, HEIGHT, VSTEP, SCROLL_STEP, AOI_HEIGHT
from ex11_sdl import Chrome
from ex12 import (BrowserCore, MeasureTime, NetworkThread, RasterDrawThread,
                  Task, TaskRunner, Tab, PRIORITY_INPUT, REFRESH_RATE_SEC)


class Browser(BrowserCore):
    def __init__(self, trace_path=None):
        super().__init__(MeasureTime(trace_path),
                         raster_thread=RasterDrawThread())
        self.sdl_window = sdl2.SDL_CreateWindow(
            b"wbe-ko", sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED, WIDTH, HEIGHT,
            sdl2.SDL_WINDOW_SHOWN)
        self.root_surface = skia.Surface.MakeRaster(
            skia.ImageInfo.Make(WIDTH, HEIGHT,
                                ct=skia.kRGBA_8888_ColorType,
                                at=skia.kUnpremul_AlphaType))
        self.chrome = Chrome(self)
        self.chrome_surface = skia.Surface(WIDTH, int(self.chrome.bottom))
        self.tab_surface = None
        self.aoi_top = 0
        self.network = NetworkThread(self.measure)
        self.network.start_thread()
        self.raster_thread.measure = self.measure
        self.raster_thread.start_thread()
        self.needs_blit = threading.Event()

    # -- 탭 ------------------------------------------------------------ #

    def new_tab(self, url):
        tab = Tab(self, HEIGHT - self.chrome.bottom,
                  network=self.network, measure=self.measure)
        tab.task_runner.start_thread()
        self.tabs.append(tab)
        self.active_tab = tab

        def load():
            tab.load(url)
            tab.force_render()
            self.commit(tab, tab.run_animation_frame(None))
        tab.task_runner.schedule_task(
            Task(load, priority=PRIORITY_INPUT, measure=self.measure,
                 name="load"))
        return tab

    # -- 래스터와 그리기 (래스터 스레드에서 돈다) ----------------------- #

    def needs_new_aoi(self):
        if self.tab_surface is None:
            return True
        top, bottom = self.aoi_top, self.aoi_top + AOI_HEIGHT
        height = HEIGHT - self.chrome.bottom
        return self.active_tab_scroll < top \
            or self.active_tab_scroll + height > bottom

    def do_raster_and_draw(self):
        with self.lock:
            display_list = list(self.active_tab_display_list)
            scroll = self.active_tab_scroll
            height = self.active_tab_height
        if self.needs_new_aoi():
            want = scroll - (AOI_HEIGHT - (HEIGHT - self.chrome.bottom)) / 2
            limit = max(0, height + 2 * VSTEP - AOI_HEIGHT)
            self.aoi_top = max(0, min(want, limit))
            self.tab_surface = skia.Surface(WIDTH, AOI_HEIGHT)

        with self.tab_surface as canvas:
            canvas.clear(skia.ColorWHITE)
            canvas.save()
            canvas.translate(0, -self.aoi_top)
            for cmd in display_list:
                if cmd.rect.top > self.aoi_top + AOI_HEIGHT:
                    continue
                if cmd.rect.bottom < self.aoi_top:
                    continue
                cmd.execute(canvas)
            canvas.restore()

        with self.chrome_surface as canvas:
            canvas.clear(skia.ColorWHITE)
            self.chrome.raster(canvas)

        with self.root_surface as canvas:
            canvas.clear(skia.ColorWHITE)
            canvas.save()
            canvas.clipRect(skia.Rect.MakeLTRB(0, self.chrome.bottom,
                                               WIDTH, HEIGHT))
            canvas.drawImage(self.tab_surface.makeImageSnapshot(), 0,
                             self.chrome.bottom - (scroll - self.aoi_top))
            canvas.restore()
            canvas.drawImage(self.chrome_surface.makeImageSnapshot(), 0, 0)
        # SDL 은 스레드 안전하지 않다. 화면에 올리는 일은 주 스레드에 맡긴다.
        self.needs_blit.set()

    def blit_if_ready(self):
        if not self.needs_blit.is_set():
            return
        self.needs_blit.clear()
        pixels = self.root_surface.toarray(colorType=skia.kRGBA_8888_ColorType)
        surface = sdl2.SDL_CreateRGBSurfaceFrom(
            pixels.ctypes.data, WIDTH, HEIGHT, 32, WIDTH * 4,
            0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000)
        rect = sdl2.SDL_Rect(0, 0, WIDTH, HEIGHT)
        window_surface = sdl2.SDL_GetWindowSurface(self.sdl_window)
        sdl2.SDL_BlitSurface(surface, rect, window_surface, rect)
        sdl2.SDL_UpdateWindowSurface(self.sdl_window)

    # -- 입력: 브라우저 스레드가 곧바로 받는다 -------------------------- #

    def schedule_on_tab(self, fn, *args, name="input"):
        tab = self.active_tab
        if tab is None:
            return
        tab.task_runner.schedule_task(
            Task(fn, *args, priority=PRIORITY_INPUT, measure=self.measure,
                 name=name))

    def handle_click(self, x, y):
        self.measure.time("handle_click")
        if y < self.chrome.bottom:
            self.chrome.click(x, y)
            self.set_needs_raster_and_draw()
        else:
            tab = self.active_tab

            def click():
                tab.click(x, y - self.chrome.bottom)
                tab.force_render()
                self.commit(tab, tab.run_animation_frame(None))
            self.schedule_on_tab(click, name="click")
        self.measure.stop("handle_click")

    def handle_key(self, char):
        if not (0x20 <= ord(char) < 0x7f):
            return
        if self.chrome.focus:
            self.chrome.keypress(char)
            self.set_needs_raster_and_draw()
        else:
            tab = self.active_tab

            def key():
                tab.keypress(char)
                tab.force_render()
                self.commit(tab, tab.run_animation_frame(None))
            self.schedule_on_tab(key, name="keypress")

    def handle_enter(self):
        if self.chrome.focus == "address bar":
            url = ex11.ex10.address_to_url(self.chrome.address.text)
            self.chrome.focus = None
            self.chrome.render()
            tab = self.active_tab

            def go():
                tab.load(url)
                tab.force_render()
                self.commit(tab, tab.run_animation_frame(None))
            self.schedule_on_tab(go, name="load")
        self.set_needs_raster_and_draw()

    def handle_scroll(self, delta):
        with self.lock:
            self.active_tab_scroll = max(
                0, min(self.active_tab_scroll + delta,
                       max(0, self.active_tab_height + 2 * VSTEP
                           - (HEIGHT - self.chrome.bottom))))
            self.needs_raster_and_draw = True

    def handle_quit(self):
        for tab in self.tabs:
            tab.task_runner.set_needs_quit()
        self.network.set_needs_quit()
        self.raster_thread.set_needs_quit()
        self.measure.finish()
        sdl2.SDL_DestroyWindow(self.sdl_window)


def run(url_text, trace_path=None):
    sdl2.SDL_Init(sdl2.SDL_INIT_EVENTS | sdl2.SDL_INIT_VIDEO)
    browser = Browser(trace_path)
    browser.new_tab(ex11.ex10.URL(url_text))

    event = sdl2.SDL_Event()
    while True:
        # 래스터 스레드가 그리는 동안에도 여기서 입력을 받는다 (연습문제 12-8)
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl2.SDL_QUIT:
                browser.handle_quit()
                sdl2.SDL_Quit()
                return
            elif event.type == sdl2.SDL_MOUSEBUTTONUP:
                browser.handle_click(event.button.x, event.button.y)
            elif event.type == sdl2.SDL_MOUSEWHEEL:
                browser.handle_scroll(-event.wheel.y * SCROLL_STEP)
            elif event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_RETURN:
                    browser.handle_enter()
                elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                    browser.handle_scroll(SCROLL_STEP)
                elif event.key.keysym.sym == sdl2.SDLK_UP:
                    browser.handle_scroll(-SCROLL_STEP)
            elif event.type == sdl2.SDL_TEXTINPUT:
                browser.handle_key(event.text.text.decode("utf8"))

        browser.raster_and_draw()
        browser.blit_if_ready()
        browser.schedule_animation_frame()
        time.sleep(REFRESH_RATE_SEC / 4)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else ex11.HOME_URL)
