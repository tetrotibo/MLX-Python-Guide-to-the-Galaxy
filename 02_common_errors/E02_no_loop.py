# =============================================================================
# E02 - NO LOOP: missing mlx_loop()
# =============================================================================
#
# CONCEPT:
#   Without mlx_loop(), the script runs to the end and exits immediately.
#   mlx_loop() is the blocking call that hands control to MLX and starts
#   the event loop. Without it, hooks never fire and the window never
#   has a chance to receive or process any events.
#
# TRY THIS:
#   1. Run the script - window opens and immediately closes.
#   2. Uncomment m.mlx_loop(mlx_ptr) in the LOOP section below.
#   3. Run again - window stays open, ESC and X button now work.
#
# CONTROLS:
#   ESC:        quit
#   X button:   quit
#
# =============================================================================

import mlx  # type: ignore
from pathlib import Path
from config import (  # type: ignore
    EVENT_KEY_PRESS, EVENT_WINDOW_CLOSE,
    MASK_KEY_PRESS, MASK_NONE,
    KEY_ESC,
)

TITLE = Path(__file__).stem

# =============================================================================
# CONFIG
# =============================================================================

W = 600  # window width in pixels
H = 600  # window height in pixels

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

# =============================================================================
# LOOP
# =============================================================================

# BUG: the line below is missing - comment it out to see the bug
# m.mlx_loop(mlx_ptr)

# =============================================================================
# CLEANUP
# =============================================================================

m.mlx_destroy_window(mlx_ptr, win_ptr)
m.mlx_release(mlx_ptr)
