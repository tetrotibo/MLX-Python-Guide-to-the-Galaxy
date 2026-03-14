# =============================================================================
# B01 - PIXEL PUT 01: mlx_pixel_put called before mlx_loop
# =============================================================================
#
# HYPOTHESIS:
#   Calls made before mlx_loop are discarded - the X11/XQuartz display
#   server has not started processing events yet.
#   Result is INCONCLUSIVE - see B01_pixel_put_02 for the next test.
#
# TRY THIS:
#   1. Run the script - terminal confirms 360,000 pixels drawn.
#   2. Window stays black - nothing rendered.
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
    C_GREEN,
)

TITLE = Path(__file__).stem

# =============================================================================
# CONFIG
# =============================================================================

W = 600  # window width in pixels
H = 600  # window height in pixels
RECT_W = W   # rectangle width - full window
RECT_H = H   # rectangle height - full window

# =============================================================================
# INIT
# =============================================================================

m = mlx.Mlx()
mlx_ptr = m.mlx_init()
win_ptr = m.mlx_new_window(mlx_ptr, W, H, TITLE)

# =============================================================================
# HOOKS
# =============================================================================

def key_press_handler(keycode: int, param) -> int:
    """Handle key press events."""
    if keycode == KEY_ESC:
        m.mlx_loop_exit(mlx_ptr)
    return 0

def close_handler(param) -> int:
    """Handle the X button (window close event)."""
    m.mlx_loop_exit(mlx_ptr)
    return 0

m.mlx_hook(win_ptr, EVENT_KEY_PRESS, MASK_KEY_PRESS, key_press_handler, None)
m.mlx_hook(win_ptr, EVENT_WINDOW_CLOSE, MASK_NONE, close_handler, None)

rx = (W - RECT_W) // 2
ry = (H - RECT_H) // 2

count = 0
for y in range(ry, ry + RECT_H):
    for x in range(rx, rx + RECT_W):
        m.mlx_pixel_put(mlx_ptr, win_ptr, x, y, C_GREEN)
        count += 1

print(f"done - {count} pixels drawn")

# =============================================================================
# LOOP
# =============================================================================

m.mlx_loop(mlx_ptr)

# =============================================================================
# CLEANUP
# =============================================================================

m.mlx_destroy_window(mlx_ptr, win_ptr)
m.mlx_release(mlx_ptr)
