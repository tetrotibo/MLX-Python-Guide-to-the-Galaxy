# =============================================================================
# E06 - TEXT OVERWRITE: mlx_string_put erased by render()
# =============================================================================
#
# CONCEPT:
#   mlx_string_put draws directly to the window, not into the image buffer.
#   Calling render() after it overwrites the text with the image buffer.
#   render() must always come before mlx_string_put, never after.
#
# TRY THIS:
#   1. Run the script - red background, text never appears (broken state).
#   2. Press SPACE - green background, text stays visible (correct state).
#   3. Press SPACE again to toggle back and compare.
#
# CONTROLS:
#   SPACE:  toggle wrong / correct
#   ESC:    quit
#
# =============================================================================

import mlx  # type: ignore
from pathlib import Path
from config import (  # type: ignore
    EVENT_KEY_PRESS, EVENT_WINDOW_CLOSE,
    MASK_KEY_PRESS, MASK_NONE,
    KEY_ESC, KEY_SPACE,
    MLX_CHAR_W, MLX_CHAR_H,
    C_BG, C_GREEN, C_RED, C_WHITE,
)

TITLE = Path(__file__).stem

# =============================================================================
# CONFIG
# =============================================================================

W = 600  # window width in pixels
H = 600  # window height in pixels
RECT_W = 300  # rectangle width in pixels
RECT_H = 40   # rectangle height in pixels
show_correct = False  # current display state - toggled by SPACE

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

def write_rect_centered(w: int, h: int, color: int) -> None:
    """Fill a rectangle centered in the window."""
    write_rect((W - w) // 2, (H - h) // 2, w, h, color)

def render() -> None:
    """Push image buffer to window."""
    m.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 0, 0)

def str_color(color: int) -> int:
    """Convert 0xRRGGBB to 0xBBGGRR for mlx_string_put."""
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    return (b << 16) | (g << 8) | r

def put_text_centered(text: str, color: int) -> None:
    """Draw text centered in the window using mlx_string_put."""
    x = W // 2 - len(text) * MLX_CHAR_W // 2
    y = H // 2 - MLX_CHAR_H // 2 - 4
    m.mlx_string_put(mlx_ptr, win_ptr, x, y, color, text)

def render_wrong() -> None:
    """Broken order: string_put before render() - text never appears."""
    write_rect(0, 0, W, H, C_BG)
    write_rect_centered(RECT_W, RECT_H, C_RED)
    put_text_centered("WRONG - will vanish", str_color(C_WHITE))
    render()  # overwrites the text

def render_correct() -> None:
    """Correct order: render() before string_put - text stays visible."""
    write_rect(0, 0, W, H, C_BG)
    write_rect_centered(RECT_W, RECT_H, C_GREEN)
    render()  # push image buffer first
    put_text_centered("CORRECT - stays visible", str_color(C_WHITE))

# =============================================================================
# HOOKS
# =============================================================================

def key_press_handler(keycode: int, param) -> int:
    """Handle key press events."""
    global show_correct
    if keycode == KEY_ESC:
        m.mlx_loop_exit(mlx_ptr)
    elif keycode == KEY_SPACE:
        show_correct = not show_correct
        if show_correct:
            render_correct()
        else:
            render_wrong()
    return 0

def close_handler(param) -> int:
    """Handle the X button (window close event)."""
    m.mlx_loop_exit(mlx_ptr)
    return 0

m.mlx_hook(win_ptr, EVENT_KEY_PRESS, MASK_KEY_PRESS, key_press_handler, None)
m.mlx_hook(win_ptr, EVENT_WINDOW_CLOSE, MASK_NONE, close_handler, None)

render_wrong()

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
