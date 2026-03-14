# =============================================================================
# D01 - MEMORY LEAK: mlx_new_image without mlx_destroy_image
# =============================================================================
#
# CONCEPT:
#   Every mlx_new_image() allocates a buffer. If you create a new image
#   without destroying the previous one, the old buffer is never freed.
#   MLX has no garbage collection - abandoned image pointers leak permanently
#   for the lifetime of the process. On a maze project that regenerates
#   frequently, this adds up fast.
#
# TRY THIS:
#   1. Run the script - terminal prints starting memory.
#   2. Press SPACE repeatedly - watch memory climb with each new image.
#   3. Press ESC - terminal prints final memory delta.
#   4. Uncomment m.mlx_destroy_image() in the key_press_handler below.
#   5. Run again - memory stays flat no matter how many times you press SPACE.
#
# CONTROLS:
#   SPACE:  create a new image
#   ESC:    quit
#
# =============================================================================

import resource
import sys
import mlx  # type: ignore
from pathlib import Path
from config import (  # type: ignore
    EVENT_KEY_PRESS, EVENT_WINDOW_CLOSE,
    MASK_KEY_PRESS, MASK_NONE,
    KEY_ESC, KEY_SPACE,
)

TITLE = Path(__file__).stem

# =============================================================================
# CONFIG
# =============================================================================

W = 800  # window width in pixels
H = 600  # window height in pixels

# =============================================================================
# INIT
# =============================================================================

def mem_now() -> float:
    """Return current process memory usage in MB."""
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return rss / 1024 / 1024  # bytes on macOS
    return rss / 1024             # kilobytes on Linux

m = mlx.Mlx()
mlx_ptr = m.mlx_init()
win_ptr = m.mlx_new_window(mlx_ptr, W, H, TITLE)
img_ptr = m.mlx_new_image(mlx_ptr, W, H)

mem_start = mem_now()
iteration = 0

# =============================================================================
# HOOKS
# =============================================================================

def key_press_handler(keycode: int, param) -> int:
    """Handle key press events."""
    global img_ptr, iteration

    if keycode == KEY_ESC:
        m.mlx_loop_exit(mlx_ptr)
    elif keycode == KEY_SPACE:
        iteration += 1

        # BUG: old image is abandoned - uncomment the line below to fix
        # m.mlx_destroy_image(mlx_ptr, img_ptr)

        img_ptr = m.mlx_new_image(mlx_ptr, W, H)
        img_addr, _, img_size_line, _ = m.mlx_get_data_addr(img_ptr)
        row = bytearray([0xFF, 0x00, 0x00, 0xFF] * W)

        for y in range(H):
            start = y * img_size_line
            img_addr[start:start + len(row)] = row

        mem = mem_now()
        print(f"image #{iteration:4} - mem: {mem:6.1f} MB - delta: "
              f"{mem - mem_start:+.1f} MB")
    return 0

def close_handler(param) -> int:
    """Handle the X button (window close event)."""
    m.mlx_loop_exit(mlx_ptr)
    return 0

m.mlx_hook(win_ptr, EVENT_KEY_PRESS, MASK_KEY_PRESS, key_press_handler, None)
m.mlx_hook(win_ptr, EVENT_WINDOW_CLOSE, MASK_NONE, close_handler, None)

print(f"start mem: {mem_start:5.1f} MB")

# =============================================================================
# LOOP
# =============================================================================

m.mlx_loop(mlx_ptr)

# =============================================================================
# CLEANUP
# =============================================================================

mem_end = mem_now()
print(f"exit mem:  {mem_end:5.1f} MB - delta: {mem_end - mem_start:+.1f} MB")

m.mlx_destroy_image(mlx_ptr, img_ptr)
m.mlx_destroy_window(mlx_ptr, win_ptr)
m.mlx_release(mlx_ptr)
