# =============================================================================
# E04 - X BUTTON: missing close handler
# =============================================================================
#
# CONCEPT:
#   MLX has no default close handler. Clicking the X button fires event 33
#   (DestroyNotify) but if nothing is hooked to it, the event is silently
#   discarded and the program keeps running. You must always register a
#   close handler explicitly - it is mandatory for it to work.
#
# TRY THIS:
#   1. Run the script - click the X button, nothing happens.
#   2. Only way to exit is ESC.
#   3. Find the commented mlx_hook for EVENT_WINDOW_CLOSE in HOOKS.
#   4. Uncomment it and run again - X button exits cleanly.
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

# BUG: the line below is missing - uncomment it to see the fix
# m.mlx_hook(win_ptr, EVENT_WINDOW_CLOSE, MASK_NONE, close_handler, None)

# =============================================================================
# LOOP
# =============================================================================

m.mlx_loop(mlx_ptr)

# =============================================================================
# CLEANUP
# =============================================================================

m.mlx_destroy_window(mlx_ptr, win_ptr)
m.mlx_release(mlx_ptr)
