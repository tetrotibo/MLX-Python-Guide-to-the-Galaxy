# =============================================================================
# D03 - KEY REPEAT: observing X11/XQuartz key autorepeat behavior
# =============================================================================
#
# CONCEPT:
#   X11/XQuartz key autorepeat is off by default in this MLX build.
#   Holding a key fires exactly one KeyPress event. If you want continuous
#   movement while a key is held, you must explicitly enable repeat with
#   mlx_do_key_autorepeaton() - or implement your own held-key tracking
#   using KeyPress and KeyRelease events.
#
# TRY THIS:
#   1. Run the script - hold an arrow key, rectangle moves once then stops.
#   2. Press SPACE to toggle repeat ON (rectangle turns red).
#   3. Hold an arrow key - rectangle moves continuously.
#   4. Press SPACE again to toggle repeat OFF (rectangle turns green).
#
# CONTROLS:
#   Arrow keys:  move rectangle
#   SPACE:       toggle key autorepeat on/off
#   ESC:         quit
#
# =============================================================================

import mlx  # type: ignore
from pathlib import Path
from config import (  # type: ignore
    EVENT_KEY_PRESS, EVENT_WINDOW_CLOSE,
    MASK_KEY_PRESS, MASK_NONE,
    KEY_ESC, KEY_SPACE, KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN,
    C_BG, C_GREEN, C_RED,
)

TITLE = Path(__file__).stem

# =============================================================================
# CONFIG
# =============================================================================

W = 600  # window width in pixels
H = 600  # window height in pixels
RECT_W = 200  # rectangle width in pixels
RECT_H = 200  # rectangle height in pixels
STEP = 50  # pixels per arrow key press
rect_x = (W - RECT_W) // 2  # initial rectangle x position
rect_y = (H - RECT_H) // 2  # initial rectangle y position
repeat_on = False  # current autorepeat state

# =============================================================================
# INIT
# =============================================================================

m = mlx.Mlx()
mlx_ptr = m.mlx_init()
win_ptr = m.mlx_new_window(mlx_ptr, W, H, TITLE)
img_ptr = m.mlx_new_image(mlx_ptr, W, H)
img_addr, _, img_size_line, _ = m.mlx_get_data_addr(img_ptr)

# =============================================================================
# DRAWING PRIMITIVES
# =============================================================================

def write_rect(x: int, y: int, w: int, h: int, color: int) -> None:
    """Fill a rectangle - clamped to prevent buffer overflow."""
    x = max(0, x)
    w = min(w, W - x)
    y = max(0, y)
    h = min(h, H - y)

    if w <= 0 or h <= 0:
        return

    blue = color & 0xFF
    green = (color >> 8) & 0xFF
    red = (color >> 16) & 0xFF
    row = bytearray([blue, green, red, 0xFF] * w)

    for row_offset in range(h):
        start = (y + row_offset) * img_size_line + x * 4
        img_addr[start:start + len(row)] = row

def render_scene() -> None:
    """Draw background and rectangle - green when repeat off, red when on."""
    color = C_RED if repeat_on else C_GREEN
    write_rect(0, 0, W, H, C_BG)
    write_rect(rect_x, rect_y, RECT_W, RECT_H, color)
    m.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 0, 0)

# =============================================================================
# HOOKS
# =============================================================================

def key_press_handler(keycode: int, param) -> int:
    """Handle key press events."""
    global rect_x, rect_y, repeat_on

    if keycode == KEY_ESC:
        m.mlx_loop_exit(mlx_ptr)
    elif keycode == KEY_RIGHT:
        rect_x = min(rect_x + STEP, W - RECT_W)
    elif keycode == KEY_LEFT:
        rect_x = max(rect_x - STEP, 0)
    elif keycode == KEY_DOWN:
        rect_y = min(rect_y + STEP, H - RECT_H)
    elif keycode == KEY_UP:
        rect_y = max(rect_y - STEP, 0)
    elif keycode == KEY_SPACE:
        repeat_on = not repeat_on
        if repeat_on:
            m.mlx_do_key_autorepeaton(mlx_ptr)
            print("key repeat ON")
        else:
            m.mlx_do_key_autorepeatoff(mlx_ptr)
            print("key repeat OFF")
    render_scene()
    return 0

def close_handler(param) -> int:
    """Handle the X button (window close event)."""
    m.mlx_loop_exit(mlx_ptr)
    return 0

m.mlx_hook(win_ptr, EVENT_KEY_PRESS, MASK_KEY_PRESS, key_press_handler, None)
m.mlx_hook(win_ptr, EVENT_WINDOW_CLOSE, MASK_NONE, close_handler, None)

render_scene()

# =============================================================================
# LOOP
# =============================================================================

m.mlx_loop(mlx_ptr)

# =============================================================================
# CLEANUP
# =============================================================================

m.mlx_destroy_image(mlx_ptr, img_ptr)
m.mlx_destroy_window(mlx_ptr, win_ptr)
m.mlx_release(mlx_ptr)
