# =============================================================================
# B01 - PIXEL PUT 02: mlx_pixel_put called from inside a key handler
# =============================================================================
#
# HYPOTHESIS:
#   mlx_pixel_put may require an explicit flush to push pixels to screen.
#   Result is INCONCLUSIVE - see B01_pixel_put_03 for the next test.
#
# TRY THIS:
#   1. Run the script - press SPACE.
#   2. Terminal confirms 90,000 calls completed.
#   3. Window stays black - nothing rendered.
#
# CONTROLS:
#   SPACE:  attempt to draw the rect
#   ESC:    quit
#
# =============================================================================

import mlx  # type: ignore
from pathlib import Path
from config import (  # type: ignore
    EVENT_KEY_PRESS, EVENT_WINDOW_CLOSE,
    MASK_KEY_PRESS, MASK_NONE,
    KEY_ESC, KEY_SPACE,
    C_GREEN,
)

TITLE = Path(__file__).stem

# =============================================================================
# CONFIG
# =============================================================================

W = 600  # window width in pixels
H = 600  # window height in pixels
RECT_W = 300  # rectangle width in pixels
RECT_H = 300  # rectangle height in pixels

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
    elif keycode == KEY_SPACE:
        rx = (W - RECT_W) // 2
        ry = (H - RECT_H) // 2
        count = 0
        for y in range(ry, ry + RECT_H):
            for x in range(rx, rx + RECT_W):
                m.mlx_pixel_put(mlx_ptr, win_ptr, x, y, C_GREEN)
                count += 1
        print(f"mlx_pixel_put called {count} times")
    return 0

def close_handler(param) -> int:
    """Handle the X button (window close event)."""
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

m.mlx_destroy_window(mlx_ptr, win_ptr)
m.mlx_release(mlx_ptr)
