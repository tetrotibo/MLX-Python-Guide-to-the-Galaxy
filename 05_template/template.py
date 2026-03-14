# =============================================================================
# TEMPLATE - MLX STARTER TEMPLATE
# =============================================================================
#
# Copy this file as your starting point for any new MLX exercise.
# Everything here is the minimum viable MLX program:
#   - Window creation
#   - Image buffer
#   - write_pixel() and write_rect()
#   - ESC key + X button close
#   - Game loop hook
#   - Clean shutdown
#
# =============================================================================

import mlx  # type: ignore
from pathlib import Path

# =============================================================================
# CONFIG
# =============================================================================

TITLE = Path(__file__).stem

W = 800  # window width in pixels
H = 600  # window height in pixels

KEY_ESC = 65307
KEY_LEFT = 65361
KEY_RIGHT = 65363
KEY_UP = 65362
KEY_DOWN = 65364

EVENT_KEY_PRESS = 2
EVENT_KEY_RELEASE = 3
EVENT_WINDOW_CLOSE = 33
MASK_KEY_PRESS = 1
MASK_KEY_RELEASE = 2
MASK_NONE = 0

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
    if not (0 <= x < W and 0 <= y < H):
        return
    byte_index = y * img_size_line + x * 4
    img_addr[byte_index] = color & 0xFF  # blue
    img_addr[byte_index + 1] = (color >> 8) & 0xFF  # green
    img_addr[byte_index + 2] = (color >> 16) & 0xFF  # red
    img_addr[byte_index + 3] = 0xFF


def write_rect(x: int, y: int, w: int, h: int, color: int) -> None:
    blue = color & 0xFF
    green = (color >> 8) & 0xFF
    red = (color >> 16) & 0xFF
    row = bytearray([blue, green, red, 0xFF] * w)
    for row_offset in range(h):
        start = (y + row_offset) * img_size_line + x * 4
        end = start + len(row)
        img_addr[start:end] = row


def render() -> None:
    m.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 0, 0)


def str_color(color: int) -> int:
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    return (b << 16) | (g << 8) | r

# =============================================================================
# SCENE
# =============================================================================


write_rect(0, 0, W, H, 0x1D1D1D)  # background fill
# ... draw your scene here ...
render()

# =============================================================================
# HOOKS
# =============================================================================


def key_press_handler(keycode: int, param) -> int:
    if keycode == KEY_ESC:
        m.mlx_loop_exit(mlx_ptr)
    return 0


def key_release_handler(keycode: int, param) -> int:
    return 0


def close_handler(param) -> int:
    m.mlx_loop_exit(mlx_ptr)
    return 0


def game_loop(param) -> int:
    # called every frame - put time-based logic here
    return 0


m.mlx_hook(win_ptr, EVENT_KEY_PRESS, MASK_KEY_PRESS, key_press_handler, None)
m.mlx_hook(win_ptr, EVENT_KEY_RELEASE, MASK_KEY_RELEASE,
           key_release_handler, None)
m.mlx_hook(win_ptr, EVENT_WINDOW_CLOSE, MASK_NONE, close_handler, None)
m.mlx_loop_hook(mlx_ptr, game_loop, None)

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
