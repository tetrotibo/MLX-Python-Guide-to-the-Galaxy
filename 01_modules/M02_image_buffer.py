# =============================================================================
# M02 - IMAGE BUFFER: pixel buffer system and drawing workflow
# =============================================================================
#
# CONCEPTS:
#   - Why you should NEVER draw directly to the window
#   - mlx_new_image() and mlx_get_data_addr()
#   - What img_addr actually is (raw writable byte buffer)
#   - img_size_line: row stride from mlx_get_data_addr
#   - Pixel format: BGR + alpha, 4 bytes per pixel
#   - write_pixel(): fundamental drawing primitive
#   - write_rect(): fast rectangle fill using row slice assignment
#   - mlx_put_image_to_window(): pushing buffer to screen
#
# WHAT WE ARE BUILDING:
#   A window filled with colored rectangles, drawn by writing directly
#   into a raw memory buffer and pushing it to screen all at once.
#
# CONTROLS:
#   ESC:    quit
#
# =============================================================================

import mlx  # type: ignore
from pathlib import Path
from config import (  # type: ignore
    EVENT_KEY_PRESS, EVENT_WINDOW_CLOSE,
    MASK_KEY_PRESS, MASK_NONE,
    KEY_ESC,
    C_BG,
    C_RED, C_GREEN, C_BLUE,
    C_CYAN, C_MAGENTA, C_YELLOW,
)

TITLE = Path(__file__).stem

# =============================================================================
# CONFIG
# =============================================================================

W = 800  # window width in pixels
H = 600  # window height in pixels
CENTER_X = W // 2  # horizontal center in pixels
CENTER_Y = H // 2  # vertical center in pixels

# =============================================================================
# INIT
# =============================================================================

m = mlx.Mlx()
mlx_ptr = m.mlx_init()
win_ptr = m.mlx_new_window(mlx_ptr, W, H, TITLE)

"""Allocates an off-screen pixel buffer - nothing is drawn to screen yet.
Signature: mlx_new_image(mlx_ptr, width, height) -> img_ptr
Returns an image pointer. All drawing goes into this buffer first.
"""
img_ptr = m.mlx_new_image(mlx_ptr, W, H)

"""Returns direct access to the image buffer's raw memory.
Signature: mlx_get_data_addr(img_ptr) ->
    (img_addr, bits_per_pixel, size_line, endian)
img_addr  - raw writable byte buffer - write pixel data directly into it
img_size_line - row stride in bytes: use this, never recompute as width x 4
The other two return values (bits_per_pixel, endian) are discarded with _.
"""
img_addr, _, img_size_line, _ = m.mlx_get_data_addr(img_ptr)

# =============================================================================
# DRAWING PRIMITIVES
# =============================================================================

def write_pixel(x: int, y: int, color: int) -> None:
    """Write single pixel at (x, y) into the image buffer.
    MLX stores pixels in BGR order, 4 bytes per pixel:
        [Blue, Green, Red, Alpha].
    Color constants use 0xRRGGBB (RGB) - the universal convention used by
    Photoshop, Aseprite, and every browser color picker. The conversion to BGR
    happens silently inside write_pixel and write_rect. Callers always pass
    0xRRGGBB unchanged.
    Uses img_size_line for the row stride - never recompute as width x 4.
    Out-of-bounds coords are skipped silently.
    """
    if not (0 <= x < W and 0 <= y < H):
        return
    byte_index = y * img_size_line + x * 4
    img_addr[byte_index] = color & 0xFF              # blue  (lowest byte)
    img_addr[byte_index + 1] = (color >> 8) & 0xFF   # green
    img_addr[byte_index + 2] = (color >> 16) & 0xFF  # red   (highest byte)
    img_addr[byte_index + 3] = 0xFF                  # alpha - fully opaque

def write_rect(x: int, y: int, w: int, h: int, color: int) -> None:
    """Fill a rectangle with a solid color using fast row slice assignment.
    Builds one complete BGR row as a bytearray (w x 4 bytes), then copies
    it into each row via slice assignment - bulk memory copy, orders of
    magnitude faster than a per-pixel loop for large fills like backgrounds.
    """
    blue = color & 0xFF
    green = (color >> 8) & 0xFF
    red = (color >> 16) & 0xFF
    row = bytearray([blue, green, red, 0xFF] * w)
    for row_offset in range(h):
        start = (y + row_offset) * img_size_line + x * 4
        end = start + len(row)
        img_addr[start:end] = row

def render() -> None:
    """Push image buffer to window.
    Nothing drawn with write_pixel / write_rect is visible until this call.
    Draw everything first, then call render() once per frame.
    """
    m.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 0, 0)

# =============================================================================
# SCENE
# =============================================================================


# Grid layout: 3 columns x 2 rows of colored rectangles, centered in window
RECT_W, RECT_H = 200, 200
COLS, ROWS = 3, 2
GAP = 20
GRID_W = COLS * RECT_W + (COLS - 1) * GAP
GRID_H = ROWS * RECT_H + (ROWS - 1) * GAP
ORIGIN_X = CENTER_X - GRID_W // 2
ORIGIN_Y = CENTER_Y - GRID_H // 2

COLORS = [
    C_RED, C_GREEN, C_BLUE,
    C_CYAN, C_MAGENTA, C_YELLOW,
]

write_rect(0, 0, W, H, C_BG)

for i, color in enumerate(COLORS):
    col = i % COLS
    row = i // COLS
    x = ORIGIN_X + col * (RECT_W + GAP)
    y = ORIGIN_Y + row * (RECT_H + GAP)
    write_rect(x, y, RECT_W, RECT_H, color)

write_pixel(CENTER_X, CENTER_Y, 0xFFFFFF)  # single white pixel at center

render()  # push to screen - nothing above is visible until this call

# =============================================================================
# HOOKS
# =============================================================================

def key_handler(keycode: int, param) -> int:
    if keycode == KEY_ESC:
        m.mlx_loop_exit(mlx_ptr)
    return 0

def close_handler(param) -> int:
    m.mlx_loop_exit(mlx_ptr)
    return 0

m.mlx_hook(win_ptr, EVENT_KEY_PRESS, MASK_KEY_PRESS, key_handler, None)
m.mlx_hook(win_ptr, EVENT_WINDOW_CLOSE, MASK_NONE, close_handler, None)

# =============================================================================
# LOOP
# =============================================================================

m.mlx_loop(mlx_ptr)

# =============================================================================
# CLEANUP
# =============================================================================

"""Always destroy resources in reverse creation order: image -> window -> mlx.
Signature: mlx_destroy_image(mlx_ptr, img_ptr) -> None
Signature: mlx_destroy_window(mlx_ptr, win_ptr) -> None
Signature: mlx_release(mlx_ptr) -> None
An 800x600 image buffer costs ~2MB - always destroy before creating a new one.
"""
m.mlx_destroy_image(mlx_ptr, img_ptr)
m.mlx_destroy_window(mlx_ptr, win_ptr)
m.mlx_release(mlx_ptr)

# =============================================================================
# WHAT TO TRY NEXT:
#   - Move render() to before the rect loop and observe that nothing appears -
#     then move it back and understand why render timing matters
#   - Draw a gradient: loop over x and vary the color per column
# =============================================================================
