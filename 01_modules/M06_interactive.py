# =============================================================================
# M06 - INTERACTIVE: input handling, game loop, deferred pattern
# =============================================================================
#
# CONCEPTS:
#   - Event 2 = KeyPress, Event 3 = KeyRelease
#   - mlx_loop is single-threaded - handlers block everything while running
#   - Wall collision using bitmask from M03
#   - Key release: when you need it and when you don't
#   - Flash timers: visual feedback with timed expiry
#   - mlx_do_key_autorepeatoff: why X11/XQuartz key repeat causes artifacts
#
#   The deferred pattern in detail:
#     mlx_hook callbacks run synchronously inside mlx_loop. Setting a flag
#     in the handler and doing work in game_loop lets you call render_scene()
#     before the work runs - so visual feedback appears on screen first.
#     The freeze still happens, but visual feedback appears before it.
#
# WHAT WE ARE BUILDING:
#   The M04 maze scene, now interactive. Arrow keys move a player through
#   the maze with wall collision. SPACE triggers a regenerate action that
#   demonstrates the deferred pattern in practice.
#
# CONTROLS:
#   Arrow keys: move player
#   SPACE:      regenerate maze
#   ESC:        quit
#
# =============================================================================

import mlx   # type: ignore
from pathlib import Path
import time
from config import (  # type: ignore
    EVENT_KEY_PRESS, EVENT_KEY_RELEASE, EVENT_WINDOW_CLOSE,
    MASK_KEY_PRESS, MASK_KEY_RELEASE, MASK_NONE,
    KEY_ESC, KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN,
    KEY_SPACE,
    C_WHITE, C_BG, C_FLOOR, C_WALL, C_ENTRY, C_EXIT,
    C_PATH, C_PATTERN, C_PLAYER, C_UI_BG, C_UI_ACTIVE, C_UI_INACTIVE,
)

TITLE = Path(__file__).stem

# =============================================================================
# CONFIG
# =============================================================================

TILE_SIZE = 80  # pixels per tile (interior + wall strips)
WALL_SIZE = 1   # wall strip thickness in pixels
GRID_COLS = 8   # number of tile columns
GRID_ROWS = 8   # number of tile rows
BORDER = 1      # margin tiles around the grid
UI_W = 300      # width of the UI panel in pixels
UI_BTN_H = 40   # button height in pixels
UI_BTN_W = 200  # button width in pixels
FLASH_DURATION = 0.15    # seconds a button stays highlighted after a keypress
MAZE_W = (GRID_COLS + 2 * BORDER) * TILE_SIZE  # maze area width in pixels
WIN_H = (GRID_ROWS + 2 * BORDER) * TILE_SIZE   # window height in pixels
WIN_W = MAZE_W + UI_W                          # window width in pixels

# =============================================================================
# INIT
# =============================================================================

m = mlx.Mlx()
mlx_ptr = m.mlx_init()
win_ptr = m.mlx_new_window(mlx_ptr, WIN_W, WIN_H, TITLE)
img_ptr = m.mlx_new_image(mlx_ptr, WIN_W, WIN_H)
img_addr, _, img_size_line, _ = m.mlx_get_data_addr(img_ptr)

# =============================================================================
# DRAWING PRIMITIVES
# =============================================================================

def write_pixel(x: int, y: int, color: int) -> None:
    """Write one pixel at (x, y) in BGR order. Skips out-of-bounds coords."""
    if not (0 <= x < WIN_W and 0 <= y < WIN_H):
        return

    byte_index = y * img_size_line + x * 4
    img_addr[byte_index] = color & 0xFF
    img_addr[byte_index + 1] = (color >> 8) & 0xFF
    img_addr[byte_index + 2] = (color >> 16) & 0xFF
    img_addr[byte_index + 3] = 0xFF

def write_rect(x: int, y: int, w: int, h: int, color: int) -> None:
    """Fill a rectangle using fast row slice assignment."""
    blue = color & 0xFF
    green = (color >> 8) & 0xFF
    red = (color >> 16) & 0xFF
    row = bytearray([blue, green, red, 0xFF] * w)

    for row_offset in range(h):
        start = (y + row_offset) * img_size_line + x * 4
        end = start + len(row)
        img_addr[start:end] = row

def render() -> None:
    """Push image buffer to window."""
    m.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 0, 0)

def str_color(color: int) -> int:
    """Convert 0xRRGGBB to 0xBBGGRR for mlx_string_put."""
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    return (b << 16) | (g << 8) | r

# =============================================================================
# TILE COORDINATES
# =============================================================================

def tile_px(tile_col: int) -> int:
    """Convert tile column index to pixel x (top-left corner of tile)."""
    return (tile_col + BORDER) * TILE_SIZE

def tile_py(tile_row: int) -> int:
    """Convert tile row index to pixel y (top-left corner of tile)."""
    return (tile_row + BORDER) * TILE_SIZE

# =============================================================================
# TILE DRAWING
# =============================================================================

def draw_tile(tile_col: int, tile_row: int, color: int) -> None:
    """Fill interior of a tile, inset by WALL_SIZE on all sides."""
    inset = WALL_SIZE
    interior_size = TILE_SIZE - 2 * inset
    write_rect(tile_px(tile_col) + inset, tile_py(tile_row) + inset,
               interior_size, interior_size, color)

# =============================================================================
# WALL DRAWING
# =============================================================================

def draw_wall_north(tile_col: int, tile_row: int) -> None:
    write_rect(tile_px(tile_col) + WALL_SIZE, tile_py(tile_row),
               TILE_SIZE - 2 * WALL_SIZE, WALL_SIZE, C_WALL)

def draw_wall_south(tile_col: int, tile_row: int) -> None:
    write_rect(tile_px(tile_col) + WALL_SIZE,
               tile_py(tile_row) + TILE_SIZE - WALL_SIZE,
               TILE_SIZE - 2 * WALL_SIZE, WALL_SIZE, C_WALL)

def draw_wall_west(tile_col: int, tile_row: int) -> None:
    write_rect(tile_px(tile_col), tile_py(tile_row) + WALL_SIZE,
               WALL_SIZE, TILE_SIZE - 2 * WALL_SIZE, C_WALL)

def draw_wall_east(tile_col: int, tile_row: int) -> None:
    write_rect(tile_px(tile_col) + TILE_SIZE - WALL_SIZE,
               tile_py(tile_row) + WALL_SIZE,
               WALL_SIZE, TILE_SIZE - 2 * WALL_SIZE, C_WALL)

def draw_tile_walls(tile_col: int, tile_row: int, bitmask: int) -> None:
    """Draw walls encoded in a 4-bit bitmask (from M03).
    bit 3 = West, bit 2 = South, bit 1 = East, bit 0 = North
    """
    if (bitmask >> 3) & 1:
        draw_wall_west(tile_col, tile_row)
    if (bitmask >> 2) & 1:
        draw_wall_south(tile_col, tile_row)
    if (bitmask >> 1) & 1:
        draw_wall_east(tile_col, tile_row)
    if (bitmask >> 0) & 1:
        draw_wall_north(tile_col, tile_row)

# =============================================================================
# SCENE DATA
# =============================================================================

MAZE_GRID = [
    #  col0    col1    col2    col3    col4    col5    col6    col7
    [0b1001, 0b0101, 0b0101, 0b0001, 0b0001, 0b0101, 0b0101, 0b0011],  # row 0
    [0b1010, 0b1001, 0b0011, 0b1010, 0b1010, 0b1001, 0b0011, 0b1010],  # row 1
    [0b1010, 0b1110, 0b1000, 0b0110, 0b1100, 0b0010, 0b1110, 0b1010],  # row 2
    [0b1100, 0b0101, 0b0010, 0b1111, 0b1111, 0b1000, 0b0101, 0b0110],  # row 3
    [0b1001, 0b0011, 0b1010, 0b1111, 0b1111, 0b1010, 0b1001, 0b0011],  # row 4
    [0b1010, 0b1010, 0b1100, 0b0011, 0b1001, 0b0110, 0b1010, 0b1010],  # row 5
    [0b1010, 0b1100, 0b0111, 0b1010, 0b1010, 0b1101, 0b0110, 0b1010],  # row 6
    [0b1100, 0b0101, 0b0101, 0b0100, 0b0100, 0b0101, 0b0101, 0b0110],  # row 7
]

ENTRY = (0, 0)  # maze entry tile (col, row)
EXIT = (7, 7)  # maze exit tile (col, row)
PATH = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (2, 3), (2, 4), (2, 5),
        (3, 5), (3, 6), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7)]
PATTERN = [(3, 3), (4, 3), (3, 4), (4, 4)]  # pattern tiles - none overlap PATH

# =============================================================================
# STATE
# =============================================================================

# Player position in tile coordinates (col, row).
# Starts at maze entry. Arrow keys move it one tile at a time,
# subject to wall collision checked against MAZE_GRID bitmasks.
player_col, player_row = ENTRY

# Pending flags: set in key_press_handler, consumed in game_loop.
# Core of the deferred pattern - never do work directly in a handler.
pending_regen = False

# Flash timestamp: records when regen button was last pressed.
# game_loop checks every frame whether FLASH_DURATION has elapsed.
# None = not currently flashing.
flash_regen: float | None = None

# =============================================================================
# WALL COLLISION
# =============================================================================

def in_bounds(col: int, row: int) -> bool:
    """Return True if (col, row) is a valid tile position inside the grid.
    Called before draw_tile - an out-of-range index computes a pixel
    coordinate outside the image buffer and raises ValueError.
    """
    return 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS

def can_move(col: int, row: int, direction: str) -> bool:
    """Return True if player can step in direction from (col, row).
    Only checks wall bitmask - bounds are guaranteed by caller.
    Bitmask format from M03: bit 3 = West, bit 2 = South,
                             bit 1 = East, bit 0 = North
    """
    bitmask = MAZE_GRID[row][col]
    if direction == "north":
        return not ((bitmask >> 0) & 1)
    if direction == "south":
        return not ((bitmask >> 2) & 1)
    if direction == "east":
        return not ((bitmask >> 1) & 1)
    if direction == "west":
        return not ((bitmask >> 3) & 1)
    return False

# =============================================================================
# COMPOSITOR LAYERS
# =============================================================================

def draw_layer_floor() -> None:
    """Layer 1: Fill window background, then all maze tile interiors."""
    write_rect(0, 0, WIN_W, WIN_H, C_BG)
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            draw_tile(col, row, C_FLOOR)

def draw_layer_pattern() -> None:
    """Layer 2: Pattern tiles - decorative cells, drawn after floor."""
    for tile_col, tile_row in PATTERN:
        draw_tile(tile_col, tile_row, C_PATTERN)

def draw_layer_path() -> None:
    """Layer 3: Solution path, drawn after pattern tiles."""
    for tile_col, tile_row in PATH:
        draw_tile(tile_col, tile_row, C_PATH)

def draw_layer_overlay() -> None:
    """Layer 4 + 5: Entry, exit, and all walls."""
    draw_tile(*ENTRY, C_ENTRY)
    draw_tile(*EXIT,  C_EXIT)
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            draw_tile_walls(col, row, MAZE_GRID[row][col])

def draw_layer_player() -> None:
    """Layer 6: Player tile - drawn last in maze area, always on top."""
    draw_tile(player_col, player_row, C_PLAYER)

def draw_layer_ui() -> None:
    """Layer 7: UI panel background and regen button."""
    ui_center_x = MAZE_W + UI_W // 2
    btn_y = WIN_H // 2
    btn_color = C_UI_ACTIVE if flash_regen else C_UI_INACTIVE

    write_rect(MAZE_W, 0, UI_W, WIN_H, C_UI_BG)
    write_rect(ui_center_x - UI_BTN_W // 2, btn_y,
               UI_BTN_W, UI_BTN_H, btn_color)

def draw_ui_labels() -> None:
    """Draw UI text labels on top of the image buffer.
    Must be called AFTER render() - mlx_string_put draws directly
    to the window and is overwritten if render() is called again.
    """
    ui_center_x = MAZE_W + UI_W // 2
    btn_y = WIN_H // 2
    label_x = ui_center_x - UI_BTN_W // 2

    m.mlx_string_put(mlx_ptr, win_ptr, label_x, btn_y - 110,
                     str_color(C_UI_INACTIVE), "ARROWS")
    m.mlx_string_put(mlx_ptr, win_ptr, label_x, btn_y - 110,
                     str_color(C_WHITE), "                Move")
    m.mlx_string_put(mlx_ptr, win_ptr, label_x, btn_y - 80,
                     str_color(C_UI_INACTIVE), "SPACE")
    m.mlx_string_put(mlx_ptr, win_ptr, label_x, btn_y - 80,
                     str_color(C_WHITE), "          Regenerate")
    m.mlx_string_put(mlx_ptr, win_ptr, label_x, btn_y - 50,
                     str_color(C_UI_INACTIVE), "ESC")
    m.mlx_string_put(mlx_ptr, win_ptr, label_x, btn_y - 50,
                     str_color(C_WHITE), "                Quit")

# =============================================================================
# SCENE RENDER
# =============================================================================

def render_scene() -> None:
    """Draw entire scene in layer order, render, then draw text labels."""
    draw_layer_floor()
    draw_layer_pattern()
    draw_layer_path()
    draw_layer_overlay()
    draw_layer_player()
    draw_layer_ui()
    render()
    draw_ui_labels()

# =============================================================================
# ACTIONS
# =============================================================================

def do_regen() -> None:
    """Simulate maze regeneration - 300ms of blocking work.
    Here it just sleeps to demonstrate timing without complexity.
    Because this runs in game_loop, the UI highlight from flash_regen
    is already visible on screen before this blocks.
    """
    time.sleep(0.3)
    global player_col, player_row
    player_col, player_row = ENTRY

# =============================================================================
# HOOKS
# =============================================================================

def key_press_handler(keycode: int, param) -> int:
    """Handle key press events (event 2).
    Arrow keys: check wall collision, move player, redraw.
    SPACE: set pending flag, set flash timer, render feedback, return.
    Work runs on the next game_loop tick.
    """
    global player_col, player_row, pending_regen, flash_regen

    if keycode == KEY_ESC:
        m.mlx_loop_exit(mlx_ptr)
        return 0

    if (keycode == KEY_UP and in_bounds(player_col, player_row - 1)
       and can_move(player_col, player_row, "north")):
        player_row -= 1
        render_scene()
    if (keycode == KEY_DOWN and in_bounds(player_col, player_row + 1)
       and can_move(player_col, player_row, "south")):
        player_row += 1
        render_scene()
    if (keycode == KEY_RIGHT and in_bounds(player_col + 1, player_row)
       and can_move(player_col, player_row, "east")):
        player_col += 1
        render_scene()
    if (keycode == KEY_LEFT and in_bounds(player_col - 1, player_row)
       and can_move(player_col, player_row, "west")):
        player_col -= 1
        render_scene()

    if keycode == KEY_SPACE:
        pending_regen = True
        flash_regen = time.time()
        render_scene()

    return 0

def key_release_handler(keycode: int, param) -> int:
    """Handle key release events (event 3).
    Fires when a key is released - use it for continuous movement,
    held-key animations, or UI button release.
    Registered but does nothing here - see WHAT TO TRY NEXT.
    """
    return 0

def close_handler(param) -> int:
    m.mlx_loop_exit(mlx_ptr)
    return 0

m.mlx_hook(win_ptr, EVENT_KEY_PRESS, MASK_KEY_PRESS,
           key_press_handler, None)
m.mlx_hook(win_ptr, EVENT_KEY_RELEASE, MASK_KEY_RELEASE,
           key_release_handler, None)
m.mlx_hook(win_ptr, EVENT_WINDOW_CLOSE, MASK_NONE,
           close_handler, None)

# =============================================================================
# GAME LOOP
# =============================================================================

def game_loop(param) -> int:
    """Fires every frame for the lifetime of the loop.
    Signature: mlx_loop_hook(mlx_ptr, func, param) -> None
    This is where deferred work actually runs. Flags set in key handlers
    are consumed here, one per frame, keeping handlers fast.
    Sequence for SPACE:
      Frame N:   key pressed - pending_regen set, highlight shown, returns
      Frame N+1: game_loop sees pending_regen - do_regen() runs - redraw
      Frame N+2: flash timer expires - highlight removed - redraw
    """
    global pending_regen, flash_regen

    if pending_regen:
        pending_regen = False
        do_regen()
        render_scene()

    if flash_regen is not None and time.time() - flash_regen > FLASH_DURATION:
        flash_regen = None
        render_scene()

    return 0

render_scene()
m.mlx_loop_hook(mlx_ptr, game_loop, None)

# =============================================================================
# LOOP
# =============================================================================

m.mlx_loop(mlx_ptr)

# =============================================================================
# CLEANUP
# =============================================================================

m.mlx_destroy_image(mlx_ptr, img_ptr)
m.mlx_destroy_window(mlx_ptr, win_ptr)
m.mlx_release(mlx_ptr)

# =============================================================================
# WHAT TO TRY NEXT:
#   - Replace can_move(...) with True in key_press_handler - player walks
#     through walls, but walls are still drawn. in_bounds() still holds.
#   - Move do_regen() directly into key_press_handler - feel 300ms freeze
#     and notice button highlight never appears before the freeze
#   - Add a second pending flag for a different action (e.g. toggle path)
#     and observe that both flags are independent and can fire in same frame
#   - Use key_release_handler to detect when player reaches EXIT and
#     releases last arrow key - trigger a "solved" state at that moment
#   - In game_loop, auto-walk the player along PATH one step at a time using
#     time.time() to control the interval between steps
# =============================================================================
