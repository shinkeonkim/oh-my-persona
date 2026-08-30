"""11장 브라우저 셸 — SDL 창과 이벤트 고리.

    python3 ex11_sdl.py http://localhost:8000/

여기 담긴 연습문제
    11-3 관심 영역   화면 둘레 AOI_HEIGHT 만큼만 래스터해 둔다
    11-5 터치 입력   탭은 클릭으로, 두 손가락 끌기는 스크롤로
"""

import ctypes
import sys

import sdl2
import skia

import ex10
import ex11
from ex11 import (WIDTH, HEIGHT, VSTEP, SCROLL_STEP, AOI_HEIGHT, Tab,
                  paint_tree, flatten, DocumentLayout)

TOUCH_SCROLL_SCALE = 4 * HEIGHT      # 연습문제 11-5: 정규화 좌표 -> 픽셀


class Chrome(ex10.HTMLChrome):
    """9~10장 HTML 크롬을 11장 배치·그리기로 다시 만든다."""

    def render(self):
        self.nodes = ex11.ex10.HTMLParser(self.html()).parse()
        for node in ex11.tree_to_list(self.nodes, []):
            if isinstance(node, ex11.Element):
                node.is_focused = (self.focus == "address bar"
                                   and node.attributes.get("id") == "address")
        ex11.ex10.style(self.nodes, self.rules)
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)
        self.flat_display_list = flatten(self.display_list)
        self.bottom = self.document.height + 2 * VSTEP

    def paint(self):
        return [ex11.DrawRect(ex11.Rect(0, 0, WIDTH, self.bottom), "white")] \
            + self.display_list \
            + [ex11.DrawLine(0, self.bottom, WIDTH, self.bottom, "black", 1)]

    def node_at(self, x, y):
        for cmd in reversed(self.flat_display_list):
            if cmd.node is None:
                continue
            if isinstance(cmd, (ex11.Blend, ex11.Translate)):
                continue
            if ex11.hit(cmd, x, y):
                return cmd.node
        return None

    def raster(self, canvas):
        for cmd in self.paint():
            cmd.execute(canvas)


class Browser:
    def __init__(self):
        self.sdl_window = sdl2.SDL_CreateWindow(
            b"wbe-ko", sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED, WIDTH, HEIGHT,
            sdl2.SDL_WINDOW_SHOWN)
        self.root_surface = skia.Surface.MakeRaster(
            skia.ImageInfo.Make(WIDTH, HEIGHT,
                                ct=skia.kRGBA_8888_ColorType,
                                at=skia.kUnpremul_AlphaType))
        self.chrome_surface = None
        self.tab_surface = None
        self.aoi_top = 0                     # 연습문제 11-3

        self.tabs = []
        self.active_tab = None
        self.chrome = Chrome(self)
        self.chrome_surface = skia.Surface(WIDTH, int(self.chrome.bottom))
        self.touch_points = {}               # 연습문제 11-5

    # -- 탭 ------------------------------------------------------------ #

    def new_tab(self, url, background=False):
        tab = Tab(HEIGHT - self.chrome.bottom)
        tab.load(url)
        self.tabs.append(tab)
        if not background or self.active_tab is None:
            self.active_tab = tab
        self.chrome.render()
        self.raster_and_draw()
        return tab

    # -- 연습문제 11-3 -------------------------------------------------- #

    def needs_new_aoi(self):
        tab = self.active_tab
        if self.tab_surface is None:
            return True
        top, bottom = self.aoi_top, self.aoi_top + AOI_HEIGHT
        return tab.scroll < top or tab.scroll + tab.tab_height > bottom

    def recenter_aoi(self):
        tab = self.active_tab
        want = tab.scroll - (AOI_HEIGHT - tab.tab_height) / 2
        limit = max(0, tab.document.height + 2 * VSTEP - AOI_HEIGHT)
        self.aoi_top = max(0, min(want, limit))

    def raster_tab(self):
        tab = self.active_tab
        if self.needs_new_aoi():
            self.recenter_aoi()
            self.tab_surface = skia.Surface(WIDTH, AOI_HEIGHT)
        with self.tab_surface as canvas:
            tab.raster(canvas, self.aoi_top)

    def raster_chrome(self):
        with self.chrome_surface as canvas:
            canvas.clear(skia.ColorWHITE)
            self.chrome.raster(canvas)

    def raster_and_draw(self):
        if self.active_tab is None:
            return
        self.raster_chrome()
        self.raster_tab()
        with self.root_surface as canvas:
            canvas.clear(skia.ColorWHITE)
            tab_image = self.tab_surface.makeImageSnapshot()
            # 관심 영역 안에서 화면에 보일 부분만 오려 붙인다
            offset = self.active_tab.scroll - self.aoi_top
            canvas.save()
            canvas.clipRect(skia.Rect.MakeLTRB(
                0, self.chrome.bottom, WIDTH, HEIGHT))
            canvas.drawImage(tab_image, 0, self.chrome.bottom - offset)
            canvas.restore()
            canvas.drawImage(self.chrome_surface.makeImageSnapshot(), 0, 0)
        self.blit()

    def blit(self):
        pixels = self.root_surface.toarray(
            colorType=skia.kRGBA_8888_ColorType)
        surface = sdl2.SDL_CreateRGBSurfaceFrom(
            pixels.ctypes.data, WIDTH, HEIGHT, 32, WIDTH * 4,
            0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000)
        rect = sdl2.SDL_Rect(0, 0, WIDTH, HEIGHT)
        window_surface = sdl2.SDL_GetWindowSurface(self.sdl_window)
        sdl2.SDL_BlitSurface(surface, rect, window_surface, rect)
        sdl2.SDL_UpdateWindowSurface(self.sdl_window)

    # -- 입력 ---------------------------------------------------------- #

    def handle_click(self, x, y):
        if y < self.chrome.bottom:
            if self.active_tab is not None:
                self.active_tab.blur()
            self.chrome.click(x, y)
        else:
            self.chrome.blur()
            self.active_tab.click(x, y - self.chrome.bottom)
        self.raster_and_draw()

    def handle_key(self, char):
        if not (0x20 <= ord(char) < 0x7f):
            return
        if self.chrome.focus:
            self.chrome.keypress(char)
        elif self.active_tab is not None:
            self.active_tab.keypress(char)
        self.raster_and_draw()

    def handle_enter(self):
        if not self.chrome.enter():
            if self.active_tab is not None:
                self.active_tab.enter()
        self.chrome.render()
        self.raster_and_draw()

    def handle_backspace(self):
        if self.chrome.focus:
            self.chrome.backspace()
        elif self.active_tab is not None:
            self.active_tab.backspace()
        self.raster_and_draw()

    def handle_scroll(self, delta):
        self.active_tab.scroll_by(delta)
        self.raster_and_draw()

    # -- 연습문제 11-5: 터치 ------------------------------------------- #

    def handle_finger_down(self, event):
        f = event.tfinger
        self.touch_points[f.fingerId] = (f.x, f.y)

    def handle_finger_up(self, event):
        f = event.tfinger
        start = self.touch_points.pop(f.fingerId, None)
        if start is None or self.touch_points:
            return                     # 두 손가락 이상이면 탭이 아니다
        dx = abs(f.x - start[0]) * WIDTH
        dy = abs(f.y - start[1]) * HEIGHT
        if dx < 10 and dy < 10:        # 거의 안 움직였으면 탭 = 클릭
            self.handle_click(f.x * WIDTH, f.y * HEIGHT)

    def handle_finger_motion(self, event):
        f = event.tfinger
        if len(self.touch_points) < 2:
            return                     # 두 손가락 끌기만 스크롤로 본다
        self.touch_points[f.fingerId] = (f.x, f.y)
        self.handle_scroll(-f.dy * TOUCH_SCROLL_SCALE)

    def handle_multi_gesture(self, event):
        """두 손가락 끌기(SDL_MultiGestureEvent)를 스크롤로."""
        g = event.mgesture
        if g.numFingers >= 2:
            self.handle_scroll(-g.dDist * TOUCH_SCROLL_SCALE)


def run(url_text):
    sdl2.SDL_Init(sdl2.SDL_INIT_EVENTS | sdl2.SDL_INIT_VIDEO)
    browser = Browser()
    browser.new_tab(ex11.ex10.URL(url_text))

    event = sdl2.SDL_Event()
    while True:
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl2.SDL_QUIT:
                sdl2.SDL_DestroyWindow(browser.sdl_window)
                sdl2.SDL_Quit()
                return
            elif event.type == sdl2.SDL_MOUSEBUTTONUP:
                browser.handle_click(event.button.x, event.button.y)
            elif event.type == sdl2.SDL_MOUSEWHEEL:
                browser.handle_scroll(-event.wheel.y * SCROLL_STEP)
            elif event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_RETURN:
                    browser.handle_enter()
                elif event.key.keysym.sym == sdl2.SDLK_BACKSPACE:
                    browser.handle_backspace()
                elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                    browser.handle_scroll(SCROLL_STEP)
                elif event.key.keysym.sym == sdl2.SDLK_UP:
                    browser.handle_scroll(-SCROLL_STEP)
            elif event.type == sdl2.SDL_TEXTINPUT:
                browser.handle_key(event.text.text.decode("utf8"))
            elif event.type == sdl2.SDL_FINGERDOWN:
                browser.handle_finger_down(event)
            elif event.type == sdl2.SDL_FINGERUP:
                browser.handle_finger_up(event)
            elif event.type == sdl2.SDL_FINGERMOTION:
                browser.handle_finger_motion(event)
            elif event.type == sdl2.SDL_MULTIGESTURE:
                browser.handle_multi_gesture(event)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else ex11.HOME_URL)
