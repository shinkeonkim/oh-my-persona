"""13장 브라우저 셸 — 합성·래스터·그리기를 나눈 SDL 창.

    python3 ex13_sdl.py http://localhost:8000/
"""

import ctypes
import sys
import time

import sdl2
import skia

import ex11
import ex12
import ex13
from ex11 import WIDTH, HEIGHT, VSTEP, SCROLL_STEP
from ex11_sdl import Chrome
from ex12 import Task, PRIORITY_INPUT, REFRESH_RATE_SEC
from ex12_sdl import Browser as Browser12
from ex13 import Tab, composite, paint_draw_list, draw_list


class Browser(Browser12):
    """12장 브라우저에 합성 단계를 끼워 넣는다."""

    def __init__(self, trace_path=None):
        super().__init__(trace_path)
        self.composited_layers = []
        self.draw_list = []
        self.needs_composite = False

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

    def commit(self, tab, data):
        super().commit(tab, data)
        with self.lock:
            if tab is self.active_tab:
                self.needs_composite = True

    def do_raster_and_draw(self):
        with self.lock:
            display_list = list(self.active_tab_display_list)
            scroll = self.active_tab_scroll
            needs_composite = self.needs_composite
            self.needs_composite = False

        if needs_composite:
            self.measure.time("composite")
            self.composited_layers = composite(display_list)
            self.draw_list = paint_draw_list(self.composited_layers)
            self.measure.stop("composite")

        self.measure.time("raster")
        for layer in self.composited_layers:
            layer.raster()
        self.measure.stop("raster")

        self.measure.time("draw")
        with self.chrome_surface as canvas:
            canvas.clear(skia.ColorWHITE)
            self.chrome.raster(canvas)
        with self.root_surface as canvas:
            canvas.clear(skia.ColorWHITE)
            canvas.save()
            canvas.clipRect(skia.Rect.MakeLTRB(0, self.chrome.bottom,
                                               WIDTH, HEIGHT))
            canvas.translate(0, self.chrome.bottom - scroll)
            draw_list(self.draw_list, canvas)
            canvas.restore()
            canvas.drawImage(self.chrome_surface.makeImageSnapshot(), 0, 0)
        self.measure.stop("draw")
        self.needs_blit.set()

    # -- 연습문제 13-11: 스크롤도 애니메이션 --------------------------- #

    def handle_scroll(self, delta, smooth=True):
        tab = self.active_tab
        if tab is None:
            return
        if not smooth:
            super().handle_scroll(delta)
            return

        def scroll():
            tab.smooth_scroll_by(delta)
            self.commit(tab, tab.run_animation_frame(None))
            self.set_needs_animation_frame(tab)
        self.schedule_on_tab(scroll, name="smooth_scroll")


def run(url_text, trace_path=None):
    sdl2.SDL_Init(sdl2.SDL_INIT_EVENTS | sdl2.SDL_INIT_VIDEO)
    browser = Browser(trace_path)
    browser.new_tab(ex11.ex10.URL(url_text))

    event = sdl2.SDL_Event()
    while True:
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl2.SDL_QUIT:
                browser.handle_quit()
                sdl2.SDL_Quit()
                return
            elif event.type == sdl2.SDL_MOUSEBUTTONUP:
                browser.handle_click(event.button.x, event.button.y)
            elif event.type == sdl2.SDL_MOUSEWHEEL:
                browser.handle_scroll(-event.wheel.y * SCROLL_STEP,
                                      smooth=False)
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
