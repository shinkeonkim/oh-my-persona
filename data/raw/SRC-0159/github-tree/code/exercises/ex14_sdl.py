"""14장 브라우저 셸 — 확대·다크 모드·접근성이 붙은 SDL 창.

    python3 ex14_sdl.py http://localhost:8000/

키
    Ctrl + '+' / '-' / '0'   확대 / 축소 / 되돌리기
    Ctrl + 'd'               다크 모드
    Ctrl + 'h'               고대비 모드 (연습문제 14-7)
    Ctrl + 'a'               문서를 한 노드씩 읽기 (연습문제 14-3)
    Tab                      다음 포커스 대상
"""

import ctypes
import sys
import time

import sdl2
import skia

import ex11
import ex13
import ex14
from ex11 import WIDTH, HEIGHT, SCROLL_STEP
from ex11_sdl import Chrome
from ex12 import Task, PRIORITY_INPUT, REFRESH_RATE_SEC
from ex13_sdl import Browser as Browser13
from ex14 import Tab, AccessibilityThread, default_speaker, ZOOM_STEP


class Browser(Browser13):
    def __init__(self, trace_path=None):
        super().__init__(trace_path)
        # 연습문제 14-6: 말하기는 접근성 스레드에서
        self.accessibility = AccessibilityThread(default_speaker())
        self.accessibility.start_thread()

    def new_tab(self, url):
        tab = Tab(self, HEIGHT - self.chrome.bottom,
                  speaker=self.accessibility,
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

    def on_tab(self, fn, name):
        tab = self.active_tab
        if tab is None:
            return

        def wrapped():
            fn(tab)
            tab.force_render()
            self.commit(tab, tab.run_animation_frame(None))
        self.schedule_on_tab(wrapped, name=name)

    # -- 접근성 / 확대 -------------------------------------------------- #

    def handle_tab_key(self):
        self.on_tab(lambda tab: tab.advance_tab(), "advance_tab")

    def handle_zoom(self, factor):
        self.on_tab(lambda tab: tab.zoom_by(factor), "zoom")

    def handle_reset_zoom(self):
        self.on_tab(lambda tab: tab.reset_zoom(), "reset_zoom")

    def handle_dark_mode(self):
        def toggle(tab):
            tab.dark_mode = not tab.dark_mode
            tab.restyle()
        self.on_tab(toggle, "dark_mode")

    def handle_forced_colors(self):
        def toggle(tab):
            tab.forced_colors = not tab.forced_colors
            tab.restyle()
        self.on_tab(toggle, "forced_colors")

    def handle_read_next(self):
        self.on_tab(lambda tab: tab.advance_accessibility(),
                    "advance_accessibility")

    def handle_hover(self, x, y):
        if y < self.chrome.bottom:
            return
        self.on_tab(lambda tab: tab.hover(x, y - self.chrome.bottom), "hover")

    def handle_quit(self):
        self.accessibility.set_needs_quit()
        super().handle_quit()


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
