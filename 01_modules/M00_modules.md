## MLX Guide - Modules

Six modules, each introducing one new layer of MLX concepts.
Every module builds on the previous one and uses A-MAZE-ING
as the reference project throughout.

---

## M01 - INIT

<!-- MLX initialization, window creation, clean shutdown -->

A window that opens, stays open, and closes properly - either by
pressing ESC or clicking the X button. The absolute foundation.
Every MLX program starts here.

**Concepts:**
- The MLX object and what `mlx_init()` actually does
- Creating a window with `mlx_new_window()`
- Hooking keyboard events with `mlx_hook()`
- Closing the window with `mlx_loop_exit()`
- The X button: event 33, works on both Linux and Mac
- `mlx_loop()`: the blocking call that hands control to MLX

---

## M02 - IMAGE BUFFER

<!-- Pixel buffer system and drawing workflow -->

A window filled with colored rectangles, drawn by writing directly
into a raw memory buffer and pushing it to screen all at once.

**Concepts:**
- Why you should NEVER draw directly to the window
- `mlx_new_image()` and `mlx_get_data_addr()`
- What `img_addr` actually is (raw writable byte buffer)
- `img_size_line`: row stride from `mlx_get_data_addr`
- Pixel format: BGR + alpha, 4 bytes per pixel
- `write_pixel()`: fundamental drawing primitive
- `write_rect()`: fast rectangle fill using row slice assignment
- `mlx_put_image_to_window()`: pushing buffer to screen

---

## M03 - TILE GRID & WALLS

<!-- Coordinates, inset tiles, wall bitmasks -->

A grid of colored tiles with inset walls between them - the exact
visual structure used to render a maze. By the end of this module
you will understand how any cell-based grid game is drawn with MLX.

**Concepts:**
- Tile coordinates vs pixel coordinates
- `tile_px()` / `tile_py()`: converting tile index to pixel position
- `draw_tile()`: filling interior of a tile (respecting wall inset)
- Drawing individual walls (north, south, east, west) as thin strips
- Wall bitmask encoding: how one integer describes all 4 walls
- Walls drawn after tiles: conventional with inset tiles, not required

**Wall bitmask format:**
```
bit 3 (0b1000) = West
bit 2 (0b0100) = South
bit 1 (0b0010) = East
bit 0 (0b0001) = North
Example: 0b1010 = West + East walls present
```

---

## M04 - DRAW ORDER & LAYERS

<!-- Compositor pattern, flat pixel buffer, UI split -->

A static multi-element scene (background, grid, path, overlay, UI panel)
drawn once in correct order using the compositor pattern.

**Concepts:**
- There are NO real layers in MLX - just one flat pixel buffer
- "Layering" = draw order: last draw wins
- The compositor pattern: one named function per conceptual layer
- Separating maze area from UI panel (two x-regions)

**Draw stack (bottom to top):**
```
1. floor fill         - background + all tile interiors
2. pattern tiles      - special cells drawn over floor
3. path               - solution path drawn over pattern
4. entry / exit tiles - drawn AFTER path, always visible
5. walls              - drawn after tiles (conventional)
6. UI background      - fills the right panel
7. UI content         - drawn over panel background
```

---

## M05 - TEXT

<!-- mlx_string_put, color conversion, draw order -->

A palette viewer - each color constant from `config.py` rendered as
a colored rectangle paired with a text label. Demonstrates both
`mlx_string_put` and the color conversion it requires.

**Concepts:**
- `mlx_string_put` bypasses the image buffer and draws straight to window -
  each call is a synchronous X11/XQuartz roundtrip, slow enough that
  drawing a dozen labels renders visibly top to bottom
- Text is always drawn on top of the last `mlx_put_image_to_window` call
- No control over font family, size, or weight - X11/XQuartz fixed font only
- Unicode characters do not render - ASCII only
- Color is the only customizable property
- `mlx_string_put` expects `0xBBGGRR`, not `0xRRGGBB` - see `str_color()`
- `render()` must always come BEFORE `mlx_string_put`, never after

---

## M06 - INTERACTIVE

<!-- Input handling, game loop, deferred pattern -->

The M04 maze scene, now interactive. Arrow keys move a player through
the maze with wall collision. SPACE triggers a regenerate action that
demonstrates the deferred pattern in practice.

**Concepts:**
- Event 2 = KeyPress, Event 3 = KeyRelease
- `mlx_loop` is single-threaded - handlers block everything while running
- Wall collision using bitmask from M03
- Key release: when you need it and when you don't
- Flash timers: visual feedback with timed expiry
- `mlx_do_key_autorepeatoff`: why X11/XQuartz key repeat causes artifacts

**The deferred pattern in detail:**
`mlx_hook` callbacks run synchronously inside `mlx_loop`. Setting a flag
in the handler and doing work in `game_loop` lets you call `render_scene()`
before the work runs - so visual feedback appears on screen first.
The freeze still happens, but visual feedback appears before it.

---
