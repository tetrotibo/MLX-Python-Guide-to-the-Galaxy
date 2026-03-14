_This guide was written alongside A-MAZE-ING, a school project
by tdarscot and tdhenain at 42 Belgium._

## About

This guide exists because the Python MLX binding has almost no
documentation and many students hit the same walls. Everything here
is based on my original research and experimentation done during the
development of A-MAZE-ING.

The goal is not to hand you ready-made solutions - it is to save you
the days of searching that should not be necessary just to open a window
and draw a pixel. This is the guide that would have been useful
as I started developing the visualizer for A-MAZE-ING: enough to get
unstuck, not enough to skip the discovery. The progressive
understanding of how MLX works, and the moment where everything
falls into place, is yours to experience.

MLX has more to offer than what is covered here. Bitmap fonts,
sprites, elaborate UI and other techniques are left for you to find.
This guide serves as a bridge, from completely lost to having
a solid foundation you can build your own project on.

## Installation

| Platform | Status |
| -------- | ------ |
| **Linux AMD64** | 🟢 Fully supported - tested on Ubuntu 22.04 AMD64 |
| **Mac Silicon** | 🟢 Working via Docker `--platform linux/amd64` - tested on Ventura 13.4 (Mac Studio M2) |
| **Mac Intel** | 🟡 Should work - not tested |
| **Windows** | 🟡 WSL2 with WSLg may work - not tested |

**1. Install Python and pip**

Skip if already installed (`python3 --version` to check).
```bash
apt-get update && apt-get install -y python3 python3-pip
```

**2. Install X11 dependencies**
```bash
apt-get install -y libx11-dev libxext-dev libxcb-keysyms1
```

**3. Install MLX wheel**

From the root of the cloned repository:
```bash
pip3 install 00_install/mlx-2.2-py3-none-any.whl
```

**4. Verify**
```bash
python3 01.modules/M01_init.py
```

A window should open. Press ESC or click the X button to close it.


## Modules

| File                  | Topic                                              |
| --------------------- | -------------------------------------------------- |
| M01 - init            | MLX init, window creation, clean shutdown          |
| M02 - image buffer    | Image buffer, `write_pixel()`, `write_rect()`      |
| M03 - tile grid       | Tile coordinates, inset tiles, wall bitmasks       |
| M04 - draw order      | Draw order, compositor pattern, UI split           |
| M05 - text            | `mlx_string_put()`, color conversion, draw order   |
| M06 - interactive     | Input handling, game loop, deferred pattern        |


## Common Errors

| File                  | Error                                              |
| --------------------- | -------------------------------------------------- |
| E01 - bounds          | `write_rect()` overflow - silent corruption vs crash |
| E02 - no loop         | Missing `mlx_loop()` - window closes immediately   |
| E03 - mask key press  | Wrong mask on key hook - keys never fire           |
| E04 - x button        | Missing close handler - X button has no effect     |
| E05 - sync loop       | `mlx_loop()` is single-threaded and synchronous    |
| E06 - text overwrite  | `mlx_string_put()` erased by `mlx_put_image_to_window()` |
| E07 - str color       | `mlx_string_put()` expects 0xBBGGRR not 0xRRGGBB  |

## Diagnostics

| File                  | Topic                                              |
| --------------------- | -------------------------------------------------- |
| D01 - memory leak     | `mlx_new_image()` without `mlx_destroy_image()`   |
| D02 - frame rate      | Measuring effective FPS via `mlx_loop_hook()`     |
| D03 - key repeat      | X11/XQuartz key autorepeat behavior               |

## Broken MLX Functions

| File                  | Topic                                              |
| --------------------- | -------------------------------------------------- |
| B01 - pixel put 01    | `mlx_pixel_put()` called before `mlx_loop()` - black |
| B01 - pixel put 02    | `mlx_pixel_put()` called from key handler - black  |
| B01 - pixel put 03    | `mlx_pixel_put()` with explicit flush - black      |

## Conventions

### Tile coordinates

Tile indices are always converted to pixel positions via:
```python
def tile_px(tile_col): return (tile_col + BORDER) * TILE_SIZE
def tile_py(tile_row): return (tile_row + BORDER) * TILE_SIZE
```

### Inset tiles

`draw_tile()` fills only the interior of a tile, leaving `WALL_SIZE`
pixels on each edge as a gap. Without this, two adjacent same-color
tiles bleed into a solid block with no visible separation at open
passages.

### Wall rendering

All modules use the 4-walls-per-cell approach: each cell owns and
draws all 4 of its wall strips, trimmed at both ends by `WALL_SIZE`
to avoid corner overlap. This leaves a `WALL_SIZE x WALL_SIZE`
junction gap at every corner - almost invisible at `WALL_SIZE = 1`,
visible at `WALL_SIZE = 2+`.

A cleaner alternative (west + north walls only) is documented in
M03 but not used in the guide.

### Draw order

MLX has no real layers - just one flat pixel buffer. The last
`write_rect()` call to touch a pixel wins. The correct draw stack:
```
1. Background fill + floor tiles
2. Pattern tiles
3. Path tiles
4. Entry / exit tiles  - must come after path
5. Walls               - conventional, not required with inset tiles
6. UI background
7. UI content
```

## Color Constants

All constants use `0xRRGGBB` with a `C_` prefix. `write_rect()`
handles the BGR conversion internally.

| Constant        | Role                            |
| --------------- | ------------------------------- |
| C_BG            | Full-window background fill     |
| C_FLOOR         | Default tile interior           |
| C_WALL          | Wall strip color                |
| C_ENTRY         | Entry tile                      |
| C_EXIT          | Exit tile                       |
| C_PATH          | Solution path tile              |
| C_PATTERN       | Decorative highlight tile       |
| C_UI_BG         | UI panel background             |
| C_UI_ACTIVE     | UI panel highlighted element    |
| C_UI_INACTIVE   | UI panel default element        |

## Wall Bitmask Format

Used in M03 onwards to encode which walls are present on a cell:
```
bit 3 (0b1000) = West
bit 2 (0b0100) = South
bit 1 (0b0010) = East
bit 0 (0b0001) = North
```

Example: `0b1010` = West + East walls (horizontal corridor).
Extracting a bit: `(bitmask >> bit_position) & 1`

## Keyboard Events

| Event                | X11/XQuartz number | mlx_hook mask |
| -------------------- | ------------------ | ------------- |
| EVENT_KEY_PRESS      | 2                  | 1             |
| EVENT_KEY_RELEASE    | 3                  | 2             |
| EVENT_WINDOW_CLOSE   | 33                 | 0             |

### Deferred pattern

Key handlers run synchronously inside `mlx_loop()` - there is no
parallelism. While a handler executes, the loop is paused and no
redraws happen. The deferred pattern lets you render visual feedback
before work runs on the next frame:
```python
# In key_press_handler:
pending_action = True
render_scene()     # feedback visible NOW, before work runs

# In game_loop - one frame later:
if pending_action:
    pending_action = False
    do_work()
    render_scene()
```

The freeze still happens - the pattern ensures feedback appears
before it. See M06 and E05 for full demonstrations.

## Thanks

**amaazouz** — for his curiosity about MLX and A-MAZE-ING, which
pushed me to document what I'd learned.

**dloic** — for his completely different approach to wall rendering
that made me think harder about my own, and for being just as
frustrated by the lack of MLX documentation - which is part of
why this guide exists.

**tdhenain** — for his partnership throughout A-MAZE-ING.

**cgazen** and **kprist** — for discovering the close window fix
that saved everyone.

**gwfranco** — for his terminal-based take on A-MAZE-ING.

**gdupret** - for his last-minute tips that always arrive
exactly when they are needed.

**mhummels**, **syalcin** and **aouassar** — for their feedback on A-MAZE-ING.

Also thanks to **mhummels**, **gdupret**, **gwfranco**, **cgazen**,
**kprist**, and **dloic** for sharing their A-MAZE-ING — seeing
different approaches to the same project was invaluable.
