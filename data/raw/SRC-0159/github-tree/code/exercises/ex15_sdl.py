"""15장 브라우저 셸 — 프레임이 있는 SDL 창.

    python3 ex15_sdl.py http://localhost:8000/
"""

import ctypes
import sys
import time

import sdl2

import ex11
import ex14
import ex15
from ex11 import WIDTH, HEIGHT, SCROLL_STEP
from ex12 import Task, PRIORITY_INPUT, REFRESH_RATE_SEC
from ex14 import ZOOM_STEP, AccessibilityThread, default_speaker
from ex14_sdl import Browser as Browser14
from ex15 import Tab


class Browser(Browser14):
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

    def handle_back(self):
        """연습문제 15-10: 가장 최근에 이동한 프레임에서 뒤로."""
        self.on_tab(lambda tab: tab.go_back(), "go_back")


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
