## Broken MLX Functions

Functions confirmed non-functional on this build of the Python MLX binding.
Each entry documents what was tested, what was observed, and what to use instead.
These are not usage errors - the function is called correctly and still does nothing.

---

## PIXEL_PUT

<!-- mlx_pixel_put is non-functional on this build -->

**Symptom:** Pixels drawn with `mlx_pixel_put` never appear regardless
of color, coordinates, flush calls, or call location.

**Cause:** Unknown. The call silently succeeds with no exception.
Most likely a missing X11/XQuartz expose event path in this build.

**Fix:** Never use `mlx_pixel_put`. Use `write_pixel` via the image
buffer instead - see investigation log below for full context.

---

## Investigation log

Three tests were written in sequence, each ruling out one hypothesis.
Run them in order if you want to reproduce the investigation yourself.

**`B01_pixel_put_01.py` - called before `mlx_loop`**

360,000 calls at module level, filling the entire 600x600 window before
`mlx_loop` is started. Window stays black. Terminal confirms all calls
completed.

*Hypothesis ruled out: calls made before the event loop starts are
discarded because X11/XQuartz is not ready yet.*
→ Inconclusive. Moved calls inside the loop to test next.

---

**`B01_pixel_put_02.py` - called from inside a key handler**

90,000 calls triggered by SPACE, from inside a key handler, while
`mlx_loop` is running. Window stays black. Terminal prints
`mlx_pixel_put called 90000 times`.

*Hypothesis ruled out: X11/XQuartz was not ready before the loop started.*
→ Still black inside the loop. New hypothesis: maybe an explicit
flush is needed.

---

**`B01_pixel_put_03.py` - called with explicit `mlx_sync` flush**

Same as test 02, plus `mlx_sync(mlx_ptr, SYNC_WIN_FLUSH, win_ptr)`
called immediately after the pixel loop. Window stays black.
Terminal confirms 90,000 calls and the sync.

*Hypothesis ruled out: the display server needs an explicit flush signal.*
→ Still black. No remaining hypothesis. **Function is non-functional
on this build.**

---

## Fix

Never use `mlx_pixel_put`. Use `write_pixel` via the image buffer instead:

```python
def write_pixel(x, y, color):
    i = y * img_size_line + x * 4
    img_addr[i]     =  color        & 0xFF
    img_addr[i + 1] = (color >> 8)  & 0xFF
    img_addr[i + 2] = (color >> 16) & 0xFF
    img_addr[i + 3] = 0xFF

m.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 0, 0)
```

---
