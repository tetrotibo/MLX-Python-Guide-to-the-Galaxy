## Python MLX - All 34 Functions

| Category | Function | Returns | Description |
| -------- | -------- | ------- | ----------- |
| INIT | `mlx.Mlx()` | `Mlx` | Creates the MLX object - entry point for all function calls |
| INIT | `m.mlx_init()` | `mlx_ptr` | Connects to the display server (X11/XQuartz), returns session handle |
| INIT | `m.mlx_release(mlx_ptr)` | `None` | Disconnects from display server, releases all resources |
| WINDOW | `m.mlx_new_window(mlx_ptr, w, h, title)` | `win_ptr` | Creates a window, returns its handle |
| WINDOW | `m.mlx_clear_window(mlx_ptr, win_ptr)` | `None` | Fills the window with black |
| WINDOW | `m.mlx_destroy_window(mlx_ptr, win_ptr)` | `None` | Closes and destroys a window |
| DRAW | `m.mlx_pixel_put(mlx_ptr, win_ptr, x, y, color)` | `None` | Draws one pixel directly to window - very slow, avoid for fills |
| DRAW | `m.mlx_string_put(mlx_ptr, win_ptr, x, y, color, text)` | `None` | Draws text directly to window, bypasses image buffer |
| IMAGE | `m.mlx_new_image(mlx_ptr, w, h)` | `img_ptr` | Allocates an off-screen pixel buffer |
| IMAGE | `m.mlx_get_data_addr(img_ptr)` | `(addr, bpp, size_line, endian)` | Returns direct access to the image buffer's raw memory |
| IMAGE | `m.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, x, y)` | `None` | Pushes image buffer to window |
| IMAGE | `m.mlx_destroy_image(mlx_ptr, img_ptr)` | `None` | Frees image buffer memory |
| IMAGE | `m.mlx_png_file_to_image(mlx_ptr, filename, w, h)` | `img_ptr` | Loads a PNG file into an image buffer |
| IMAGE | `m.mlx_xpm_file_to_image(mlx_ptr, filename, w, h)` | `img_ptr` | Loads an XPM file into an image buffer |
| IMAGE | `m.mlx_xpm_to_image(mlx_ptr, xpm_data, w, h)` | `img_ptr` | Creates an image from XPM data in memory |
| EVENT | `m.mlx_loop(mlx_ptr)` | `None` | Starts the event loop - blocks until `mlx_loop_exit` is called |
| EVENT | `m.mlx_loop_exit(mlx_ptr)` | `None` | Exits the event loop from inside a hook callback |
| EVENT | `m.mlx_loop_hook(mlx_ptr, func, param)` | `None` | Registers a callback fired every frame |
| EVENT | `m.mlx_hook(win_ptr, event, mask, func, param)` | `None` | Registers a callback for any X11/XQuartz event |
| EVENT | `m.mlx_key_hook(win_ptr, func, param)` | `None` | Shorthand hook for key release events |
| EVENT | `m.mlx_mouse_hook(win_ptr, func, param)` | `None` | Shorthand hook for mouse button clicks |
| EVENT | `m.mlx_expose_hook(win_ptr, func, param)` | `None` | Hook for window redraw events (X11 only) |
| MOUSE | `m.mlx_mouse_show(mlx_ptr)` | `None` | Makes the mouse cursor visible |
| MOUSE | `m.mlx_mouse_hide(mlx_ptr)` | `None` | Hides the mouse cursor |
| MOUSE | `m.mlx_mouse_move(mlx_ptr, x, y)` | `None` | Moves the mouse cursor to (x, y) |
| MOUSE | `m.mlx_mouse_get_pos(win_ptr)` | `(x, y)` | Returns current mouse cursor position |
| KEYBOARD | `m.mlx_do_key_autorepeaton(mlx_ptr)` | `None` | Enables key autorepeat while held |
| KEYBOARD | `m.mlx_do_key_autorepeatoff(mlx_ptr)` | `None` | Disables key autorepeat (off by default in this build) |
| INFO | `m.mlx_get_screen_size(mlx_ptr)` | `(ret, w, h)` | Returns monitor screen dimensions |
| SYNC | `m.mlx_do_sync(mlx_ptr)` | `None` | Flushes all pending drawing commands |
| SYNC | `m.mlx_sync(mlx_ptr, cmd, param)` | `None` | Advanced sync control (1=writable, 2=flush, 3=complete) |
| SYNC | `m.SYNC_IMAGE_WRITABLE` | `1` | Constant for `mlx_sync` - image ready for writing |
| SYNC | `m.SYNC_WIN_FLUSH` | `2` | Constant for `mlx_sync` - flush window drawing |
| SYNC | `m.SYNC_WIN_COMPLETED` | `3` | Constant for `mlx_sync` - wait until drawing complete |

---

## Function Notes

<details>
<summary><code>mlx.Mlx()</code></summary>
<br>

Creates a Python object that gives you access to all MLX functions. Think of it as opening a toolbox - `m` now contains all the methods you need. Without this, you can't call any MLX functions. It's just setting up the interface between Python and the underlying C library.

</details>

<details>
<summary><code>m.mlx_init()</code></summary>

Connects to the graphics system (X11/XQuartz) and returns a unique ID (`mlx_ptr`) for this connection. Every MLX function needs this ID to know which graphics session you're talking to. Like logging into a system and getting a session token - you'll pass `mlx_ptr` to almost every function after this.

</details>

<details>
<summary><code>m.mlx_release(mlx_ptr)</code></summary>

Disconnects from the graphics system and releases all resources. Call this at the end of your program to clean up. Closes the connection opened by `mlx_init()`.

</details>

<details>
<summary><code>m.mlx_new_window(mlx_ptr, w, h, title)</code></summary>

Creates a new window on screen with specified dimensions and title. Returns a window ID (`win_ptr`) that you'll use to draw in this specific window. You can create multiple windows - each gets its own ID. The window appears immediately but is empty (black) until you draw something.

</details>

<details>
<summary><code>m.mlx_clear_window(mlx_ptr, win_ptr)</code></summary>

Fills the entire window with black, erasing everything. Use this when you want to start fresh or clear old drawings.

</details>

<details>
<summary><code>m.mlx_destroy_window(mlx_ptr, win_ptr)</code></summary>

Closes and destroys a window completely. The window disappears from screen and all its resources are freed. Can't use `win_ptr` after this.

</details>

<details>
<summary><code>m.mlx_pixel_put(mlx_ptr, win_ptr, x, y, color)</code></summary>

Draws a single pixel at coordinates (x, y) with the specified color. Origin (0,0) is top-left. Color format is `0xRRGGBB`. **Non-functional on this MLX build** - see `B01_pixel_put_*.py` for the full investigation. Use `write_pixel` via the image buffer instead.

</details>

<details>
<summary><code>m.mlx_string_put(mlx_ptr, win_ptr, x, y, color, text)</code></summary>

Draws text directly to the window at position (x, y). Bypasses the image buffer - calling `render()` after it overwrites the text. Always call `render()` first, then `mlx_string_put`. Color must be `0xBBGGRR` - use `str_color()` to convert from `0xRRGGBB`. See E06 and E07.

</details>

<details>
<summary><code>m.mlx_new_image(mlx_ptr, w, h)</code></summary>

Creates an image buffer in memory - a blank canvas you can draw on pixel by pixel. Images are much faster than `mlx_pixel_put` because you prepare everything in memory then display all at once with a single `mlx_put_image_to_window` call. An 800x600 image costs ~1.8MB - always destroy before creating a new one.

</details>

<details>
<summary><code>m.mlx_get_data_addr(img_ptr)</code></summary>

Returns direct access to the image buffer's raw memory. `addr` is a writable byte buffer - write pixel data directly into it. `size_line` is the row stride in bytes - always use this, never recompute as `width x 4`. MLX stores pixels in BGR order, 4 bytes per pixel: `[Blue, Green, Red, Alpha]`.

**Returns:** `(addr, bits_per_pixel, size_line, endian)`

</details>

<details>
<summary><code>m.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, x, y)</code></summary>

Pushes the image buffer to the window at position (x, y). Nothing drawn with `write_pixel` or `write_rect` is visible until this call. Draw everything first, then call once per frame.

</details>

<details>
<summary><code>m.mlx_destroy_image(mlx_ptr, img_ptr)</code></summary>

Destroys an image buffer and frees its memory. Always destroy in reverse creation order: image before window before mlx. After this, `img_ptr` is invalid.

</details>

<details>
<summary><code>m.mlx_png_file_to_image(mlx_ptr, filename, w, h)</code></summary>

Loads a PNG file from disk into an image buffer. Returns image ID or None if failed. MLX's PNG support is limited - complex PNGs may not load correctly.

</details>

<details>
<summary><code>m.mlx_xpm_file_to_image(mlx_ptr, filename, w, h)</code></summary>

Loads an XPM file into an image buffer. XPM is an older image format still common in 42 projects. Returns image ID or None if failed.

</details>

<details>
<summary><code>m.mlx_xpm_to_image(mlx_ptr, xpm_data, w, h)</code></summary>

Creates an image directly from XPM data in memory (not a file). XPM data is an array of strings. Useful for embedding small images directly in code.

</details>

<details>
<summary><code>m.mlx_loop(mlx_ptr)</code></summary>

Starts the main event loop. This function blocks - it never returns unless `mlx_loop_exit` is called. The loop calls your registered hook functions when events fire. Code below `mlx_loop()` will not run until the loop exits.

</details>

<details>
<summary><code>m.mlx_loop_exit(mlx_ptr)</code></summary>

Breaks out of the event loop. Call this from inside a hook callback (key handler, close handler) to exit cleanly. After this, `mlx_loop()` returns and execution continues in cleanup.

</details>

<details>
<summary><code>m.mlx_loop_hook(mlx_ptr, func, param)</code></summary>

Registers a callback fired on every tick of `mlx_loop` - as fast as the system allows. Runs continuously for the entire lifetime of the loop. This is where deferred work runs and where you measure FPS. See M06 and D02.

**Callback signature:** `def func(param) -> int`

</details>

<details>
<summary><code>m.mlx_hook(win_ptr, event, mask, func, param)</code></summary>

Registers a callback for a specific X11/XQuartz event on a specific window. More flexible than the shorthand hooks - required for `EVENT_WINDOW_CLOSE` (event 33). Use `MASK_KEY_PRESS` for key events, `MASK_NONE` for most others. See M01.

**Callback signature:** `def func(keycode, param) -> int` (key events) or `def func(param) -> int` (others)

</details>

<details>
<summary><code>m.mlx_key_hook(win_ptr, func, param)</code></summary>

Shorthand for registering a key hook. Note: fires on key **release**, not press. Use `mlx_hook` with `EVENT_KEY_PRESS` if you need press events.

**Callback signature:** `def func(keycode, param) -> int`

</details>

<details>
<summary><code>m.mlx_mouse_hook(win_ptr, func, param)</code></summary>

Registers a callback for mouse button clicks. Button codes: 1=left, 2=middle, 3=right.

**Callback signature:** `def func(button, x, y, param) -> int`

</details>

<details>
<summary><code>m.mlx_expose_hook(win_ptr, func, param)</code></summary>

Registers a callback for window redraw events (when the window is uncovered). X11/XQuartz only - does not fire on Wayland. Usually not needed for programs that redraw continuously.

**Callback signature:** `def func(param) -> int`

</details>

<details>
<summary><code>m.mlx_mouse_show(mlx_ptr)</code></summary>

Makes the mouse cursor visible. Default state is visible - only needed after calling `mlx_mouse_hide()`.

</details>

<details>
<summary><code>m.mlx_mouse_hide(mlx_ptr)</code></summary>

Hides the mouse cursor. The cursor is still functional, just invisible. Good for immersive graphics or custom cursor implementations.

</details>

<details>
<summary><code>m.mlx_mouse_move(mlx_ptr, x, y)</code></summary>

Forcibly moves the mouse cursor to position (x, y). Use sparingly - disorienting for users. Useful for FPS-style mouse look where you need to recenter the cursor each frame.

</details>

<details>
<summary><code>m.mlx_mouse_get_pos(win_ptr)</code></summary>

Returns the current mouse cursor position within the window as a `(x, y)` tuple. Useful for hover effects or drag-without-click interactions.

</details>

<details>
<summary><code>m.mlx_do_key_autorepeaton(mlx_ptr)</code></summary>

Enables X11/XQuartz key autorepeat. When a key is held, `KeyPress` events fire repeatedly. Off by default in this MLX build - you must explicitly opt in. See D03.

</details>

<details>
<summary><code>m.mlx_do_key_autorepeatoff(mlx_ptr)</code></summary>

Disables key autorepeat. Holding a key fires exactly one `KeyPress` event. Already the default in this MLX build. Call once at startup if you need to guarantee this behavior. See D03.

</details>

<details>
<summary><code>m.mlx_get_screen_size(mlx_ptr)</code></summary>

Returns the monitor's screen dimensions as `(return_code, width, height)`. Useful for making fullscreen windows or centering content. Can be called before creating any windows.

</details>

<details>
<summary><code>m.mlx_do_sync(mlx_ptr)</code></summary>

Flushes all pending drawing commands to the display server. MLX usually handles this automatically. Use if rendering looks delayed or incomplete.

</details>

<details>
<summary><code>m.mlx_sync(mlx_ptr, cmd, param)</code></summary>

Advanced synchronization with specific commands: 1=image writable, 2=window flush, 3=window completed. For precise timing control. Most programs don't need this - use `mlx_do_sync()` instead. Tested in `B01_pixel_put_03.py` with `SYNC_WIN_FLUSH` - did not make `mlx_pixel_put` work.

</details>

<details>
<summary><code>m.SYNC_IMAGE_WRITABLE</code> / <code>m.SYNC_WIN_FLUSH</code> / <code>m.SYNC_WIN_COMPLETED</code></summary>

Constants (1, 2, 3) for use with `mlx_sync`. Advanced use only.

</details>

---

## The 8 Essential Functions

| Function | Role |
| -------- | ---- |
| `mlx_init()` | Start graphics session |
| `mlx_new_window()` | Create a window |
| `mlx_new_image()` | Allocate pixel buffer |
| `mlx_get_data_addr()` | Get raw memory access for fast drawing |
| `mlx_put_image_to_window()` | Push buffer to screen |
| `mlx_hook()` | Register event callbacks |
| `mlx_loop_hook()` | Register per-frame callback |
| `mlx_loop()` | Run the program |
