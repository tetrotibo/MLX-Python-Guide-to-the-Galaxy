# =============================================================================
# E03 - MASK KEY PRESS: wrong mask on key hook
# =============================================================================
#
# CONCEPT:
#   mlx_hook takes an event mask as its third argument. The mask tells
#   X11/XQuartz which sub-types of the event to deliver. For KEY_PRESS,
#   the correct mask is MASK_KEY_PRESS (1). Passing MASK_NONE (0) registers
#   the hook but tells X11/XQuartz not to deliver key events to it -
#   the callback exists but never fires.
#
# TRY THIS:
#   1. Run the script - press any key, nothing happens. ESC does nothing.
#   2. Only way to exit is the X button.
#   3. Find the key hook in HOOKS - replace MASK_NONE with MASK_KEY_PRESS.
#   4. Run again - keys respond, ESC exits cleanly.
#
# CONTROLS:
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

# BUG: MASK_NONE should be MASK_KEY_PRESS for the first m.mlx_hook
m.mlx_hook(win_ptr, EVENT_KEY_PRESS, MASK_NONE, key_press_handler, None)
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
