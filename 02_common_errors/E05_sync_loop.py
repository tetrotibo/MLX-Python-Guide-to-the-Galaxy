# =============================================================================
# E05 - SYNC LOOP: single-threaded synchronous event loop
# =============================================================================
#
# CONCEPT:
#   mlx_loop runs on a single thread. Every hook callback is called
#   directly from inside that thread - there is no parallelism.
#   While a handler executes, the loop is paused. No redraws happen,
#   no other events are processed, no game_loop ticks fire.
#   The freeze is not caused by the sleep itself - it is caused by
#   the loop being unable to advance until the handler returns.
#
# TRY THIS:
#   1. Move the rectangle with arrow keys to confirm it responds.
#   2. Press SPACE - window freezes for 2 seconds.
#      (terminal: "mlx_loop blocked - handler running...")
#   3. While frozen, press arrow keys - nothing moves.
#   4. After the sleep ends, all queued moves fire at once -
#      X11/XQuartz buffered the events but mlx_loop could not process them
#      while blocked inside the handler.
#
# CONTROLS:
#   SPACE:      trigger 2 second freeze
#   Arrow keys: move rectangle
#   ESC:        quit
#
# =============================================================================

import time
import mlx  # type: ignore
from pathlib import Path
from config import (  # type: ignore
    EVENT_KEY_PRESS, EVENT_WINDOW_CLOSE,
    MASK_KEY_PRESS, MASK_NONE,
    KEY_ESC, KEY_SPACE,
    KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN,
    C_BG, C_GREEN,
)

TITLE = Path(__file__).stem

# =============================================================================
# CONFIG
# =============================================================================

W = 600  # window width in pixels
H = 600  # window height in pixels
RECT_W = 200  # rectangle width in pixels
RECT_H = 200  # rectangle height in pixels
STEP = 50     # pixels per arrow key press
rect_x = (W - RECT_W) // 2  # initial rectangle x position
rect_y = (H - RECT_H) // 2  # initial rectangle y position

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

def render() -> None:
    """Push image buffer to window."""
    m.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 0, 0)

def render_scene() -> None:
    """Draw background and rectangle, then push to window."""
    write_rect(0, 0, W, H, C_BG)
    write_rect(rect_x, rect_y, RECT_W, RECT_H, C_GREEN)
    render()

# =============================================================================
# HOOKS
# =============================================================================

def key_press_handler(keycode: int, param) -> int:
    """Handle key press events."""
    global rect_x, rect_y

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
        print("mlx_loop blocked - handler running...")
        time.sleep(2)
        print("handler returned - loop resumes")

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
