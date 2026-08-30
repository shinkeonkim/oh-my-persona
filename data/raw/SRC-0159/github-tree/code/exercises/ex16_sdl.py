"""16장 브라우저 셸 — 크기를 조절할 수 있는 SDL 창.

    python3 ex16_sdl.py http://localhost:8000/

연습문제 16-5 가 여기 있다. SDL_WINDOW_RESIZABLE 로 창을 만들고
SDL_WINDOWEVENT_RESIZED 를 받아 프레임을 다시 배치한다.
"""

import ctypes
import sys
import time

import sdl2
import skia

import ex11
import ex14
import ex15
import ex16
from ex11 import HEIGHT, SCROLL_STEP, WIDTH
from ex12 import Task, PRIORITY_INPUT, REFRESH_RATE_SEC
from ex14 import ZOOM_STEP
from ex15_sdl import Browser as Browser15
from ex16 import Tab


class Browser(Browser15):
    def __init__(self, trace_path=None):
        super().__init__(trace_path)
        # 연습문제 16-5: 창 크기를 바꿀 수 있게 다시 만든다
        sdl2.SDL_SetWindowResizable(self.sdl_window, sdl2.SDL_TRUE)
        self.width, self.height = WIDTH, HEIGHT

    def new_tab(self, url):
        tab = Tab(self, HEIGHT - self.chrome.bottom,
                  speaker=self.accessibility,
                  network=self.network, measure=self.measure)
        tab.task_runner.start_thread()
        self.tabs.append(tab)
        self.active_tab = tab

        def load():
            tab.load(url)
            self.commit(tab, tab.run_animation_frame(None))
        tab.task_runner.schedule_task(
            Task(load, priority=PRIORITY_INPUT, measure=self.measure,
                 name="load"))
        return tab

    def handle_resize(self, width, height):
        """연습문제 16-5."""
        if width <= 0 or height <= 0:
            return
        self.width, self.height = width, height
        self.root_surface = skia.Surface.MakeRaster(
            skia.ImageInfo.Make(width, height,
                                ct=skia.kRGBA_8888_ColorType,
                                at=skia.kUnpremul_AlphaType))
        self.chrome_surface = skia.Surface(width, int(self.chrome.bottom))
        self.tab_surface = None
        self.on_tab(lambda tab: tab.resize(width, height - self.chrome.bottom),
                    "resize")
        self.set_needs_raster_and_draw()


def run(url_text, trace_path=None):
    sdl2.SDL_Init(sdl2.SDL_INIT_EVENTS | sdl2.SDL_INIT_VIDEO)
    browser = Browser(trace_path)
    browser.new_tab(ex11.ex10.URL(url_text))

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
                browser.handle_click(event.button.x, event.button.y)
            elif event.type == sdl2.SDL_MOUSEMOTION:
                browser.handle_hover(event.motion.x, event.motion.y)
            elif event.type == sdl2.SDL_MOUSEWHEEL:
                browser.handle_scroll(-event.wheel.y * SCROLL_STEP,
                                      smooth=False)
            elif event.type == sdl2.SDL_KEYDOWN:
                key = event.key.keysym.sym
                if key == sdl2.SDLK_RETURN:
                    browser.handle_enter()
                elif key == sdl2.SDLK_TAB:
                    browser.handle_tab_key()
                elif key == sdl2.SDLK_BACKSPACE and ctrl:
                    browser.handle_back()
                elif key == sdl2.SDLK_DOWN:
                    browser.handle_scroll(SCROLL_STEP)
                elif key == sdl2.SDLK_UP:
                    browser.handle_scroll(-SCROLL_STEP)
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
            elif event.type == sdl2.SDL_TEXTINPUT:
                if not (sdl2.SDL_GetModState() & sdl2.KMOD_CTRL):
                    browser.handle_key(event.text.text.decode("utf8"))

        browser.raster_and_draw()
        browser.blit_if_ready()
        browser.schedule_animation_frame()
        time.sleep(REFRESH_RATE_SEC / 4)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else ex11.HOME_URL)
