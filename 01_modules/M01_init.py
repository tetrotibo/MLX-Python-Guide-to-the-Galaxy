# =============================================================================
# M01 - INIT: MLX initialization, window creation, clean shutdown
# =============================================================================
#
# CONCEPTS:
#   - The MLX object and what mlx_init() actually does
#   - Creating a window with mlx_new_window()
#   - Hooking keyboard events with mlx_hook()
#   - Closing the window with mlx_loop_exit()
#   - The X button: event 33, works on both Linux and Mac
#   - mlx_loop(): the blocking call that hands control to MLX
#
# WHAT WE ARE BUILDING:
#   A window that opens, stays open, and closes properly,
#   either by pressing ESC or clicking the X button.
#   This is the absolute foundation. Every MLX program starts here.
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

W = 800  # window width in pixels
H = 600  # window height in pixels

# =============================================================================
# INIT
# =============================================================================

"""Loads the MLX library and returns the wrapper object.
Signature: mlx.Mlx() -> Mlx
Every MLX call goes through this object - think of it as the driver.
"""
m = mlx.Mlx()

"""Connects to the display server (X11 on Linux, XQuartz on Mac).
Signature: mlx_init() -> mlx_ptr
Returns a connection handle - pass this to every subsequent call.
Without this, nothing else works.
"""
mlx_ptr = m.mlx_init()

"""Creates the actual OS window.
Signature: mlx_new_window(mlx_ptr, width, height, title) -> win_ptr
Returns a window pointer - keep it, you need it for hooks and drawing.
"""
win_ptr = m.mlx_new_window(mlx_ptr, W, H, TITLE)

# =============================================================================
# HOOKS
# =============================================================================

"""Exits the event loop cleanly from inside a hook callback.
Signature: mlx_loop_exit(mlx_ptr) -> None
After this call, mlx_loop() returns and execution continues in CLEANUP.
"""

def key_press_handler(keycode: int, param) -> int:
    """Handle key press events.
    keycode is the X11/XQuartz keycode of the pressed key.
    ESC exits the loop cleanly via mlx_loop_exit().
    """
    if keycode == KEY_ESC:
        m.mlx_loop_exit(mlx_ptr)
    return 0

def close_handler(param) -> int:
    """Handle the X button (window close event).
    Event 33 (DestroyNotify) is the correct hook for this.
    Do NOT use event 17 (ClientMessage) - it is unreliable
    across display configurations with this MLX build.
    """
    m.mlx_loop_exit(mlx_ptr)
    return 0

"""Registers a callback for a specific event on a specific window.
Signature: mlx_hook(win_ptr, event_id, mask, func, param) -> None

event_id - which X11 event to listen for
mask     - MASK_KEY_PRESS for KeyPress, MASK_NONE for most others
func     - your callback, called when the event fires
param    - arbitrary data passed to your callback (None if unused)
"""
m.mlx_hook(win_ptr, EVENT_KEY_PRESS, MASK_KEY_PRESS, key_press_handler, None)
m.mlx_hook(win_ptr, EVENT_WINDOW_CLOSE, MASK_NONE, close_handler, None)

# =============================================================================
# LOOP
# =============================================================================

"""Blocking call - hands control to MLX and starts the event loop.
Signature: mlx_loop(mlx_ptr) -> None
Code below this line will NOT run until mlx_loop_exit() is called.
"""
m.mlx_loop(mlx_ptr)

# =============================================================================
# CLEANUP
# =============================================================================

"""Free resources in reverse order: image -> window -> mlx instance.
Signature: mlx_destroy_window(mlx_ptr, win_ptr) -> None
Signature: mlx_release(mlx_ptr) -> None
M01 has no image buffer - mlx_destroy_image() is skipped here.
From M02 onwards, always destroy the image first before the window.
An 800x600 image buffer costs ~2MB - always destroy before creating a new one.
"""
# m.mlx_destroy_image(mlx_ptr, img_ptr)  # no image in M01
m.mlx_destroy_window(mlx_ptr, win_ptr)
m.mlx_release(mlx_ptr)

# =============================================================================
# WHAT TO TRY NEXT:
#   - Change W, H and observe the result
#   - Add a second window (call mlx_new_window again, hook it separately)
#   - Try removing close_handler and see what happens with the X button
#   - Try event 17 instead of 33 and test on your platform
# =============================================================================
