## MLX Diagnostics

Tools for observing and measuring MLX behavior at runtime.
These are not error scripts - they are instruments. Run them when
something feels off: loop too slow, input behaving unexpectedly,
memory climbing for no reason.

---

## MEMORY_LEAK

<!-- mlx_new_image called without mlx_destroy_image -->

**Symptom:** Memory climbs steadily each time a new image is created.
No crash, no exception.

**Cause:** Every `mlx_new_image` allocates a buffer. Creating a new
image without destroying the previous one abandons the old buffer.
MLX has no garbage collection - it leaks for the lifetime of the process.

**How to measure:** Run `D01_memory_leak.py` and press SPACE repeatedly.
Terminal prints memory delta after each new image.

**Fix:**

```python
m.mlx_destroy_image(mlx_ptr, img_ptr)    # free old image first
img_ptr = m.mlx_new_image(mlx_ptr, W, H) # then create new one

# on exit - reverse creation order:
m.mlx_destroy_image(mlx_ptr, img_ptr)
m.mlx_destroy_window(mlx_ptr, win_ptr)
m.mlx_release(mlx_ptr)
```

---

## FRAME_RATE

<!-- Loop runs but effective FPS is lower than expected -->

**Symptom:** Motion feels sluggish or uneven. FPS lower than expected
or fluctuates significantly.

**Cause:** Each `mlx_loop_hook` tick costs whatever `loop_hook` takes
to execute. There is no frame cap or vsync - slow frame work shows up
immediately as dropped FPS.

**How to measure:** Run `D02_frame_rate.py`. Terminal prints FPS every
second. Add a `time.sleep()` inside `loop_hook` and watch FPS drop.

**Fix:** Keep `loop_hook` as lean as possible. Only redraw what changed.
Move logic that does not need to run every frame out of the loop.

---

## KEY_REPEAT

<!-- Observing X11/XQuartz key autorepeat behavior -->

**Symptom:** Holding an arrow key moves the rectangle once then stops.

**Cause:** Key autorepeat is off by default in this MLX build. Holding
a key fires exactly one `KeyPress` event.

**How to observe:** Run `D03_key_repeat.py`. Hold an arrow key with
repeat OFF (green) - moves once. Press SPACE to toggle ON (red) -
moves continuously.

**To enable repeat:**

```python
m.mlx_do_key_autorepeaton(mlx_ptr)   # opt-in - off by default
```

**To disable repeat:**

```python
m.mlx_do_key_autorepeatoff(mlx_ptr)  # call once at startup
```

---