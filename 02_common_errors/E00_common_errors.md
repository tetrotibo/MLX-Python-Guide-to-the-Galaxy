## Common MLX Errors

A collection of the crashes and bugs you will almost certainly hit.
Each entry has the symptom, the cause, and the fix.

---

## BOUNDS

<!-- Buffer overflow from write_rect near window edge -->

**Symptom:** Two distinct failure modes depending on direction:
- **Vertical overflow** (`y + h > H`): `ValueError` raised mid-draw.
- **Horizontal overflow** (`x + w > W`): no exception. Pixels wrap
  silently to the start of the next row with no warning.

**Cause:** `write_rect` uses raw slice assignment into a memoryview.
Vertical overflow exceeds the buffer size - Python catches it.
Horizontal overflow stays within the buffer but lands in the wrong row.

**Fix:** Add explicit bounds clamping in `write_rect`:

```python
def write_rect(x, y, w, h, color):
    x = max(0, x);  w = min(w, W - x)
    y = max(0, y);  h = min(h, H - y)
    if w <= 0 or h <= 0:
        return
    ...
```

Or keep a `BORDER` of at least 1 tile around your grid:

```python
BORDER = 1
W = (GRID_COLS + 2 * BORDER) * TILE_SIZE
H = (GRID_ROWS + 2 * BORDER) * TILE_SIZE
```

---

## NO_LOOP

<!-- Window closes instantly -->

**Symptom:** Window opens and immediately closes. Hooks never fire.

**Cause:** `m.mlx_loop(mlx_ptr)` is missing. Without it the script
runs to the end and exits. The event loop never starts.

**Fix:**

```python
m.mlx_loop(mlx_ptr)   # blocking - nothing below runs until loop exits
```

---

## MASK_KEY_PRESS

<!-- Key hook registered but never fires -->

**Symptom:** Pressing keys does nothing. ESC does nothing. Only the
X button works.

**Cause:** `mlx_hook` for `EVENT_KEY_PRESS` was registered with
`MASK_NONE` (0) instead of `MASK_KEY_PRESS` (1). The callback exists
but X11/XQuartz never delivers key events to it.

**Fix:**

```python
# Wrong
m.mlx_hook(win_ptr, EVENT_KEY_PRESS, MASK_NONE, key_press_handler, None)

# Correct
m.mlx_hook(win_ptr, EVENT_KEY_PRESS, MASK_KEY_PRESS, key_press_handler, None)
```

---

## X_BUTTON

<!-- Clicking the window X button has no effect -->

**Symptom:** Clicking the X button does nothing. Program keeps running.

**Cause:** MLX has no default close handler. Event 33 (`DestroyNotify`)
is silently discarded if nothing is hooked to it.

**Fix:**

```python
def close_handler(param) -> int:
    m.mlx_loop_exit(mlx_ptr)
    return 0

m.mlx_hook(win_ptr, EVENT_WINDOW_CLOSE, MASK_NONE, close_handler, None)
```

Note: do NOT use event 17 (`ClientMessage`) - unreliable across
display configurations.

---

## SYNC_LOOP

<!-- Work inside a key handler freezes the window -->

**Symptom:** Pressing a key freezes the window. Queued inputs all fire
at once when the handler returns.

**Cause:** MLX callbacks run synchronously inside `mlx_loop`. Any
blocking work in a handler blocks the entire event loop.

**The deferred pattern:** Set a flag in the handler, do work in
`game_loop`. This does not eliminate the freeze - it ensures visual
feedback appears on screen before the work runs:

```python
def key_press_handler(keycode, param):
    if keycode == KEY_SPACE:
        pending_regen = True
        render_scene()   # feedback visible NOW
    return 0

def game_loop(param):
    if pending_regen:
        pending_regen = False
        do_regen()       # freeze happens here, feedback already visible
```

---

## TEXT_OVERWRITE

<!-- Text drawn with mlx_string_put disappears after render() -->

**Symptom:** `mlx_string_put` labels never appear, or vanish on redraw.

**Cause:** `mlx_string_put` draws to the window directly, not the image
buffer. Calling `render()` after it overwrites the text.

**Fix:** Always call `render()` before `mlx_string_put`, never after:

```python
render()               # push image buffer first
m.mlx_string_put(...)  # draw text on top
```

---

## STR_COLOR

<!-- mlx_string_put shows wrong color - byte order reversed -->

**Symptom:** You pass `C_BLUE` (0x3333BB) and the text renders red.

**Cause:** `mlx_string_put` reads color as `0xBBGGRR`, not `0xRRGGBB`.
Bytes are swapped compared to the rest of the guide.

**Fix:** Always wrap with `str_color()` before passing to `mlx_string_put`:

```python
def str_color(color: int) -> int:
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b =  color & 0xFF
    return (b << 16) | (g << 8) | r

m.mlx_string_put(mlx_ptr, win_ptr, x, y, str_color(C_BLUE), "hello")
```

---