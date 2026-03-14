# =============================================================================
# E01 - BOUNDS: write_rect overflow (interactive)
# =============================================================================
#
# CONCEPT:
#   write_rect uses raw slice assignment into the image buffer.
#   Vertical overflow exceeds total buffer size - Python raises ValueError.
#   Horizontal overflow stays within the buffer but lands in the wrong row -
#   Python allows it silently. The corrupted pixels appear at the start of
#   the next row - visible as wrapping, but no exception, no warning.
#
# TRY THIS:
#   1. Move the rectangle with arrow keys - it starts centered, moves freely.
#   2. Push it past the right or left edge:
#      -> rect turns YELLOW, no exception, pixels wrap silently to next row
#   3. Push it past the top or bottom edge:
#      -> rect turns RED, ValueError printed to terminal
#   4. Notice horizontal overflow never crashes - silent corruption is
#      always harder to debug than a loud exception.
#
# CONTROLS:
#   Arrow keys:  move rectangle
#   ESC:         quit
#
# =============================================================================

import mlx  # type: ignore
from pathlib import Path
from config import (  # type: ignore
    EVENT_KEY_PRESS, EVENT_WINDOW_CLOSE,
    MASK_KEY_PRESS, MASK_NONE,
    KEY_ESC, KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN,
    C_BG, C_GREEN, C_YELLOW, C_RED,
)

TITLE = Path(__file__).stem

# =============================================================================
# CONFIG
# =============================================================================

W = 600  # window width in pixels
H = 600  # window height in pixels
RECT_W = 300  # rectangle width in pixels
RECT_H = 300  # rectangle height in pixels
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

def write_pixel(x: int, y: int, color: int) -> None:
    """Write one pixel at (x, y) in BGR order. Skips out-of-bounds coords."""
    if not (0 <= x < W and 0 <= y < H):
        return

    i = y * img_size_line + x * 4
    img_addr[i] = color & 0xFF
    img_addr[i + 1] = (color >> 8) & 0xFF
    img_addr[i + 2] = (color >> 16) & 0xFF
    img_addr[i + 3] = 0xFF

def write_rect(x: int, y: int, w: int, h: int, color: int) -> None:
    """Safe write_rect - bounds-clamped, never overflows."""
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

def write_rect_raw(x: int, y: int, w: int, h: int, color: int) -> None:
    """Unguarded write_rect - no clamping, this is what we are testing."""
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
    """Draw background and the test rectangle."""
    write_rect(0, 0, W, H, C_BG)

    h_overflow = (rect_x + RECT_W > W) or (rect_x < 0)
    v_overflow = (rect_y + RECT_H > H) or (rect_y < 0)

    if v_overflow:
        color = C_RED
    elif h_overflow:
        color = C_YELLOW
    else:
        color = C_GREEN

    try:
        write_rect_raw(rect_x, rect_y, RECT_W, RECT_H, color)
    except Exception as e:
        print(f"EXCEPTION: {e}")

    render()

# =============================================================================
# HOOKS
# =============================================================================

def key_press_handler(keycode: int, param) -> int:
    global rect_x, rect_y

    if keycode == KEY_ESC:
        m.mlx_loop_exit(mlx_ptr)
    elif keycode == KEY_RIGHT:
        rect_x += STEP
    elif keycode == KEY_LEFT:
        rect_x -= STEP
    elif keycode == KEY_DOWN:
        rect_y += STEP
    elif keycode == KEY_UP:
        rect_y -= STEP
    render_scene()
    return 0

def close_handler(param) -> int:
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
