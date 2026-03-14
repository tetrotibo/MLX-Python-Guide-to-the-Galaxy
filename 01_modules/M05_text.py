# =============================================================================
# M05 - TEXT: mlx_string_put, color conversion, draw order
# =============================================================================
#
# CONCEPTS:
#   - mlx_string_put bypasses the image buffer and draws straight to window -
#     each call is a synchronous X11/XQuartz roundtrip, slow enough that
#     drawing a dozen labels renders visibly top to bottom like credits
#   - Text is always drawn on top of the last mlx_put_image_to_window call
#   - No control over font family, size, or weight - X11/XQuartz font only
#   - Unicode characters do not render - ASCII only
#   - Color is the only customizable property
#   - mlx_string_put expects 0xBBGGRR, not 0xRRGGBB - see str_color()
#   - render() must always come BEFORE mlx_string_put, never after -
#     calling render() again overwrites the text with the image buffer
#
# WHAT WE ARE BUILDING:
#   A palette viewer - each color constant from config.py rendered as
#   a colored rectangle paired with a text label. Demonstrates both
#   mlx_string_put and the color conversion it requires.
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
    C_WHITE, C_RED, C_GREEN, C_BLUE,
    C_CYAN, C_MAGENTA, C_YELLOW,
    C_BG, C_FLOOR, C_WALL, C_ENTRY, C_EXIT,
    C_PATH, C_PATTERN, C_PLAYER,
    C_UI_BG, C_UI_ACTIVE, C_UI_INACTIVE,
)

TITLE = Path(__file__).stem

# =============================================================================
# CONFIG
# =============================================================================

W = 700  # window width in pixels
H = 700  # window height in pixels
COLOR_X = 60   # x position of color rectangle
COLOR_W = 120  # width of color rectangle in pixels
COLOR_H = 20   # height of color rectangle in pixels
LABEL_X = 210  # x position of text label
ROW_H = 32     # vertical distance between rows in pixels
ROW_0 = 60     # y position of first row in pixels

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
    """Fill a rectangle using fast row slice assignment."""
    blue = color & 0xFF
    green = (color >> 8) & 0xFF
    red = (color >> 16) & 0xFF
    row = bytearray([blue, green, red, 0xFF] * w)
    for row_offset in range(h):
        start = (y + row_offset) * img_size_line + x * 4
        end = start + len(row)
        img_addr[start:end] = row

def render() -> None:
    """Push image buffer to window."""
    m.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 0, 0)

# =============================================================================
# COLOR CONVERSION
# =============================================================================

"""All color constants use 0xRRGGBB - the universal convention used by
Photoshop, Aseprite, and every browser color picker. write_rect handles
the BGR conversion internally. mlx_string_put does not - it is a C
function that reads the integer directly, giving 0xBBGGRR on screen.
str_color() corrects this at the call site so all code stays consistent.
"""

def str_color(color: int) -> int:
    """Convert 0xRRGGBB to 0xBBGGRR for mlx_string_put."""
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    return (b << 16) | (g << 8) | r

# =============================================================================
# SCENE
# =============================================================================

LABELS = [
    (C_WHITE,         f"C_WHITE         {hex(C_WHITE)}   soft white"),
    (C_RED,           f"C_RED           {hex(C_RED)}   soft red"),
    (C_GREEN,         f"C_GREEN         {hex(C_GREEN)}   soft green"),
    (C_BLUE,          f"C_BLUE          {hex(C_BLUE)}   soft blue"),
    (C_CYAN,          f"C_CYAN          {hex(C_CYAN)}   soft cyan"),
    (C_MAGENTA,       f"C_MAGENTA       {hex(C_MAGENTA)}   soft magenta"),
    (C_YELLOW,        f"C_YELLOW        {hex(C_YELLOW)}   soft yellow"),
    (C_BG,            f"C_BG            {hex(C_BG)}   charcoal"),
    (C_FLOOR,         f"C_FLOOR         {hex(C_FLOOR)}   dark grey"),
    (C_WALL,          f"C_WALL          {hex(C_WALL)}   silver"),
    (C_ENTRY,         f"C_ENTRY         {hex(C_ENTRY)}   steel blue"),
    (C_EXIT,          f"C_EXIT          {hex(C_EXIT)}   steel blue"),
    (C_PATH,          f"C_PATH          {hex(C_PATH)}   moss green"),
    (C_PATTERN,       f"C_PATTERN       {hex(C_PATTERN)}   amber"),
    (C_PLAYER,        f"C_PLAYER        {hex(C_PLAYER)}   burnt orange"),
    (C_UI_BG,         f"C_UI_BG         {hex(C_UI_BG)}   jet black"),
    (C_UI_ACTIVE,     f"C_UI_ACTIVE     {hex(C_UI_ACTIVE)}   burnt orange"),
    (C_UI_INACTIVE,   f"C_UI_INACTIVE   {hex(C_UI_INACTIVE)}   steel blue"),
]

write_rect(0, 0, W, H, C_UI_BG)

for i, (color, _) in enumerate(LABELS):
    y = ROW_0 + i * ROW_H
    write_rect(COLOR_X, y, COLOR_W, COLOR_H, color)
render()

# render() is called once after all rectangles are drawn, then
# mlx_string_put draws all labels on top in a second loop.
# mlx_string_put is slow - drawing 18 labels renders visibly top to bottom.

"""Draw text labels directly to the window, on top of the image buffer.
Signature: mlx_string_put(mlx_ptr, win_ptr, x, y, color, text) -> None

x, y  - pixel position of the text baseline
color - must be 0xBBGGRR - always wrap with str_color()
text  - ASCII string only, unicode does not render
"""
for i, (_, label) in enumerate(LABELS):
    y = ROW_0 + i * ROW_H
    m.mlx_string_put(mlx_ptr, win_ptr, LABEL_X, y + 4,
                     str_color(C_WHITE), label)

# =============================================================================
# HOOKS
# =============================================================================

def key_press_handler(keycode: int, param) -> int:
    if keycode == KEY_ESC:
        m.mlx_loop_exit(mlx_ptr)
    return 0

def close_handler(param) -> int:
    m.mlx_loop_exit(mlx_ptr)
    return 0

m.mlx_hook(win_ptr, EVENT_KEY_PRESS, MASK_KEY_PRESS, key_press_handler, None)
m.mlx_hook(win_ptr, EVENT_WINDOW_CLOSE, MASK_NONE, close_handler, None)

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

# =============================================================================
# WHAT TO TRY NEXT:
#   - In the label loop, replace str_color(C_WHITE) with C_WHITE directly.
#     0xEEEEEE is read as 0xEEEEEE by mlx_string_put - happens to look the
#     same because white is symmetric. Try C_BLUE (0x3333BB) instead:
#     mlx_string_put reads it as 0xBB3333 - text turns red.
#   - Swap the order of render() and the label loop - text disappears
#     because render() overwrites the labels with the image buffer.
#   - Think about how you would draw custom-sized text without mlx_string_put:
#     what data would you need per character, and how would you store it?
# =============================================================================
